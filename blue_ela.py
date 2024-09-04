import sys
import time

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
        self.reported_count = 0
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
                        if self.state == 1:
                            self.reported_count += 1
                        self.state = state
                        print(
                            f"Device ID: {id} State: {state} Reported count: {self.reported_count} Device count: {count} Difference: {count-self.reported_count} Signal: {dev.rssi} Time Since State Change: {time.time() - self.t}"
                        )
                        self.t = time.time()


scanner = Scanner().withDelegate(ScanDelegate())
while True:
    devices = scanner.scan(10)

