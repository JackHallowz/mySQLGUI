import serial

serialport = serial.Serial('COM7', baudrate=115200, timeout=1)

textfile = open('DataSave.txt', 'w')

