import shutil
import subprocess
import json
import glob
import os

class StorageBackend:
    def get_root_usage(self):
        try:
            usage = shutil.disk_usage('/')
            return {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free
            }
        except Exception:
            return None

    def get_detailed_storage_info(self):
        try:
            cmd = ["lsblk", "-b", "-J", "-o", "NAME,SIZE,FSUSED,FSUSE%,FSTYPE,MOUNTPOINT,TYPE,ROTA,MODEL,VENDOR,SERIAL,TRAN"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            disks = []
            
            # Helper to fetch NVMe temp
            def get_nvme_temp(name):
                try:
                    for hwmon in glob.glob('/sys/class/hwmon/hwmon*'):
                        with open(os.path.join(hwmon, 'name'), 'r') as f:
                            hname = f.read().strip()
                        if hname == 'nvme':
                            # Rough check, works for single nvme usually, but can be improved
                            temp_file = os.path.join(hwmon, 'temp1_input')
                            if os.path.exists(temp_file):
                                with open(temp_file, 'r') as f:
                                    temp_milli = int(f.read().strip())
                                    return f"{temp_milli // 1000}°C"
                except Exception:
                    pass
                return "Unavailable"

            for dev in data.get("blockdevices", []):
                if dev.get("type") == "disk":
                    # Filter out loop devices or zram
                    if dev.get("name", "").startswith("loop") or dev.get("name", "").startswith("zram"):
                        continue
                        
                    rota = dev.get("rota")
                    tran = dev.get("tran")
                    
                    dtype = "Unknown"
                    if str(tran).lower() == "nvme":
                        dtype = "NVMe"
                    elif str(tran).lower() == "sata" or str(tran).lower() == "ata":
                        dtype = "HDD" if rota else "SSD"
                    elif str(tran).lower() == "usb":
                        dtype = "USB"
                        
                    temp = "Unavailable"
                    if dtype == "NVMe":
                        temp = get_nvme_temp(dev.get("name"))
                        
                    disk_info = {
                        "name": dev.get("name"),
                        "model": str(dev.get("model") or "Unavailable").strip(),
                        "vendor": str(dev.get("vendor") or "Unavailable").strip(),
                        "serial": str(dev.get("serial") or "Unavailable").strip(),
                        "size": dev.get("size", 0),
                        "type": dtype,
                        "tran": str(tran or "Unavailable").upper(),
                        "temperature": temp,
                        "speed": "Unavailable", # Reliable speed requires root/smartctl
                        "partitions": []
                    }
                    
                    for child in dev.get("children", []):
                        if child.get("type") == "part":
                            disk_info["partitions"].append({
                                "name": child.get("name"),
                                "size": child.get("size", 0),
                                "used": child.get("fsused", 0) or 0,
                                "use_percent": child.get("fsuse%", "0%"),
                                "fstype": child.get("fstype", "Unknown"),
                                "mountpoint": child.get("mountpoint", None)
                            })
                            
                    disks.append(disk_info)
                    
            return disks
        except Exception as e:
            print(f"Error fetching storage info: {e}")
            return []
