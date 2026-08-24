import os
import time
from PySide6.QtCore import QObject, QTimer, Signal

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class DiskActivityMonitor(QObject):
    # read_bytes_sec, write_bytes_sec, iops, is_active
    activity_updated = Signal(float, float, int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._poll)
        self._disk_name = None
        self._last_stats = None
        self._last_time = 0

    def start(self, disk_name):
        if not disk_name: return
        self._disk_name = os.path.basename(disk_name) # Ensure no paths, e.g. "nvme0n1"
        self._last_stats = self._read_stats()
        self._last_time = time.perf_counter()
        self.activity_updated.emit(0.0, 0.0, 0, False)
        self.timer.start()

    def stop(self):
        self.timer.stop()
        self._last_stats = None
        self.activity_updated.emit(0.0, 0.0, 0, False)

    def _read_stats(self):
        if not HAS_PSUTIL or not self._disk_name:
            return None
        try:
            counters = psutil.disk_io_counters(perdisk=True)
            if counters and self._disk_name in counters:
                c = counters[self._disk_name]
                return {
                    'read_bytes': c.read_bytes,
                    'write_bytes': c.write_bytes,
                    'reads': c.read_count,
                    'writes': c.write_count
                }
        except Exception:
            pass
        return None

    def _poll(self):
        current_stats = self._read_stats()
        current_time = time.perf_counter()
        
        if current_stats and self._last_stats and current_time > self._last_time:
            dt = current_time - self._last_time
            
            d_reads = current_stats['reads'] - self._last_stats['reads']
            d_writes = current_stats['writes'] - self._last_stats['writes']
            d_read_bytes = current_stats['read_bytes'] - self._last_stats['read_bytes']
            d_write_bytes = current_stats['write_bytes'] - self._last_stats['write_bytes']
            
            # Guard against negative deltas (e.g. counters reset)
            if d_reads < 0 or d_writes < 0 or d_read_bytes < 0 or d_write_bytes < 0:
                d_reads = d_writes = d_read_bytes = d_write_bytes = 0
            
            read_bytes_sec = d_read_bytes / dt
            write_bytes_sec = d_write_bytes / dt
            iops = int((d_reads + d_writes) / dt)
            
            # Consider active if IOPS > 0 or throughput > 1KB/s
            is_active = iops > 0 or read_bytes_sec > 1024 or write_bytes_sec > 1024
            
            if not is_active:
                read_bytes_sec = 0.0
                write_bytes_sec = 0.0
                iops = 0
                
            self.activity_updated.emit(read_bytes_sec, write_bytes_sec, iops, is_active)
            
        self._last_stats = current_stats
        self._last_time = current_time
