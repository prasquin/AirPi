#!/usr/bin/python3

""" Read low-level data from HTU21D sensor.

A low-level Class to read data directly from the HTU21D sensor,
which provides temperature and humidity readings.

"""

import struct, array, time, io, fcntl

CMD_READ_TEMP_HOLD = b"\xE3"
CMD_READ_HUM_HOLD = b"\xE5"
CMD_READ_TEMP_NOHOLD = b"\xF3"
CMD_READ_HUM_NOHOLD = b"\xF5"
CMD_WRITE_USER_REG = b"\xE6"
CMD_READ_USER_REG = b"\xE7"
CMD_SOFT_RESET= b"\xFE"
I2C_SLAVE=0x0703

class i2c(object):
    def __init__(self, device, bus):
        self.fr = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
        self.fw = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)
        fcntl.ioctl(self.fr, I2C_SLAVE, device)
        fcntl.ioctl(self.fw, I2C_SLAVE, device)

    def write(self, bytes):
        return self.fw.write(bytes)

    def read(self, bytes):
        return self.fr.read(bytes)

    def close(self):
        self.fw.close()
        self.fr.close()

class HTU21D:
    def __init__(self, HTU21D_ADDR=0x40, bus=1, debug=False): #HTU21D 0x40, bus 1
        self.debug = debug
        self.dev = i2c(HTU21D_ADDR, bus)
        self.dev.write(CMD_SOFT_RESET)
        time.sleep(.015)

    def ctemp(self, sensorTemp):
        tSensorTemp = sensorTemp / 65536.0
        return -46.85 + (175.72 * tSensorTemp)

    def chumid(self, sensorHumi):
        tSensorHumi = sensorHumi / 65536.0
        return -6.0 + (125.0 * tSensorHumi)

    def crccheck(self, value):
        remainder = (((value[0] << 8) + value[1]) << 8) | value[2]
        divisor = 0x988000
        for i in range(0, 16):
            if (remainder & 1 << (23 - i)):
                remainder ^= divisor
            divisor = divisor >> 1
        if remainder == 0:
            return True
        else:
            return False
    
    def readTemperature(self):
        self.dev.write(CMD_READ_TEMP_NOHOLD)
        time.sleep(.05)
        data = self.dev.read(3)
        buf = array.array('B', data)
        if self.crccheck(buf):
            temp = (buf[0] << 8 | buf [1]) & 0xFFFC
            return self.ctemp(temp)
        else:
            return False
            
    def readHumidity(self):
        self.dev.write(CMD_READ_HUM_NOHOLD)
        time.sleep(.016)
        data = self.dev.read(3)
        buf = array.array('B', data)
        if self.crccheck(buf):
            humid = (buf[0] << 8 | buf [1]) & 0xFFFC
            return self.chumid(humid)
        else:
            return False
            
if __name__ == "__main__":
    obj = HTU21D()
    print("Temp: %s C" % round(obj.readTemperature(),2))
    print("Humid: %s %% rH" % round(obj.readHumidity(),2))
