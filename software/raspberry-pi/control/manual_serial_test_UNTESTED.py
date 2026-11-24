#!/usr/bin/env python3
"""Experimental, NOT YET validated on RPOD Pi->Nano USB link.

Only sends F/L/R/S one-shot commands to a Nano running the short motor_test.ino
protocol. Keep wheels raised during first validation and verify Nano pinout,
shared grounds, and regulated 5V wiring before starting motors.
Requires Python pyserial: sudo apt install python3-serial
"""
import time
import serial
from serial.tools import list_ports


def main():
    ports = [p.device for p in list_ports.comports()
             if p.device.startswith(('/dev/ttyUSB', '/dev/ttyACM'))]
    if len(ports) != 1:
        raise SystemExit('Expected one Nano serial device; found: ' + repr(ports))
    with serial.Serial(ports[0], baudrate=115200, timeout=1) as nano:
        time.sleep(2.0)  # Nano may reset when USB serial is opened
        print('RPOD serial test. F forward, L left, R right, S stop, Q quit')
        while True:
            try:
                cmd = input('Command > ').strip().upper()
            except (KeyboardInterrupt, EOFError):
                cmd = 'Q'
            if cmd == 'Q':
                nano.write(b'S')
                nano.flush()
                break
            if cmd not in ('F', 'L', 'R', 'S'):
                print('Use F, L, R, S, or Q')
                continue
            nano.write(cmd.encode('ascii'))
            nano.flush()
            print('Sent', cmd, '(requires short one-shot Arduino test firmware)')


if __name__ == '__main__':
    main()
