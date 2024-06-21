# EZO pH Circuit Driver for Micropython

IMPORTANT: This is not an official/affiliated driver (at the time of writing this, I do not believe there is one).

Circuit: https://atlas-scientific.com/embedded-solutions/ezo-ph-circuit/

This Micropython driver provides an interface to interact with the EZO pH sensor via I2C communication. The driver allows you to take pH readings, set temperature compensation, and change the I2C address of the sensor. Note that not all features of the EZO pH sensor are implemented in this driver.

## Features

- Initialize the EZO pH sensor with specified I2C parameters.
- Take pH readings.
- Set and get temperature compensation for accurate pH readings.
- Change the I2C address of the sensor.
- Find the sensor by flashing its LED.

## Installation

You can install usniffs from the REPL with mip.

```python
# micropython REPL
import mip
mip.install("github:surdouski/micropython-EZO-pH")
```

Alternatively, you can install it by using mpremote if you don't have network connectivity on device.

```
$ mpremote mip install github:surdouski/micropython-EZO-pH
```

## Usage

```python
import asyncio
from machine import Pin
from ezo_ph import EzoPh

async def main():
    # Initialize the I2C and the EzoPh sensor
    i2c_index = 0
    scl = Pin(13)
    sda = Pin(12)
    sensor = EzoPh(i2c_index, scl, sda)

    # Find sensor (flashes LED)
    await sensor.find(5)  # flashes for 5 seconds
    
    # Change I2C address
    new_address = 0x64
    await sensor.change_i2c_address(new_address)  # update and restart chip with new i2c address
    
    # Set temperature compensation
    await sensor.set_temperature_compensation(26.0)
    
    # Get current temperature compensation
    temp_comp = await sensor.get_temperature_compensation()
    print(f"Temperature Compensation: {temp_comp}")
    
    # Take a pH reading
    ph_value = await sensor.take_reading()
    print(f"pH Value: {ph_value}")

asyncio.run(main())
```

## Class and Methods

### EzoPh

A class to interact with the EZO pH sensor using I2C communication.

#### Initialization

```python
def __init__(self, i2c_index: int, scl: Pin, sda: Pin, clock_speed: int = 400000, address: hex = 0x63)
```

Initialize the EzoPh sensor with given I2C parameters.

- `i2c_index (int)`: Index for I2C instance.
- `scl (Pin)`: Pin used for I2C clock.
- `sda (Pin)`: Pin used for I2C data.
- `clock_speed (int)`: Clock speed for I2C communication. Default is 400kHz.
- `address (hex)`: I2C address of the EZO pH sensor. Default is 0x63.

#### Methods

##### `async find(blink_time_s: int = 5) -> None`

Flashes the device LED for the specified number of seconds.

##### `async take_reading() -> float`

Takes a pH reading and returns the value as a float.

##### `async set_temperature_compensation(temp: float | int) -> None`

Sets the temperature for compensation to get more accurate pH readings.

- `temp (float | int)`: Temperature value to set for compensation.

##### `async get_temperature_compensation() -> float`

Returns the current compensated temperature value set on the peripheral.

##### `async change_i2c_address(new_address: hex) -> None`

Changes the I2C address of the pH-EZO sensor.

- `new_address (hex)`: The new I2C address to set for the device.

## Limitations

This driver does not cover all features available on the EZO pH sensor chip. Please refer to the sensor's datasheet for complete functionality.

## License

This project is licensed under the MIT License. See the LICENSE file for details.