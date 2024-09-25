import binascii

# raw string
raw_data = "02011A020A0C030319180CFF4C001007731F113B67602818094C6F636174696F6E20616E64204E617669676174696F6E"

# split hex data into bytes
data_bytes = binascii.unhexlify(raw_data)

# decode manufacturer specific data
manufacturer_data = data_bytes[13:25]  # slice based on exact position
user_id = int.from_bytes(manufacturer_data[:3], byteorder='big')
bus_id = int.from_bytes(manufacturer_data[3:6], byteorder='big')
location_id = int.from_bytes(manufacturer_data[6:], byteorder='big')

# decode readable string
readable_text = data_bytes[-24:].decode('utf-8')

# results
print(f"User ID: {user_id}")
print(f"Bus ID: {bus_id}")
print(f"Location ID: {location_id}")
print(f"Readable Text: {readable_text}")
