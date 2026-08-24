import os
import json
import subprocess
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from components.storage.model import StorageCategory

CACHE_DIR = os.path.expanduser("~/.cache/echo-settings")
CACHE_FILE = os.path.join(CACHE_DIR, "storage_summary.json")

class StorageAnalyzer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StorageAnalyzer, cls).__new__(cls)
            cls._instance.home_dir = str(Path.home())
            cls._instance._memory_cache = None
            os.makedirs(CACHE_DIR, exist_ok=True)
            cls._instance._load_disk_cache()
        return cls._instance
        
    def _load_disk_cache(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    if isinstance(cached_data, dict):
                        # Convert category_sizes to StorageCategory instances
                        cats = {}
                        for k, v in cached_data.get("category_sizes", {}).items():
                            sz = v.get("size_bytes", 0) if isinstance(v, dict) else int(v)
                            cats[k] = StorageCategory(name=k, size_bytes=sz)
                        cached_data["category_sizes"] = cats
                        self._memory_cache = cached_data
            except Exception:
                pass

    def _save_disk_cache(self, data):
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            serializable = {
                "recommendations": data.get("recommendations", {}),
                "largest_files": data.get("largest_files", []),
                "category_sizes": {
                    k: {"size_bytes": v.size_bytes} for k, v in data.get("category_sizes", {}).items()
                }
            }
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
        except Exception:
            pass

    def _get_xdg_dir(self, name, fallbacks=None):
        try:
            r = subprocess.run(['xdg-user-dir', name], capture_output=True, text=True, timeout=1)
            p = r.stdout.strip()
            if p and os.path.exists(p):
                return p
        except Exception:
            pass
        if fallbacks:
            for f in fallbacks:
                p = os.path.join(self.home_dir, f)
                if os.path.exists(p):
                    return p
        mapping = {
            "DOCUMENTS": ["Documents", "Документы"],
            "DOWNLOAD": ["Downloads", "Загрузки"],
            "PICTURES": ["Pictures", "Изображения"],
            "VIDEOS": ["Videos", "Видео"],
            "MUSIC": ["Music", "Музыка"]
        }
        for fb in mapping.get(name, [name.capitalize()]):
            p = os.path.join(self.home_dir, fb)
            if os.path.exists(p):
                return p
        return os.path.join(self.home_dir, name.capitalize())

    def _batch_du(self, paths):
        existing = [p for p in paths if p and os.path.exists(p)]
        if not existing:
            return 0
        try:
            res = subprocess.run(['du', '-sb'] + existing, capture_output=True, text=True, timeout=5)
            total = 0
            for line in res.stdout.strip().split('\n'):
                if line:
                    parts = line.split(maxsplit=1)
                    if parts and parts[0].isdigit():
                        total += int(parts[0])
            return total
        except Exception:
            return 0

    def _get_dir_size(self, path_str):
        return self._batch_du([path_str])

    def _format_size(self, size_bytes):
        if size_bytes == 0:
            return "0 KB"
        gb = size_bytes / (1024**3)
        if gb >= 1:
            return f"{round(gb, 1)} GB"
        mb = size_bytes / (1024**2)
        if mb >= 1:
            return f"{round(mb, 1)} MB"
        kb = size_bytes / 1024
        return f"{round(kb, 1)} KB"

    def get_cached_or_instant_categories(self) -> dict[str, StorageCategory]:
        """Returns categories instantaneously for initial zero-delay rendering."""
        if self._memory_cache and "category_sizes" in self._memory_cache and self._memory_cache["category_sizes"]:
            return self._memory_cache["category_sizes"].copy()
        
        # Fast fallback scan (top directories only)
        return self.scan_quick_categories()

    def scan_quick_categories(self) -> dict[str, StorageCategory]:
        home = self.home_dir
        
        game_paths = [
            os.path.join(home, '.local/share/Steam'),
            os.path.join(home, '.local/share/Steam.bak'),
            os.path.join(home, '.steam'),
            os.path.join(home, '.local/share/lutris'),
            os.path.join(home, '.local/share/heroic'),
            os.path.join(home, '.local/share/Paradox Interactive'),
            os.path.join(home, '.var/app/com.usebottles.bottles'),
            os.path.join(home, '.wine'),
            os.path.join(home, 'Games'),
            os.path.join(home, 'Игры'),
        ]
        
        app_paths = [
            '/var/lib/flatpak',
            '/var/lib/snapd/snaps',
            os.path.join(home, '.local/share/flatpak'),
            os.path.join(home, '.var/app'),
            os.path.join(home, 'Applications'),
            '/opt'
        ]
        
        cats = {
            "Games": StorageCategory("Games", self._batch_du(game_paths)),
            "Downloads": StorageCategory("Downloads", self._batch_du([self._get_xdg_dir('DOWNLOAD', ['Downloads', 'Загрузки'])])),
            "Applications": StorageCategory("Applications", self._batch_du(app_paths)),
            "Pictures": StorageCategory("Pictures", self._batch_du([self._get_xdg_dir('PICTURES', ['Pictures', 'Изображения'])])),
            "Videos": StorageCategory("Videos", self._batch_du([self._get_xdg_dir('VIDEOS', ['Videos', 'Видео'])])),
            "Music": StorageCategory("Music", self._batch_du([self._get_xdg_dir('MUSIC', ['Music', 'Музыка'])])),
            "Documents": StorageCategory("Documents", self._batch_du([self._get_xdg_dir('DOCUMENTS', ['Documents', 'Документы'])])),
            "Trash": StorageCategory("Trash", self._batch_du([os.path.join(home, '.local/share/Trash')])),
        }
        return cats

    def get_largest_files(self):
        largest = []
        try:
            # Search user media and downloads first for fast non-blocking output
            search_dirs = [
                self._get_xdg_dir('DOWNLOAD', ['Downloads', 'Загрузки']),
                self._get_xdg_dir('DOCUMENTS', ['Documents', 'Документы']),
                self._get_xdg_dir('VIDEOS', ['Videos', 'Видео']),
                self.home_dir
            ]
            existing_dirs = [d for d in search_dirs if d and os.path.exists(d)]
            dirs_str = " ".join(f'"{d}"' for d in existing_dirs[:2])
            
            cmd = f"find {dirs_str} -maxdepth 4 -type f -size +50M -exec du -b {{}} + 2>/dev/null | sort -nr | head -n 5"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=2)
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        size_bytes = int(parts[0])
                        file_path = parts[1]
                        file_name = os.path.basename(file_path)
                        folder_path = os.path.dirname(file_path).replace(self.home_dir, "~")
                        largest.append({
                            "name": file_name,
                            "path": folder_path,
                            "size": self._format_size(size_bytes)
                        })
        except Exception:
            pass
        return largest

    def analyze(self, force_refresh=False, check_cancelled=None, category_callback=None):
        if self._memory_cache is not None and not force_refresh and "largest_files" in self._memory_cache:
            if category_callback:
                for cat in self._memory_cache.get("category_sizes", {}).values():
                    category_callback(cat)
            return self._memory_cache
            
        data = {
            "recommendations": {},
            "largest_files": [],
            "category_sizes": {}
        }
        
        home = self.home_dir
        
        category_definitions = [
            ("Games", [
                os.path.join(home, '.local/share/Steam'),
                os.path.join(home, '.local/share/Steam.bak'),
                os.path.join(home, '.steam'),
                os.path.join(home, '.local/share/lutris'),
                os.path.join(home, '.local/share/heroic'),
                os.path.join(home, '.local/share/Paradox Interactive'),
                os.path.join(home, '.var/app/com.usebottles.bottles'),
                os.path.join(home, '.wine'),
                os.path.join(home, 'Games'),
                os.path.join(home, 'Игры'),
            ]),
            ("Downloads", [self._get_xdg_dir('DOWNLOAD', ['Downloads', 'Загрузки'])]),
            ("Applications", [
                '/var/lib/flatpak',
                '/var/lib/snapd/snaps',
                os.path.join(home, '.local/share/flatpak'),
                os.path.join(home, '.var/app'),
                os.path.join(home, 'Applications'),
                '/opt'
            ]),
            ("Pictures", [self._get_xdg_dir('PICTURES', ['Pictures', 'Изображения'])]),
            ("Videos", [self._get_xdg_dir('VIDEOS', ['Videos', 'Видео'])]),
            ("Music", [self._get_xdg_dir('MUSIC', ['Music', 'Музыка'])]),
            ("Documents", [self._get_xdg_dir('DOCUMENTS', ['Documents', 'Документы'])]),
            ("Trash", [os.path.join(home, '.local/share/Trash')]),
        ]
        
        for name, paths in category_definitions:
            if check_cancelled and check_cancelled():
                return data
            size = self._batch_du(paths)
            cat_obj = StorageCategory(name=name, size_bytes=size)
            data["category_sizes"][name] = cat_obj
            if category_callback:
                category_callback(cat_obj)
                
        if check_cancelled and check_cancelled():
            return data
            
        cache_path = os.path.join(self.home_dir, ".cache")
        cache_size = self._get_dir_size(cache_path)
        
        trash_sz = data["category_sizes"].get("Trash").size_bytes if "Trash" in data["category_sizes"] else 0
        dl_sz = data["category_sizes"].get("Downloads").size_bytes if "Downloads" in data["category_sizes"] else 0
        
        data["recommendations"]["Empty Trash"] = self._format_size(trash_sz) if trash_sz > 0 else "Clean"
        data["recommendations"]["Downloads"] = self._format_size(dl_sz) if dl_sz > 0 else "0 KB"
        data["recommendations"]["Cache"] = self._format_size(cache_size) if cache_size > 0 else "0 KB"
        
        if check_cancelled and check_cancelled():
            return data
            
        data["largest_files"] = self.get_largest_files()
        
        self._memory_cache = data
        self._save_disk_cache(data)
        return data

class StorageScannerThread(QThread):
    scan_finished = Signal(dict)
    category_updated = Signal(object) # Emits StorageCategory
    
    def __init__(self, parent=None, force_refresh=False):
        super().__init__(parent)
        self.force_refresh = force_refresh
        
    def _emit_category(self, category_obj: StorageCategory):
        self.category_updated.emit(category_obj)
        
    def run(self):
        analyzer = StorageAnalyzer()
        data = analyzer.analyze(
            force_refresh=self.force_refresh,
            check_cancelled=self.isInterruptionRequested,
            category_callback=self._emit_category
        )
        if not self.isInterruptionRequested():
            self.scan_finished.emit(data)
