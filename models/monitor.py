from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class MonitorModel:
    id: str # e.g. "DP-1"
    name: str # e.g. "Xiaomi Corporation 27"
    x: int = 0
    y: int = 0
    width: int = 1920
    height: int = 1080
    scale: float = 1.0
    orientation: int = 0  # 0=0°, 1=90°, 2=180°, 3=270°
    is_primary: bool = False
    is_active: bool = True
    current_mode: str = "1920x1080"
    current_rate: float = 60.0
    resolutions: List[str] = field(default_factory=list)
    rates: Dict[str, List[float]] = field(default_factory=dict)
