# bluedoor

"""
How to use this on another tower:
    - Clone repo: `git clone https://github.com/davidenders11/bluedoor.git`
    - Create a venv in this directory: `python -m venv .`
    - Activate virtual environment on that tower (`source /home/kargo/bluedoor/bin/activate`)
    - Install requirements `pip install -r requirements.txt`
    - Run script with sudo (sudo python /home/kargo/bluedoor/blue_ela.py)
        - Must be run as root according to bluepy docs: https://ianharvey.github.io/bluepy-doc/scanner.html
    - BTLEManagementError with code 17 and error "Invalid index" probably means there is no dongle on that tower
"""
