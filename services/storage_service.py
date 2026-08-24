from backends.storage_backend import StorageBackend

class StorageService:
    def __init__(self):
        self.backend = StorageBackend()

    def get_storage_info(self):
        usage = self.backend.get_root_usage()
        if not usage:
            return None
            
        total_gb = usage['total'] / (1024**3)
        used_gb = usage['used'] / (1024**3)
        free_gb = usage['free'] / (1024**3)
        percent = (usage['used'] / usage['total']) * 100

        return {
            "total_gb": round(total_gb, 1),
            "used_gb": round(used_gb, 1),
            "free_gb": round(free_gb, 1),
            "percent": int(percent)
        }

    def get_detailed_disks(self):
        disks = self.backend.get_detailed_storage_info()
        for disk in disks:
            disk["size_gb"] = round(disk["size"] / (1024**3), 1)
            for part in disk["partitions"]:
                part["size_gb"] = round(part["size"] / (1024**3), 1)
                
                used = 0
                if part.get("used"):
                    try:
                        used = int(part["used"])
                    except:
                        pass
                        
                part["used_gb"] = round(used / (1024**3), 1)
                part["free_gb"] = round(max(0, part["size_gb"] - part["used_gb"]), 1)
                
                use_pct = str(part.get("use_percent", "0%")).replace('%', '')
                try:
                    part["percent"] = int(use_pct)
                except:
                    part["percent"] = 0
                    
        return disks
        
    def get_trim_status(self):
        import subprocess
        try:
            cmd = ["systemctl", "is-active", "fstrim.timer"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1)
            if "active" in result.stdout.strip():
                return "Enabled"
            return "Disabled"
        except Exception:
            return "Unavailable"
