from PySide6.QtCore import QThread, Signal
import subprocess
import array
import math
import os

class MicMonitorThread(QThread):
    level_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.proc = None
        
    def run(self):
        self.running = True
        try:
            env = dict(os.environ, LC_ALL="C")
            self.proc = subprocess.Popen(
                ['parec', '--format=s16le', '--channels=1', '--rate=16000', '--latency-msec=30'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                env=env
            )
            
            while self.running and self.proc.poll() is None:
                data = self.proc.stdout.read(1024)
                if not data:
                    break
                
                try:
                    arr = array.array('h', data)
                    if arr:
                        peak = max(abs(x) for x in arr)
                        if peak > 0:
                            db = 20 * math.log10(peak / 32768.0)
                            level = (db + 45) / 45.0
                            level = max(0.0, min(1.0, level))
                        else:
                            level = 0.0
                            
                        self.level_changed.emit(level)
                except Exception:
                    pass
        except Exception:
            pass
        finally:
            if self.proc:
                self.proc.terminate()
                self.proc.wait()
                
    def stop(self):
        self.running = False
        if self.proc:
            self.proc.terminate()
        self.wait()
