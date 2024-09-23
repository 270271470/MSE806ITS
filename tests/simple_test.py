"""
File name:      simple_test.py
Author:         Mauritz Koekemoer
Created:        22-09-2024
Version:        1.0
Description:    This script scans all nearby BT devices
Additional:     Because we are interacting with hardware, elevated privileges (sudo) is required. Run with command below:
Command:        sudo /home/mauzer(or hasitha or prasad)/beacon-project/venv/bin/python3 simple_test.py
"""

# import libraries
from bluepy.btle import Scanner, DefaultDelegate

# class to scan & handle detection of all BT devices
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        print(f"Detected Device: {dev.addr} (RSSI: {dev.rssi})")
        for (adtype, desc, value) in dev.getScanData():
            print(f"  {desc}: {value}")

# instantiate scanner object
scanner = Scanner().withDelegate(ScanDelegate())
print("Scanning for BLE devices...")
devices = scanner.scan(10.0)  # Scans for 10 seconds
