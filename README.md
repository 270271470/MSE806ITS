# MSE806ITS
BLE Passenger Detection

First, open the system terminal (outside the virtual environment) and install the following packages:

sudo apt install libbluetooth-dev libglib2.0-dev build-essential python3-dev

Once the above packages are installed:

1. Use VS Code to clone https://github.com/270271470/MSE806ITS.git or CLI

2. Once cloned, in the 'beacon-project' directory, create a new virtual environment:

	-> python3 -m venv venv

3. Activate venv with:

	-> source venv/bin/activate

4. Install the required Libraries:

	-> pip install –r requirements.txt

5. The scanner.py file requires sudo permission, run the file with:

	-> E.g. sudo /home/yourname/beacon-project/venv/bin/python3 scanner.py