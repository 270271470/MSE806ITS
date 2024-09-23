"""
File name:      scanner.py
Author:         Mauritz Koekemoer
Created:        20-09-2024
Version:        1.6
Description:    This script detects BLE beacons from mobile phones
Additional:     Because we are interacting with hardware, elevated privileges (sudo) is required. Run with command below:
Command:        sudo /home/mauzer(or hasitha or prasad)/beacon-project/venv/bin/python3 scanner.py
"""

# import libs needed
from bluepy.btle import Scanner, DefaultDelegate
import struct
import json
import os
from datetime import datetime

# load location mappings from resources directory (this will probably be replaced by a database or API query)
def load_locations(filename="locations.txt"):
    # Define the full path to the file in the /resources directory
    resources_path = os.path.join(os.path.dirname(__file__), "resources", filename)
    locations = {}
    with open(resources_path, 'r') as file:
        for line in file:
            bus_stop, coordinates = line.strip().split(':')
            locations[int(bus_stop)] = coordinates.strip()
    return locations

# save data to onboard.json in the /livedata directory (will be used for API and/or db interaction)
def save_onboard_data(userid, location, coordinates, filename="livedata/onboard.json"):
    directory = os.path.join(os.path.dirname(__file__), "livedata")
    filepath = os.path.join(directory, "onboard.json")
    
    # create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    timestamp = datetime.now().isoformat()  # to map the time a user was at a location
    entry = {
        "userid": userid,
        "location": f"Bus stop {location}",
        "coordinates": coordinates,
        "timestamp": timestamp
    }

    # read existing data, append new entry + save
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(entry)

    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

# class to scan for BLE and handle detection of advertised beacons
class ScanDelegate(DefaultDelegate):
    def __init__(self, locations):
        DefaultDelegate.__init__(self)
        self.locations = locations

    def handleDiscovery(self, dev, isNewDev, isNewData):
        for (adtype, desc, value) in dev.getScanData():
            if desc == "Manufacturer" and len(value) >= 48:
                try:
                    uuid = value[8:40]
                    major = struct.unpack(">H", bytes.fromhex(value[40:44]))[0]
                    minor = struct.unpack(">H", bytes.fromhex(value[44:48]))[0]

                    # check if major is 5 digits and minor is within range
                    if 10000 <= major <= 99999 and 1001 <= minor <= 1999:
                        coordinates = self.locations.get(minor, "Unknown Location")
                        if coordinates != "Unknown Location":
                            print(f"Detected iBeacon: UserID: {major}, Bus Stop: {minor}, Coordinates: {coordinates}")
                            save_onboard_data(major, minor, coordinates)
                        else:
                            print(f"Location for Bus Stop {minor} not found in locations.txt.")
                except Exception as e:
                    print(f"Failed to parse iBeacon data: {e}")

# load bus stop locations
locations = load_locations()

# set up scanner with the delegate
scanner = Scanner().withDelegate(ScanDelegate(locations))

# scan continuously - stop with Cntrl-C
print("Starting BLE scan...")
try:
    while True:
        scanner.scan(10.0)  # scan for 10 seconds in each loop iteration
except KeyboardInterrupt:
    print("Scan stopped by user.")
