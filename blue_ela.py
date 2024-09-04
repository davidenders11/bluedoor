import sys
import time

"""
How to use this on another tower:
    - Copy entire folder bluedoor to tower (scp -r /home/kargo/bluedoor/ kargo@argus-000-000-0002-02:~)
    - Activate virtual environment on that tower (source /home/kargo/bluedoor/bin/activate)
    - Make sure bluepy is installed (pip install bluepy)
    - Run script with sudo (sudo python /home/kargo/bluedoor/blue_ela.py)
        - Must be run as root according to bluepy docs: https://ianharvey.github.io/bluepy-doc/scanner.html
    - BTLEManagementError with code 17 and error "Invalid index" probably means there is no dongle on that tower
"""


# Add the desired path to the beginning of sys.path
sys.path.insert(0, "/home/kargo/bluedoor/lib/python3.10/site-packages/")
from bluepy.btle import Scanner, DefaultDelegate


# this part is generic parsing for BLE advertising data
def parse_data(payload):
    segments = {}
    idx = 0
    try:
        while idx < len(payload):
            next_size = int(payload[idx])
            idx += 1
            seg = payload[idx : idx + next_size]
            seg_type = seg[0]
            content = seg[1:]
            if seg_type == 0x16:
                seg_type_sub = int(content[0]) * 16 + int(content[1])
                seg_type = (seg_type, seg_type_sub)
                content = content[2:]

            segments[seg_type] = content
            idx += next_size
    except:
        pass
    return segments


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        self.t = time.time()
        self.state = -1
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewData:
            if isinstance(dev.rawData, bytes):
                segments = parse_data(dev.rawData)
                device_type = segments.get((22, 1050), None)
                data_raw = segments.get((22, 138), None)
                device_id = segments.get(9, None)
                if (
                    device_type == b"\x00"
                    and data_raw is not None
                    and device_id is not None
                ):
                    # ELA door sensor
                    data = int.from_bytes(data_raw, byteorder="little", signed=False)
                    state = data % 2
                    count = data >> 1
                    id = device_id.decode("ascii")
                    if state != self.state:
                        self.state = state
                        print(
                            f"Device ID: {id} State: {state} Count: {count} Signal: {dev.rssi} Time Since State Change: {time.time() - self.t}"
                        )
                        self.t = time.time()


scanner = Scanner().withDelegate(ScanDelegate())
while True:
    devices = scanner.scan(10)

