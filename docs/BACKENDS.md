# Архитектура Бэкендов (Backends)

В этом документе приведена таблица связей между разделами приложения, соответствующими Backend-компонентами и используемыми Linux API.

| Раздел | Backend | Linux API / Служба | Статус |
|--------|---------|--------------------|--------|
| **Appearance** | `AppearanceBackend` | GSettings (`org.gnome.desktop.interface`) | ✅ Готово |
| **Storage** | `StorageBackend` | `shutil.disk_usage` / `df` | ✅ Готово |
| **Wi-Fi** | `WiFiBackend` | NetworkManager (`nmcli` / DBus) | ✅ Готово |
| **Bluetooth** | `BluetoothBackend` | BlueZ (`bluetoothctl` / DBus) | ⏳ Запланировано |
| **Sound** | `SoundBackend` | PipeWire (`wpctl` / `pactl`) | ⏳ Запланировано |
| **Power** | `PowerBackend` | UPower (DBus) / `power-profiles-daemon` | ⏳ Запланировано |
| **Users** | `UsersBackend` | AccountsService (DBus) | ⏳ Запланировано |
| **Wallpaper** | `WallpaperBackend` | GSettings (`org.gnome.desktop.background`) | ⏳ Запланировано |
| **Displays** | `DisplayBackend` | Mutter DBus (`org.gnome.Mutter.DisplayConfig`) | ⏳ Запланировано |
| **Network** | `NetworkBackend` | NetworkManager (`nmcli` / DBus) | ⏳ Запланировано |
| **Keyboard** | `KeyboardBackend` | GSettings / `localectl` | ⏳ Запланировано |
| **Mouse & Touchpad** | `MouseBackend` | GSettings (`org.gnome.desktop.peripherals`) | ⏳ Запланировано |
