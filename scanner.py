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
import json
import os
from datetime import datetime

# load location mappings from resources directory (this will probably be replaced by a database or API query)
def load_locations(filename="locations.txt"):
    resources_path = os.path.join(os.path.dirname(__file__), "resources", filename)
    locations = {}
    with open(resources_path, 'r') as file:
        for line in file:
            bus_stop, coordinates = line.strip().split(':')
            locations[int(bus_stop)] = coordinates.strip()
    return locations

# save data to bus-specific JSON file in the appropriate year/month/day directory
def save_onboard_data(userid, busid, locationid, coordinates):
    # create dir structure based on the current year, month and day
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    
    # base directory for data storage
    base_directory = os.path.join(os.path.dirname(__file__), "livedata", year, month, day)
    
    # create directories if they do not exist
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    # def file path for specific bus
    filename = f"bus-{busid}.json"
    filepath = os.path.join(base_directory, filename)

    # prepare entry with the current timestamp
    timestamp = now.isoformat()
    entry = {
        "userid": userid,
        "busid": busid,
        "location": f"Bus stop {locationid}",
        "coordinates": coordinates,
        "timestamp": timestamp
    }

    # get existing data + append new entry +  save
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
            # separate handling for Android and iPhone based on value content
            if desc == "Manufacturer" and len(value) >= 40:
                # check if beacon is from an Android device
                if value.startswith("4c000215"):
                    self.handle_android_beacon(value)
                # check if beacon is from an iPhone device
                elif value.startswith("4c000215"):
                    self.handle_iphone_beacon(value)

    def handle_android_beacon(self, value):
        """
        handle parsing and processing for Android beacons
        """
        try:
            # extract UUID from transmitted data
            uuid = value[8:40]  # extract, assuming starts at 8th character

            # parse UUID to extract relevant parts
            userid = uuid[0:8]  # first 8 chars for userid
            identifier1 = uuid[8:12]  # next 4 chars (should be 1234)
            busid = uuid[12:16]  # next 4 chars for busid
            locationid = uuid[16:20]  # next 4 chars for locationid
            identifier2 = uuid[20:]  # remaining chars (should be 567812345678)

            # validate identifiers
            if identifier1 == "1234" and identifier2 == "567812345678":
                coordinates = self.locations.get(int(locationid), "Unknown Location")
                if coordinates != "Unknown Location":
                    # print only valid beacons
                    print(f"Valid Beacon: UserID: {userid}, BusID: {busid}, LocationID: {locationid}, Coordinates: {coordinates}")
                    save_onboard_data(userid, busid, locationid, coordinates)

        except Exception as e:
            # suppress errors that are not valid beacons
            pass

    def handle_iphone_beacon(self, value):
        """
        handles parsing + processing for iPhone beacons
        """
        try:
            # extract from the transmitted data
            uuid = value[8:40]  # extract UUID assuming starts at 8th char

            # parse UUID to extract relevant parts
            userid = uuid[0:8]  # first 8 chars for userid
            identifier1 = uuid[8:12]  # next 4 chars (should be 1234)
            busid = uuid[12:16]  # next 4 chars for busid
            locationid = uuid[16:20]  # next 4 chars for locationid
            identifier2 = uuid[20:]  # remaining chars (should be 567812345678)
            

            # validate identifiers
            if identifier1 == "1234" and identifier2 == "567812345678":
                coordinates = self.locations.get(int(locationid), "Unknown Location")
                if coordinates != "Unknown Location":
                    # print only if valid beacon
                    print(f"Valid Beacon: UserID: {userid}, BusID: {busid}, LocationID: {locationid}, Coordinates: {coordinates}")
                    save_onboard_data(userid, busid, locationid, coordinates)

        except Exception as e:
            # suppress errors that are not valid beacons
            pass

# load bus stop locations
locations = load_locations()

# set up scanner with the delegate
scanner = Scanner().withDelegate(ScanDelegate(locations))

# scan continuously - stop with Cntrl-C
print("Scanning for valid Passenger Beacons...")
try:
    while True:
        scanner.scan(10.0)  # scan for 10 seconds in each loop iteration
except KeyboardInterrupt:
    print("Scan stopped by user.")
