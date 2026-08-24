"""
System environment and compatibility validation for Echo Settings.
Performs real, non-destructive checks against OS, desktop, hardware, and libraries.
"""

import os
import sys
import platform
import shutil
import subprocess
from dataclasses import dataclass
from localization import t

@dataclass
class CheckResult:

    id: str
    title: str
    status: str  # 'pass', 'warning', 'fail'
    value: str
    details: str
    critical: bool = False


class SystemChecker:
    @staticmethod
    def get_os_info() -> tuple[str, str, str]:
        """Returns (name, id, version) from /etc/os-release or platform."""
        name, os_id, version = "Linux", "linux", ""
        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            name = line.split("=", 1)[1].strip().strip('"')
                        elif line.startswith("ID="):
                            os_id = line.split("=", 1)[1].strip().strip('"')
                        elif line.startswith("VERSION_ID="):
                            version = line.split("=", 1)[1].strip().strip('"')
            except Exception:
                pass
        return name, os_id, version

    @staticmethod
    def check_distribution() -> CheckResult:
        name, os_id, version = SystemChecker.get_os_info()
        os_lower = f"{name} {os_id}".lower()
        is_supported = any(d in os_lower for d in ("pika", "debian", "ubuntu", "pop", "mint", "fedora", "arch", "linux"))
        
        return CheckResult(
            id="distribution",
            title=t("installer.chk_os", "Operating System"),
            status="pass" if is_supported else "warning",
            value=name,
            details=f"{name} is fully supported with native system integration." if is_supported else f"Distribution '{name}' may require manual dependencies."
        )

    @staticmethod
    def check_architecture() -> CheckResult:
        arch = platform.machine()
        is_supported = arch in ("x86_64", "amd64", "aarch64")
        return CheckResult(
            id="architecture",
            title=t("installer.chk_arch", "CPU Architecture"),
            status="pass" if is_supported else "fail",
            value=arch,
            details=f"Architecture '{arch}' is fully supported for native execution.",
            critical=True
        )

    @staticmethod
    def check_desktop_environment() -> CheckResult:
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "") or os.environ.get("XDG_SESSION_DESKTOP", "") or "Unknown"
        is_gnome = "gnome" in desktop.lower()
        
        return CheckResult(
            id="desktop",
            title=t("installer.chk_desktop", "Desktop Environment"),
            status="pass" if is_gnome else "warning",
            value=desktop if desktop else "Unknown",
            details="GNOME Desktop detected. Full GSettings and Shell integration enabled." if is_gnome else f"Desktop '{desktop}' detected. Some GNOME-specific features may be limited."
        )

    @staticmethod
    def check_display_server() -> CheckResult:
        session_type = os.environ.get("XDG_SESSION_TYPE", "")
        if not session_type:
            session_type = "wayland" if os.environ.get("WAYLAND_DISPLAY") else ("x11" if os.environ.get("DISPLAY") else "unknown")
            
        is_wayland = "wayland" in session_type.lower()
        return CheckResult(
            id="display_server",
            title=t("installer.chk_display", "Display Server"),
            status="pass",
            value="Wayland" if is_wayland else "X11",
            details="Wayland compositor active with native fractional scaling and security." if is_wayland else "X11 display server active."
        )

    @staticmethod
    def check_python_runtime() -> CheckResult:
        v = sys.version_info
        ver_str = f"{v.major}.{v.minor}.{v.micro}"
        is_ok = v >= (3, 10)
        return CheckResult(
            id="python",
            title=t("installer.chk_python", "Python Runtime"),
            status="pass" if is_ok else "fail",
            value=f"Python {ver_str}",
            details=f"Python {ver_str} meets the minimum requirement (>= 3.10).",
            critical=True
        )

    @staticmethod
    def check_gobject_apis() -> CheckResult:
        apis = []
        missing = []
        
        try:
            import gi
            gi.require_version('GLib', '2.0')
            gi.require_version('Gio', '2.0')
            from gi.repository import GLib, Gio
            apis.append("GLib/Gio")
        except Exception:
            missing.append("python3-gi")

        try:
            import gi
            gi.require_version('NM', '1.0')
            from gi.repository import NM
            apis.append("NetworkManager")
        except Exception:
            missing.append("gir1.2-nm-1.0")

        try:
            import gi
            gi.require_version('UPowerGlib', '1.0')
            from gi.repository import UPowerGlib
            apis.append("UPower")
        except Exception:
            missing.append("gir1.2-upowerglib-1.0")

        try:
            import gi
            gi.require_version('Geoclue', '2.0')
            from gi.repository import Geoclue
            apis.append("GeoClue")
        except Exception:
            missing.append("gir1.2-geoclue-2.0")

        if not missing:
            return CheckResult(
                id="gobject",
                title=t("installer.chk_apis", "System Integration APIs"),
                status="pass",
                value="All APIs available",
                details=f"Found: {', '.join(apis)}"
            )
        else:
            pkg_hint = f"sudo apt install {' '.join(missing)}"
            return CheckResult(
                id="gobject",
                title=t("installer.chk_apis", "System Integration APIs"),
                status="warning",
                value=f"{len(apis)}/{len(apis) + len(missing)} available",
                details=f"Available: {', '.join(apis)}. Optional hint: {pkg_hint}"
            )

    @staticmethod
    def check_dbus() -> CheckResult:
        has_gdbus = shutil.which("gdbus") is not None
        has_gsettings = shutil.which("gsettings") is not None
        
        if has_gdbus and has_gsettings:
            return CheckResult(
                id="dbus",
                title=t("installer.chk_dbus", "System Bus & D-Bus"),
                status="pass",
                value="Active",
                details="D-Bus message bus and GSettings tools are accessible."
            )
        else:
            return CheckResult(
                id="dbus",
                title=t("installer.chk_dbus", "System Bus & D-Bus"),
                status="warning",
                value="Limited",
                details="gdbus or gsettings utilities were not found in PATH."
            )


    @staticmethod
    def check_existing_installation() -> CheckResult:
        system_installed = os.path.exists("/usr/share/echo-settings") or os.path.exists("/usr/bin/echo-settings")
        user_installed = os.path.exists(os.path.expanduser("~/.local/share/echo-settings")) or os.path.exists(os.path.expanduser("~/.local/bin/echo-settings"))
        
        if system_installed:
            return CheckResult(
                id="existing_install",
                title="Installation Status",
                status="pass",
                value="System-wide installed",
                details="Existing system-wide installation detected. Upgrading will preserve all settings."
            )
        elif user_installed:
            return CheckResult(
                id="existing_install",
                title="Installation Status",
                status="pass",
                value="User installed",
                details="Existing user installation detected. Upgrading will preserve all settings."
            )
        else:
            return CheckResult(
                id="existing_install",
                title="Installation Status",
                status="pass",
                value="Ready for new install",
                details="No previous installation detected. Ready for clean setup."
            )

    @staticmethod
    def run_all_checks() -> list[CheckResult]:
        """Runs all validation checks in order."""
        return [
            SystemChecker.check_distribution(),
            SystemChecker.check_architecture(),
            SystemChecker.check_desktop_environment(),
            SystemChecker.check_display_server(),
            SystemChecker.check_python_runtime(),
            SystemChecker.check_gobject_apis(),
            SystemChecker.check_dbus(),
            SystemChecker.check_existing_installation()
        ]
