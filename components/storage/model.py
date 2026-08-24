from dataclasses import dataclass

STORAGE_COLORS = {
    "Applications": "#FF2D55",
    "Games": "#BF5AF2",
    "Documents": "#FF9500",
    "Downloads": "#34C759",
    "Pictures": "#32ADE6",
    "Videos": "#5E5CE6",
    "Music": "#FF375F",
    "Trash": "#8E8E93",
    "Other": "#5AC8FA",
    "Used": "#007AFF"
}

@dataclass
class StorageCategory:
    name: str
    size_bytes: int
    
    @property
    def size_gb(self) -> float:
        return self.size_bytes / (1024**3)
        
    @property
    def color(self) -> str:
        return STORAGE_COLORS.get(self.name, "#5AC8FA")
