import asyncio
from machine import Pin, I2C


# response codes
NO_DATA_TO_SEND = 0xFF
STILL_PROCESSING = 0xFE
SYNTAX_ERROR = 0x02
SUCCESSFUL_REQUEST = 0x01  # also START_MARKER
END_MARKER = 0x00


class EzoPhWriteException(Exception):
    ...


def with_instance_lock(func):
    async def wrapper(self, *args, **kwargs):
        await self.lock.acquire()
        try:
            return await func(self, *args, **kwargs)
        finally:
            self.lock.release()
    return wrapper


class EzoPh:
    """
    Class to interact with the EZO pH sensor using I2C communication.

    Attributes:
        _i2c (I2C): I2C communication instance.
        _address (hex): I2C address of the EZO pH sensor.
        lock (asyncio.Lock): Lock for instance-specific operations.
    """
    def __init__(self, i2c_index: int, scl: Pin, sda: Pin, clock_speed: int = 400000, address: hex = 0x63):
        """
        Initialize the EzoPh sensor with given I2C parameters.

        Args:
            i2c_index (int): Index for I2C instance.
            scl (Pin): Pin used for I2C clock.
            sda (Pin): Pin used for I2C data.
            clock_speed (int): Clock speed for I2C communication.
            address (hex): I2C address of the EZO pH sensor.
        """
        self._i2c = I2C(
            i2c_index,
            scl=scl,
            sda=sda,
            freq=clock_speed,
        )
        self._address = address  # datasheet says default is 99 (0x63)
        self.lock = asyncio.Lock()

    @with_instance_lock
    async def find(self, blink_time_s: int = 5) -> None:
        """Flashes the device LED for n seconds before resuming continuous mode operation."""
        self._i2c.writeto(self._address, bytes("Find", "ascii"))
        await asyncio.sleep(blink_time_s)

        self._i2c.writeto(self._address, bytes("123", "ascii"))

    @with_instance_lock
    async def take_reading(self) -> float:
        """Take a ph reading and return the value as a float."""

        self._i2c.writeto(self._address, bytes("R", "ascii"))
        await asyncio.sleep_ms(900)  # read should take 900ms according to datasheet

        response = await self._read()  # example response: 9.560
        ph_reading = float(response)
        return ph_reading

    @with_instance_lock
    async def set_temperature_compensation(self, temp: float | int) -> None:
        """
        Set the temperature to get a more accurate (compensated for) pH reading.

        Note: The temperature is reset on device reset, needs to be set every time it is turned back on.

        Args:
            temp (float | int): Temperature value to set for compensation.
        """
        self._i2c.writeto(self._address, bytes(f"T,{temp}", "ascii"))
        await asyncio.sleep_ms(300)

    @with_instance_lock
    async def get_temperature_compensation(self) -> float:
        """
        Returns the current compensated temperature value set on the peripheral.

        Default is [25.0].

        Returns:
            float: The compensated temperature value.
        """
        self._i2c.writeto(self._address, bytes("T,?", "ascii"))
        await asyncio.sleep_ms(300)

        response = await self._read()  # example response: ?T,19.5
        temp_compensation = float(response.strip("?T,"))
        return temp_compensation

    @with_instance_lock
    async def change_i2c_address(self, new_address: hex) -> None:
        """
        Updates the pH-EZO's I2C address, which reboots the device (there is no response code).

        Args:
            new_address (hex): The new I2C address to set for the device.
        """
        self._i2c.writeto(self._address, bytes(f"I2C,{new_address}", "ascii"))
        self._address = new_address
        await asyncio.sleep(2)  # wait for restart

    async def _read(self) -> str:
        """
        Read data from the I2C device and return it as a string.

        Returns:
            str: The data read from the device.
        """
        response = self._i2c.readfrom(self._address, 16)  # read more bytes than we expect

        if response[0] == STILL_PROCESSING:
            await asyncio.sleep_ms(900)  # wait another 900ms instead of failing right away

        if response[0] == NO_DATA_TO_SEND or response[0] == SYNTAX_ERROR or response[0] == STILL_PROCESSING:
            return ""  # sadness

        buffer = []
        for byte in response[1:]:
            if byte == 0x00:
                break
            buffer.append(byte)
        return bytes(buffer).decode("ascii")

