from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class SearchItem:
    id: str
    page: str
    section: str
    title: str
    description: str
    keywords: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    icon_color: str = "#007AFF"
    
    # Optional localization keys for title & section if available
    title_key: str = ""
    section_key: str = ""


class SettingsIndex:
    """
    Static in-memory registry of all searchable controls across Echo Settings.
    Created once on startup or lazy evaluation, zero I/O and zero D-Bus overhead.
    """
    _instance = None
    _items: List[SearchItem] = []

    @classmethod
    def get_instance(cls) -> "SettingsIndex":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._build_index()

    def get_all_items(self) -> List[SearchItem]:
        return self._items

    def _build_index(self):
        self._items = [
            # =========================================================================
            # 1. APPEARANCE
            # =========================================================================
            SearchItem(
                id="appearance.theme",
                page="Appearance",
                section="Theme",
                title="Theme",
                description="Select Light, Dark, or Automatic appearance theme based on schedule",
                keywords=["theme", "dark mode", "light mode", "auto mode", "color mode", "style", "ui", "look"],
                aliases=["dark theme", "light theme", "dark mode", "night mode", "темная тема", "светлая тема", "авто тема", "оформление", "тема"],
                icon_color="#AF52DE",
                title_key="search.item.theme",
                section_key="search.sec.appearance",
            ),
            SearchItem(
                id="appearance.accent",
                page="Appearance",
                section="Accent Color",
                title="Accent Color",
                description="Choose system-wide highlight and accent color for buttons and controls",
                keywords=["accent", "color", "tint", "highlight", "blue", "purple", "red", "green", "orange", "yellow"],
                aliases=["system accent", "accent color", "акцент", "цвет акцента", "системный цвет", "подсветка"],
                icon_color="#AF52DE",
                title_key="search.item.accent",
                section_key="search.sec.appearance",
            ),
            SearchItem(
                id="appearance.contrast",
                page="Appearance",
                section="Contrast",
                title="Increase Contrast",
                description="Enhance visual contrast of UI borders, controls and cards for accessibility",
                keywords=["contrast", "accessibility", "borders", "visibility", "high contrast"],
                aliases=["high contrast", "контраст", "высокий контраст", "четкость"],
                icon_color="#AF52DE",
                title_key="search.item.contrast",
                section_key="search.sec.appearance",
            ),
            SearchItem(
                id="appearance.workspaces",
                page="Appearance",
                section="Multitasking & Workspaces",
                title="Workspaces & Multitasking",
                description="Configure multi-monitor workspaces and application window switching behavior",
                keywords=["workspace", "multitasking", "virtual desktops", "multiple displays", "app switching", "dock", "windows"],
                aliases=["virtual desktop", "workspaces", "многозадачность", "рабочие столы", "переключение окон", "мониторы"],
                icon_color="#AF52DE",
                title_key="search.item.workspaces",
                section_key="search.sec.appearance",
            ),
            SearchItem(
                id="appearance.hot_corners",
                page="Appearance",
                section="Hot Corners",
                title="Hot Corners",
                description="Trigger actions by moving the cursor to screen corners (Overview, Desktop, Lock, App Grid)",
                keywords=["hot corners", "corners", "gestures", "actions", "overview", "lock screen", "show desktop"],
                aliases=["hot corner", "screen corners", "активные углы", "углы экрана", "горячие углы", "жесты"],
                icon_color="#AF52DE",
                title_key="search.item.hot_corners",
                section_key="search.sec.appearance",
            ),

            # =========================================================================
            # 2. GENERAL
            # =========================================================================
            SearchItem(
                id="general.about",
                page="General",
                section="About",
                title="About This System",
                description="System overview, device model, processor, memory, GPU, and OS version information",
                keywords=["about", "system info", "specs", "hardware", "cpu", "gpu", "ram", "memory", "os", "model"],
                aliases=["system specs", "about mac", "о системе", "характеристики", "процессор", "память", "видеокарта", "железо"],
                icon_color="#8E8E93",
                title_key="search.item.about",
                section_key="search.sec.general",
            ),
            SearchItem(
                id="general.name",
                page="General",
                section="Device Name",
                title="Device Name",
                description="Change the computer hostname and local network identity name",
                keywords=["name", "hostname", "computer name", "device name", "identity"],
                aliases=["rename", "имя устройства", "имя компьютера", "хостнейм", "название"],
                icon_color="#8E8E93",
                title_key="search.item.device_name",
                section_key="search.sec.general",
            ),
            SearchItem(
                id="general.updates",
                page="General",
                section="Software Update",
                title="Software Updates",
                description="Check for system updates, package upgrades, and kernel security patches",
                keywords=["update", "software update", "upgrade", "patches", "system upgrade", "check updates"],
                aliases=["system update", "обновление", "обновление системы", "патчи", "апдейт"],
                icon_color="#8E8E93",
                title_key="search.item.software_update",
                section_key="search.sec.general",
            ),
            SearchItem(
                id="general.language",
                page="General",
                section="Language",
                title="System Language",
                description="Change application and system interface language (English, Russian, German, etc.)",
                keywords=["language", "locale", "translation", "interface language", "russian", "english", "deutsch"],
                aliases=["change language", "язык", "язык системы", "русский язык", "локализация", "перевод"],
                icon_color="#8E8E93",
                title_key="search.item.language",
                section_key="search.sec.general",
            ),
            SearchItem(
                id="general.airdrop",
                page="General",
                section="AirDrop & Sharing",
                title="AirDrop & Sharing",
                description="Discoverability and file sharing over local Wi-Fi and Bluetooth network",
                keywords=["airdrop", "sharing", "file sharing", "transfer", "bluetooth sharing", "send files"],
                aliases=["share", "поделиться", "передача файлов", "аирдроп", "общий доступ"],
                icon_color="#8E8E93",
                title_key="search.item.airdrop",
                section_key="search.sec.general",
            ),
            SearchItem(
                id="general.startup",
                page="General",
                section="Startup Items",
                title="Startup Items",
                description="Manage applications that open automatically when you log into your system",
                keywords=["startup", "autostart", "login items", "boot apps", "launch on startup"],
                aliases=["autostart", "автозагрузка", "автозапуск", "программы при входе", "стартап"],
                icon_color="#8E8E93",
                title_key="search.item.startup",
                section_key="search.sec.general",
            ),
            SearchItem(
                id="general.default_browser",
                page="General",
                section="Default Apps",
                title="Default Web Browser",
                description="Select default web browser for opening web links and HTML documents",
                keywords=["browser", "default browser", "chrome", "firefox", "safari", "web"],
                aliases=["default web browser", "браузер по умолчанию", "браузер", "интернет"],
                icon_color="#8E8E93",
                title_key="search.item.browser",
                section_key="search.sec.general",
            ),

            # =========================================================================
            # 3. DISPLAY
            # =========================================================================
            SearchItem(
                id="display.resolution",
                page="Display",
                section="Layout & Position",
                title="Display Resolution",
                description="Configure screen pixel resolution (e.g. 1920x1080, 2560x1440, 4K UHD)",
                keywords=["resolution", "display", "screen", "pixels", "4k", "1080p", "monitor", "native resolution"],
                aliases=["screen resolution", "разрешение экрана", "разрешение", "монитор", "пиксели", "дисплей"],
                icon_color="#32ADE6",
                title_key="search.item.resolution",
                section_key="search.sec.display",
            ),
            SearchItem(
                id="display.refresh_rate",
                page="Display",
                section="Layout & Position",
                title="Refresh Rate",
                description="Set display panel refresh frequency in Hertz (60Hz, 120Hz, 144Hz, 240Hz)",
                keywords=["refresh rate", "hz", "hertz", "144hz", "60hz", "smoothness", "framerate", "fps"],
                aliases=["screen hz", "частота обновления", "герцы", "герцовка", "fps", "плавность экрана"],
                icon_color="#32ADE6",
                title_key="search.item.refresh_rate",
                section_key="search.sec.display",
            ),
            SearchItem(
                id="display.scale",
                page="Display",
                section="Layout & Position",
                title="Display Scaling",
                description="Adjust desktop UI scale percentage (100%, 125%, 150%, 200% HiDPI)",
                keywords=["scale", "scaling", "hidpi", "ui scale", "text size", "zoom", "fractional scaling"],
                aliases=["display scale", "масштабирование", "масштаб", "размер элементов", "hidpi", "крупный текст"],
                icon_color="#32ADE6",
                title_key="search.item.scaling",
                section_key="search.sec.display",
            ),
            SearchItem(
                id="display.night_shift",
                page="Display",
                section="Night Light",
                title="Night Light",
                description="Shift display colors to warmer spectrum in the evening to reduce eye strain",
                keywords=["night shift", "night light", "blue light", "warm colors", "eye strain", "kelvin", "sunset"],
                aliases=["blue light filter", "ночной режим", "ночной свет", "фильтр синего", "теплые цвета", "глаза"],
                icon_color="#32ADE6",
                title_key="search.item.night_shift",
                section_key="search.sec.display",
            ),
            SearchItem(
                id="display.arrange",
                page="Display",
                section="Arrange Displays",
                title="Arrange Displays",
                description="Drag to arrange multiple display monitors in physical spatial layout",
                keywords=["arrange", "multi monitor", "dual screen", "alignment", "extended display"],
                aliases=["arrange screens", "расположение экранов", "два монитора", "положение мониторов"],
                icon_color="#32ADE6",
                title_key="search.item.arrange",
                section_key="search.sec.display",
            ),

            # =========================================================================
            # 4. SOUND
            # =========================================================================
            SearchItem(
                id="sound.output_volume",
                page="Sound",
                section="Output",
                title="Output Volume",
                description="Adjust master speaker and headphone audio playback volume level",
                keywords=["volume", "sound", "audio", "speakers", "headphones", "louder", "quieter", "mute"],
                aliases=["master volume", "громкость", "звук", "динамики", "наушники", "аудио", "тише", "громче"],
                icon_color="#FF2D55",
                title_key="search.item.volume",
                section_key="search.sec.sound",
            ),
            SearchItem(
                id="sound.device",
                page="Sound",
                section="Output",
                title="Output Device",
                description="Select default audio playback output endpoint (Speakers, HDMI, Headphones, Bluetooth)",
                keywords=["device", "output", "speakers", "hdmi", "dac", "soundcard", "playback"],
                aliases=["sound output", "устройство вывода", "вывод звука", "колонки", "выход аудио"],
                icon_color="#FF2D55",
                title_key="search.item.sound_output",
                section_key="search.sec.sound",
            ),
            SearchItem(
                id="sound.balance",
                page="Sound",
                section="Output",
                title="Stereo Balance",
                description="Adjust stereo sound output balance between Left and Right audio channels",
                keywords=["balance", "stereo", "left", "right", "channels", "pan"],
                aliases=["audio balance", "баланс звука", "баланс", "стерео", "левый правый канал"],
                icon_color="#FF2D55",
                title_key="search.item.balance",
                section_key="search.sec.sound",
            ),
            SearchItem(
                id="sound.test_speakers",
                page="Sound",
                section="Output",
                title="Test Speakers",
                description="Play test sound tones on Left and Right audio channels to verify speaker setup",
                keywords=["test", "speaker test", "audio test", "left speaker", "right speaker", "diagnostics"],
                aliases=["test audio", "проверка динамиков", "тест звука", "проверка колонок"],
                icon_color="#FF2D55",
                title_key="search.item.test_speakers",
                section_key="search.sec.sound",
            ),
            SearchItem(
                id="sound.effects",
                page="Sound",
                section="Sound Effects",
                title="Sound Effects",
                description="Alert tones, notification sounds, and user interface feedback sound effects",
                keywords=["effects", "alert", "beep", "ui sounds", "alerts", "feedback"],
                aliases=["alert sounds", "звуковые эффекты", "звуки оповещений", "сигналы"],
                icon_color="#FF2D55",
                title_key="search.item.effects",
                section_key="search.sec.sound",
            ),

            # =========================================================================
            # 5. NOTIFICATIONS
            # =========================================================================
            SearchItem(
                id="notifications.allow",
                page="Notifications",
                section="General",
                title="Allow Notifications",
                description="Enable or disable system-wide desktop notifications and banner popups",
                keywords=["notifications", "alerts", "banners", "popups", "messages", "allow notifications"],
                aliases=["enable notifications", "уведомления", "разрешить уведомления", "оповещения", "баннеры"],
                icon_color="#FF3B30",
                title_key="search.item.allow_notifications",
                section_key="search.sec.notifications",
            ),
            SearchItem(
                id="notifications.dnd",
                page="Notifications",
                section="Do Not Disturb",
                title="Do Not Disturb",
                description="Mute all notification banners and sound alerts during focus sessions",
                keywords=["dnd", "do not disturb", "mute", "focus", "silence", "quiet hours", "gaming"],
                aliases=["do not disturb", "не беспокоить", "режим не беспокоить", "тихий режим", "без звука"],
                icon_color="#FF3B30",
                title_key="search.item.dnd",
                section_key="search.sec.notifications",
            ),
            SearchItem(
                id="notifications.lock_screen",
                page="Notifications",
                section="Lock Screen",
                title="Lock Screen Notifications",
                description="Display notification banners and previews on the lock screen before unlocking",
                keywords=["lock screen", "lockscreen", "security", "privacy", "notifications on lock screen"],
                aliases=["notifications lock screen", "уведомления на экране блокировки", "экран блокировки", "показ на замке"],
                icon_color="#FF3B30",
                title_key="search.item.lock_screen_notif",
                section_key="search.sec.notifications",
            ),
            SearchItem(
                id="notifications.previews",
                page="Notifications",
                section="General",
                title="Show Previews",
                description="Show message contents and text previews in incoming notification banners",
                keywords=["previews", "message text", "content preview", "privacy"],
                aliases=["show previews", "показ миниатюр", "предпросмотр сообщений", "текст уведомлений"],
                icon_color="#FF3B30",
                title_key="search.item.previews",
                section_key="search.sec.notifications",
            ),
            SearchItem(
                id="notifications.badges",
                page="Notifications",
                section="General",
                title="Badge App Icons",
                description="Show unread count badges on application icons in the dock and panel",
                keywords=["badges", "unread count", "dock badges", "app icons", "counter"],
                aliases=["badge icons", "наклейки на значках", "счетчик уведомлений", "бейджи"],
                icon_color="#FF3B30",
                title_key="search.item.badges",
                section_key="search.sec.notifications",
            ),

            # =========================================================================
            # 6. MOUSE
            # =========================================================================
            SearchItem(
                id="mouse.speed",
                page="Mouse",
                section="Tracking",
                title="Tracking Speed",
                description="Adjust mouse pointer movement tracking speed and sensitivity",
                keywords=["mouse speed", "tracking speed", "pointer speed", "cursor speed", "sensitivity", "dpi", "velocity"],
                aliases=["pointer speed", "cursor speed", "mouse speed", "скорость мыши", "скорость указателя", "чувствительность мыши", "сенса"],
                icon_color="#8E8E93",
                title_key="search.item.mouse_speed",
                section_key="search.sec.pointer",
            ),
            SearchItem(
                id="mouse.natural_scroll",
                page="Mouse",
                section="Scrolling",
                title="Natural Scrolling",
                description="Content moves in the same direction as fingers/wheel (macOS style natural scrolling)",
                keywords=["natural scrolling", "scroll direction", "reverse scroll", "wheel direction", "mac scroll"],
                aliases=["invert scroll", "reverse scroll", "естественная прокрутка", "направление прокрутки", "инверсия колесика"],
                icon_color="#8E8E93",
                title_key="search.item.natural_scroll",
                section_key="search.sec.mouse",
            ),
            SearchItem(
                id="mouse.acceleration",
                page="Mouse",
                section="Tracking",
                title="Pointer Acceleration",
                description="Pointer speed scales dynamically with movement velocity",
                keywords=["acceleration", "pointer acceleration", "mouse accel", "linear", "flat profile"],
                aliases=["mouse accel", "акселерация мыши", "ускорение мыши", "ускорение указателя"],
                icon_color="#8E8E93",
                title_key="search.item.acceleration",
                section_key="search.sec.pointer",
            ),
            SearchItem(
                id="mouse.primary_button",
                page="Mouse",
                section="Buttons",
                title="Primary Mouse Button",
                description="Set Left or Right button as the primary click button for left-handed use",
                keywords=["primary button", "left click", "right click", "left handed", "swap buttons"],
                aliases=["left handed mouse", "основная кнопка мыши", "левая кнопка", "кнопка мыши для левши", "смена кнопок"],
                icon_color="#8E8E93",
                title_key="search.item.primary_btn",
                section_key="search.sec.buttons",
            ),
            SearchItem(
                id="mouse.double_click",
                page="Mouse",
                section="Buttons",
                title="Double-Click Speed",
                description="Adjust maximum time interval recognized between double clicks",
                keywords=["double click", "click speed", "interval", "double click test"],
                aliases=["double click speed", "двойной клик", "скорость двойного клика", "двойное нажатие"],
                icon_color="#8E8E93",
                title_key="search.item.double_click",
                section_key="search.sec.buttons",
            ),

            # =========================================================================
            # 7. KEYBOARD
            # =========================================================================
            SearchItem(
                id="keyboard.repeat_rate",
                page="Keyboard",
                section="Key Repeat",
                title="Key Repeat Rate",
                description="Speed at which a character repeats when holding down a key",
                keywords=["repeat rate", "key repeat", "typing speed", "repeat delay", "keyboard"],
                aliases=["key repeat rate", "повтор клавиш", "скорость повтора клавиш", "автоповтор"],
                icon_color="#8E8E93",
                title_key="search.item.repeat_rate",
                section_key="search.sec.keyboard",
            ),
            SearchItem(
                id="keyboard.delay",
                page="Keyboard",
                section="Key Repeat",
                title="Delay Until Repeat",
                description="Time to wait before a held key starts repeating characters",
                keywords=["delay", "repeat delay", "hold key", "keyboard response"],
                aliases=["key delay", "задержка повтора", "задержка до повтора", "время удержания"],
                icon_color="#8E8E93",
                title_key="search.item.repeat_delay",
                section_key="search.sec.keyboard",
            ),
            SearchItem(
                id="keyboard.backlight",
                page="Keyboard",
                section="Keyboard Backlight",
                title="Keyboard Backlight",
                description="Adjust keyboard key backlight brightness level and auto-off timeout",
                keywords=["backlight", "keyboard light", "illumination", "brightness"],
                aliases=["keyboard brightness", "подсветка клавиатуры", "яркость клавиатуры", "свет клавиш"],
                icon_color="#8E8E93",
                title_key="search.item.backlight",
                section_key="search.sec.keyboard",
            ),
            SearchItem(
                id="keyboard.input_sources",
                page="Keyboard",
                section="Input Sources",
                title="Input Sources & Layouts",
                description="Manage keyboard typing layouts (English, Russian, German) and shortcut switching",
                keywords=["layout", "input source", "switch language", "qwerty", "russian layout", "typing"],
                aliases=["keyboard layout", "раскладка клавиатуры", "переключение языка", "языки ввода", "раскладки"],
                icon_color="#8E8E93",
                title_key="search.item.input_sources",
                section_key="search.sec.keyboard",
            ),

            # =========================================================================
            # 8. PRIVACY & SECURITY
            # =========================================================================
            SearchItem(
                id="privacy.location",
                page="Privacy & Security",
                section="Permissions",
                title="Location Services",
                description="Allow apps to access system geographical location and GPS coordinates",
                keywords=["location", "gps", "privacy", "geo", "maps", "permission"],
                aliases=["location services", "геолокация", "местоположение", "службы геолокации", "доступ к локации"],
                icon_color="#007AFF",
                title_key="search.item.location",
                section_key="search.sec.privacy",
            ),
            SearchItem(
                id="privacy.camera",
                page="Privacy & Security",
                section="Permissions",
                title="Camera Access",
                description="Manage which applications have permission to capture webcam video",
                keywords=["camera", "webcam", "video", "privacy", "security", "permission"],
                aliases=["camera access", "камера", "доступ к камере", "веб-камера", "вебка"],
                icon_color="#007AFF",
                title_key="search.item.camera",
                section_key="search.sec.privacy",
            ),
            SearchItem(
                id="privacy.microphone",
                page="Privacy & Security",
                section="Permissions",
                title="Microphone Access",
                description="Control application access to microphone and sound recording input",
                keywords=["microphone", "mic", "audio input", "record", "permission"],
                aliases=["mic access", "микрофон", "доступ к микрофону", "запись звука"],
                icon_color="#007AFF",
                title_key="search.item.microphone",
                section_key="search.sec.privacy",
            ),
            SearchItem(
                id="privacy.screen_lock",
                page="Privacy & Security",
                section="Security",
                title="Screen Lock & Password",
                description="Require password immediately after screen turns off or system goes to sleep",
                keywords=["screen lock", "password", "lock", "security", "pin", "screen off timeout"],
                aliases=["screen lock", "блокировка экрана", "пароль при входе", "блокировка", "безопасность"],
                icon_color="#007AFF",
                title_key="search.item.screen_lock",
                section_key="search.sec.privacy",
            ),

            # =========================================================================
            # 9. WI-FI
            # =========================================================================
            SearchItem(
                id="wifi.power",
                page="Wi-Fi",
                section="Wi-Fi",
                title="Wi-Fi Power",
                description="Turn Wi-Fi wireless network adapter ON or OFF",
                keywords=["wifi", "wireless", "wlan", "network", "internet", "toggle wifi", "radio"],
                aliases=["wifi toggle", "вайфай", "вай фай", "беспроводная сеть", "включить wifi", "выключить wifi"],
                icon_color="#007AFF",
                title_key="search.item.wifi_power",
                section_key="search.sec.wifi",
            ),
            SearchItem(
                id="wifi.networks",
                page="Wi-Fi",
                section="Available Networks",
                title="Available Wi-Fi Networks",
                description="Scan, discover, and connect to nearby Wi-Fi access points and SSID networks",
                keywords=["networks", "ssid", "connect wifi", "hotspot", "scan networks", "password"],
                aliases=["wifi networks", "доступные сети", "список сетей", "подключение к wifi", "роутер", "вайфай сети"],
                icon_color="#007AFF",
                title_key="search.item.wifi_networks",
                section_key="search.sec.wifi",
            ),

            # =========================================================================
            # 10. BLUETOOTH
            # =========================================================================
            SearchItem(
                id="bluetooth.power",
                page="Bluetooth",
                section="Bluetooth",
                title="Bluetooth Power",
                description="Toggle Bluetooth controller radio ON or OFF for accessories and audio",
                keywords=["bluetooth", "bt", "wireless", "headphones", "mouse", "keyboard", "radio"],
                aliases=["bluetooth toggle", "блютуз", "блютус", "включить блютуз", "выключить блютуз"],
                icon_color="#007AFF",
                title_key="search.item.bt_power",
                section_key="search.sec.bluetooth",
            ),
            SearchItem(
                id="bluetooth.devices",
                page="Bluetooth",
                section="My Devices",
                title="Paired Bluetooth Devices",
                description="Manage paired headphones, mice, keyboards, gamepads and connect nearby devices",
                keywords=["devices", "pair", "connect", "audio", "gamepad", "controller"],
                aliases=["bluetooth devices", "устройства блютуз", "наушники блютуз", "подключение устройств"],
                icon_color="#007AFF",
                title_key="search.item.bt_devices",
                section_key="search.sec.bluetooth",
            ),

            # =========================================================================
            # 11. NETWORK
            # =========================================================================
            SearchItem(
                id="network.ethernet",
                page="Network",
                section="Wired Ethernet",
                title="Ethernet & Wired Network",
                description="Configure wired LAN network interface, IP address, gateway, and DNS settings",
                keywords=["ethernet", "wired", "lan", "ip", "dns", "gateway", "cable", "network status"],
                aliases=["ethernet", "проводная сеть", "сеть", "интернет", "лан", "ip адрес", "кабель"],
                icon_color="#007AFF",
                title_key="search.item.ethernet",
                section_key="search.sec.network",
            ),
            SearchItem(
                id="network.vpn",
                page="Network",
                section="VPN",
                title="VPN Connections",
                description="Manage WireGuard, OpenVPN, and secure tunnel network connections",
                keywords=["vpn", "wireguard", "openvpn", "tunnel", "proxy", "secure connection"],
                aliases=["vpn", "впн", "vpn соединения", "прокси"],
                icon_color="#007AFF",
                title_key="search.item.vpn",
                section_key="search.sec.network",
            ),

            # =========================================================================
            # 12. STORAGE
            # =========================================================================
            SearchItem(
                id="storage.overview",
                page="Storage",
                section="Storage",
                title="Storage Overview",
                description="Disk drive capacity, free space breakdown, System, Apps, Games, and Media usage",
                keywords=["storage", "disk", "ssd", "hdd", "free space", "used space", "games", "system", "capacity"],
                aliases=["disk space", "хранилище", "память диска", "свободное место", "диск", "накопитель", "ссд"],
                icon_color="#8E8E93",
                title_key="search.item.storage_overview",
                section_key="search.sec.storage",
            ),
            SearchItem(
                id="storage.recommendations",
                page="Storage",
                section="Recommendations",
                title="Storage Recommendations",
                description="Review recommendations for clearing caches, temporary files, and old downloads",
                keywords=["recommendations", "cleanup", "clear cache", "free up space", "temp files", "downloads"],
                aliases=["storage clean", "очистка диска", "рекомендации по очистке", "удаление кэша", "освободить место"],
                icon_color="#8E8E93",
                title_key="search.item.storage_recommendations",
                section_key="search.sec.storage",
            ),

            # =========================================================================
            # 13. POWER
            # =========================================================================
            SearchItem(
                id="power.mode",
                page="Power",
                section="Power Mode",
                title="Power Mode",
                description="Select Performance, Balanced, or Power Saver battery optimization profile",
                keywords=["power mode", "battery saver", "performance", "balanced", "power profile", "energy"],
                aliases=["power mode", "режим питания", "производительность", "экономия энергии", "энергосбережение"],
                icon_color="#4CD964",
                title_key="search.item.power_mode",
                section_key="search.sec.power",
            ),
            SearchItem(
                id="power.sleep",
                page="Power",
                section="Sleep & Screen Off",
                title="Screen Sleep Timeout",
                description="Configure idle time before display screen turns off to save power",
                keywords=["sleep", "screen off", "display sleep", "timeout", "idle", "energy saver"],
                aliases=["screen sleep", "отключение экрана", "сон", "время до сна", "спящий режим"],
                icon_color="#4CD964",
                title_key="search.item.screen_sleep",
                section_key="search.sec.power",
            ),
            SearchItem(
                id="power.battery",
                page="Power",
                section="Battery",
                title="Battery Health",
                description="Current battery charge percentage, health capacity status, and charging rate",
                keywords=["battery", "charge", "battery health", "cycle count", "power adapter", "charging"],
                aliases=["battery level", "батарея", "аккумулятор", "состояние батареи", "зарядка", "уровень заряда"],
                icon_color="#4CD964",
                title_key="search.item.battery_health",
                section_key="search.sec.power",
            ),

            # =========================================================================
            # 14. ECHO SEARCH (SPOTLIGHT)
            # =========================================================================
            SearchItem(
                id="search.shortcuts",
                page="Echo Search",
                section="Keyboard Shortcuts",
                title="Echo Search Hotkey",
                description="Customize system-wide keyboard shortcut to activate Echo Search (Spotlight)",
                keywords=["search hotkey", "spotlight shortcut", "command space", "super space", "launcher hotkey"],
                aliases=["spotlight hotkey", "горячая клавиша поиска", "сочетание клавиш поиска", "спотлайт", "лаунчер"],
                icon_color="#FF9500",
                title_key="spotlight.shortcut",
                section_key="spotlight.title",
            ),
            SearchItem(
                id="search.categories",
                page="Echo Search",
                section="Search Categories",
                title="Search Results Categories",
                description="Select indexed categories for Spotlight results: Apps, Documents, Calculations, Settings",
                keywords=["search categories", "indexing", "spotlight categories", "calculator", "files search"],
                aliases=["search sources", "категории поиска", "индексация", "результаты поиска", "источники поиска"],
                icon_color="#FF9500",
                title_key="spotlight.categories",
                section_key="spotlight.title",
            ),
        ]
