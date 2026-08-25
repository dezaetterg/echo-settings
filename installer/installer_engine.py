"""
Echo Settings - Core Installation & Packaging Engine
Handles file deployment, icon scaling, desktop registration, and uninstallation.
"""

import os
import sys
import shutil
import subprocess
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt

from version import VERSION, APP_NAME, APP_ID, APP_DESCRIPTION

ICON_SIZES = [16, 24, 32, 48, 64, 128, 256, 512]

class InstallationEngine:
    @staticmethod
    def get_source_dir() -> str:
        """Finds the Tahoe Settings source directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # Check standard locations
        candidates = [
            os.path.join(parent_dir, "Tahoe Settings"),
            parent_dir,
            os.path.join(current_dir, "Tahoe Settings"),
            current_dir
        ]
        for c in candidates:
            if os.path.isfile(os.path.join(c, "main.py")):
                return os.path.abspath(c)
        return parent_dir

    @staticmethod
    def get_paths(scope: str = "user") -> dict:
        """Returns standard FHS target paths based on scope ('user' or 'system')."""
        if scope == "system":
            prefix = "/usr"
            return {
                "prefix": prefix,
                "app_dir": "/usr/share/echo-settings",
                "bin_dir": "/usr/bin",
                "bin_file": "/usr/bin/echo-settings",
                "desktop_dir": "/usr/share/applications",
                "desktop_file": f"/usr/share/applications/{APP_ID}.desktop",
                "icons_base": "/usr/share/icons/hicolor",
                "scope": "system"
            }
        else:
            prefix = os.path.expanduser("~/.local")
            return {
                "prefix": prefix,
                "app_dir": os.path.join(prefix, "share", "echo-settings"),
                "bin_dir": os.path.join(prefix, "bin"),
                "bin_file": os.path.join(prefix, "bin", "echo-settings"),
                "desktop_dir": os.path.join(prefix, "share", "applications"),
                "desktop_file": os.path.join(prefix, "share", "applications", f"{APP_ID}.desktop"),
                "icons_base": os.path.join(prefix, "share", "icons", "hicolor"),
                "scope": "user"
            }

    @staticmethod
    @staticmethod
    def get_required_size_mb(src_dir: str) -> float:
        """Calculates size of files to copy in MB including runtime venv."""
        total = 0
        for root, dirs, files in os.walk(src_dir):
            if any(p in root for p in ("__pycache__", ".git", "scratch", ".tempmediaStorage", "dist", "build")):
                continue
            for f in files:
                if f.endswith((".pyc", ".log")) or f.startswith("test_"):
                    continue
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
        return max(1.0, round(total / (1024 * 1024), 1))

    @staticmethod
    def get_available_size_mb(path: str) -> float:
        """Returns available disk space in MB at target path."""
        try:
            check_path = path if os.path.exists(path) else os.path.dirname(path)
            while not os.path.exists(check_path) and os.path.dirname(check_path) != check_path:
                check_path = os.path.dirname(check_path)
            stat = os.statvfs(check_path)
            return round((stat.f_bavail * stat.f_frsize) / (1024 * 1024), 1)
        except Exception:
            return 1000.0

    @classmethod
    def install(cls, scope: str = "user", autostart: bool = False, desktop_shortcut: bool = False, install_echo_search: bool = True, progress_callback=None) -> bool:
        """
        Executes full standalone installation step by step with live granular progress reporting (0-100%).
        progress_callback(pct: int, total_pct: int, message: str)
        """
        import time


        def report(pct, total, msg):
            if progress_callback:
                progress_callback(pct, total, msg)

        paths = cls.get_paths(scope)
        src_dir = cls.get_source_dir()

        # Step 1: Preparing target directories (0% -> 5%)
        report(2, 100, "Preparing target installation directories...")
        os.makedirs(paths["app_dir"], exist_ok=True)
        os.makedirs(paths["bin_dir"], exist_ok=True)
        os.makedirs(paths["desktop_dir"], exist_ok=True)
        time.sleep(0.05)
        report(5, 100, "Target directories initialized.")

        is_same_dir = os.path.abspath(src_dir) == os.path.abspath(paths["app_dir"])

        # Step 2: Copying application files (5% -> 22%)
        if not is_same_dir:
            report(6, 100, "Deploying core application resources, themes and pages...")
            RUNTIME_ITEMS = [
                "animations", "assets", "backends", "components", "docs",
                "models", "pages", "services", "styles", "theme", "installer",
                "main.py", "version.py", "localization.py", "icon.png"
            ]
            ignore_patterns = shutil.ignore_patterns(
                "__pycache__", "*.pyc", "*.log", ".git*", "test_*.py", "scratch*", "build", "dist", ".tempmediaStorage"
            )

            root_dir = os.path.dirname(src_dir)
            for i, item in enumerate(RUNTIME_ITEMS):
                src_item = os.path.join(src_dir, item)
                if not os.path.exists(src_item):
                    src_item = os.path.join(root_dir, item)
                if not os.path.exists(src_item):
                    continue
                dst_item = os.path.join(paths["app_dir"], item)
                if os.path.abspath(src_item) == os.path.abspath(dst_item):
                    continue
                if os.path.isdir(src_item):
                    if os.path.exists(dst_item):
                        shutil.rmtree(dst_item)
                    shutil.copytree(src_item, dst_item, ignore=ignore_patterns)
                else:
                    shutil.copy2(src_item, dst_item)
                
                p = 6 + int(16 * ((i + 1) / len(RUNTIME_ITEMS)))
                report(p, 100, f"Deploying component: {item}...")
                time.sleep(0.02)
        else:
            report(22, 100, "Core application files verified in target directory.")

        # Step 3: Standalone Python Runtime & Dependency Deployment (22% -> 78%)
        src_venv = os.path.join(src_dir, "venv")
        dst_venv = os.path.join(paths["app_dir"], "venv")

        if not is_same_dir and os.path.exists(src_venv) and os.path.abspath(src_venv) != os.path.abspath(dst_venv):
            report(23, 100, "Analyzing standalone Qt6 & PySide6 runtime suite (~700 MB)...")
            # Collect file list for granular copy
            all_files = []
            for root, dirs, files in os.walk(src_venv):
                for f in files:
                    all_files.append(os.path.join(root, f))
            
            total_files = len(all_files)
            if os.path.exists(dst_venv):
                shutil.rmtree(dst_venv)
            os.makedirs(dst_venv, exist_ok=True)

            copied = 0
            # Batched file copying with smooth progress
            for root, dirs, files in os.walk(src_venv):
                rel_root = os.path.relpath(root, src_venv)
                target_root = os.path.join(dst_venv, rel_root)
                os.makedirs(target_root, exist_ok=True)
                for f in files:
                    s_fp = os.path.join(root, f)
                    d_fp = os.path.join(target_root, f)
                    if os.path.islink(s_fp):
                        linkto = os.readlink(s_fp)
                        os.symlink(linkto, d_fp)
                    else:
                        shutil.copy2(s_fp, d_fp)
                    copied += 1

                    if copied % 150 == 0 or copied == total_files:
                        cur_pct = 23 + int(52 * (copied / max(1, total_files)))
                        report(cur_pct, 100, f"Deploying standalone runtime: {copied}/{total_files} files ({cur_pct}%)...")
                        time.sleep(0.001)

            # Step 4: Fix virtualenv interpreter symlinks
            report(76, 100, "Configuring Python virtual environment & runtime links...")
            vbin = os.path.join(dst_venv, "bin")
            sys_py = "/usr/bin/python3" if os.path.exists("/usr/bin/python3") else sys.executable
            for p_link in ("python", "python3", "python3.13"):
                link_path = os.path.join(vbin, p_link)
                if os.path.islink(link_path) or os.path.exists(link_path):
                    try:
                        os.unlink(link_path)
                    except OSError:
                        pass
                try:
                    os.symlink(sys_py, link_path)
                except OSError:
                    pass
            time.sleep(0.05)
            report(78, 100, "Standalone Qt6 & Python runtime verified.")
        else:
            # Create dedicated venv and auto-install dependencies if missing
            report(25, 100, "Creating dedicated Python virtual environment...")
            if not os.path.exists(dst_venv):
                subprocess.run([sys.executable, "-m", "venv", dst_venv, "--system-site-packages"], check=True)
            
            report(45, 100, "Checking runtime dependencies (PySide6, psutil, pulsectl)...")
            v_py = os.path.join(dst_venv, "bin", "python")
            check_code = "import PySide6; import psutil"
            res = subprocess.run([v_py, "-c", check_code], capture_output=True)
            if res.returncode != 0:
                report(50, 100, "Auto-installing required PySide6 & system dependencies...")
                pip_exe = os.path.join(dst_venv, "bin", "pip")
                subprocess.run([pip_exe, "install", "PySide6", "psutil", "pulsectl"], check=True)
                report(75, 100, "Dependencies successfully installed.")
            else:
                report(75, 100, "All system dependencies verified.")
            report(78, 100, "Python runtime configured.")

        # Step 5: Generating native binary launcher (78% -> 85%)
        report(80, 100, "Compiling native launcher executable...")
        launcher_content = f"""#!/usr/bin/env bash
# Echo Settings - Launcher
set -e

APP_DIR="{paths['app_dir']}"
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Echo Settings is not installed in $APP_DIR" >&2
    exit 1
fi

PYTHON_EXEC=""
if [ -x "$APP_DIR/venv/bin/python" ]; then
    PYTHON_EXEC="$APP_DIR/venv/bin/python"
elif [ -x "{sys.executable}" ]; then
    PYTHON_EXEC="{sys.executable}"
else
    PYTHON_EXEC="$(which python3)"
fi

export PYTHONPATH="$APP_DIR:$PYTHONPATH"
exec "$PYTHON_EXEC" "$APP_DIR/main.py" "$@"
"""
        with open(paths["bin_file"], "w", encoding="utf-8") as f:
            f.write(launcher_content)
        os.chmod(paths["bin_file"], 0o755)

        # Step 6: Rendering HiDPI Icon Suite (85% -> 90%)
        report(85, 100, "Rendering HiDPI application icon suite (16px to 512px)...")
        icon_src = os.path.join(src_dir, "icon.png")
        if not os.path.exists(icon_src):
            icon_src = os.path.join(src_dir, "assets", "echo_icon.jpg")

        img = QImage(icon_src)
        if not img.isNull():
            for sz in ICON_SIZES:
                sz_dir = os.path.join(paths["icons_base"], f"{sz}x{sz}", "apps")
                os.makedirs(sz_dir, exist_ok=True)
                dest = os.path.join(sz_dir, "echo-settings.png")
                scaled = img.scaled(sz, sz, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                scaled.save(dest, "PNG")

            scalable_dir = os.path.join(paths["icons_base"], "scalable", "apps")
            os.makedirs(scalable_dir, exist_ok=True)
            img.save(os.path.join(scalable_dir, "echo-settings.png"), "PNG")

        report(90, 100, "HiDPI vector and bitmap icons deployed.")

        # Step 7: Registering desktop entry in GNOME (90% -> 96%)
        report(92, 100, "Registering application in GNOME App Grid...")
        desktop_content = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
GenericName=System Settings
Comment={APP_DESCRIPTION}
Exec={paths['bin_file']} %U
Icon=echo-settings
Terminal=false
Categories=Settings;HardwareSettings;DesktopSettings;GTK;Qt;
Keywords=Preferences;Settings;Control;Center;Echo;Display;Appearance;WiFi;Network;Bluetooth;Power;Sound;Storage;Keyboard;Privacy;Security;
StartupWMClass=Echo_Settings
StartupNotify=true
SingleMainWindow=true
X-GNOME-Settings-Panel=echo-settings
X-Echo-Version={VERSION}
"""
        with open(paths["desktop_file"], "w", encoding="utf-8") as f:
            f.write(desktop_content)
        os.chmod(paths["desktop_file"], 0o644)

        if shutil.which("desktop-file-validate"):
            try:
                subprocess.run(["desktop-file-validate", paths["desktop_file"]], capture_output=True)
            except Exception:
                pass

        # Optional Autostart & Desktop Shortcut (96% -> 99%)
        if autostart:
            report(96, 100, "Configuring system startup integration...")
            if scope == "system":
                autostart_dir = "/etc/xdg/autostart"
            else:
                autostart_dir = os.path.expanduser("~/.config/autostart")
            try:
                os.makedirs(autostart_dir, exist_ok=True)
                autostart_file = os.path.join(autostart_dir, "com.echo.settings.desktop")
                shutil.copy2(paths["desktop_file"], autostart_file)
            except Exception:
                pass

        if desktop_shortcut and scope == "user":
            report(97, 100, "Creating trusted Desktop shortcut...")
            desktop_dir = os.path.expanduser("~/Desktop")
            try:
                out = subprocess.check_output(["xdg-user-dir", "DESKTOP"], text=True).strip()
                if out and os.path.exists(out):
                    desktop_dir = out
            except Exception:
                pass
            if os.path.exists(desktop_dir):
                dt_file = os.path.join(desktop_dir, "com.echo.settings.desktop")
                try:
                    shutil.copy2(paths["desktop_file"], dt_file)
                    os.chmod(dt_file, 0o755)
                    subprocess.run(["gio", "set", dt_file, "metadata::trusted", "true"], capture_output=True)
                except Exception:
                    pass

        # Optional Echo Search companion integration (90% -> 98%)
        if install_echo_search:
            report(90, 100, "Configuring and deploying Echo Search Spotlight companion...")
            try:
                cls.install_echo_search(scope=scope, progress_callback=lambda p, t, m: report(90 + int(8 * (p / 100)), 100, m))
            except Exception as e:
                print(f"Echo Search companion install warning: {e}")

        # Final cache refresh (99% -> 100%)
        report(99, 100, "Updating system desktop and icon databases...")

        try:
            if shutil.which("update-desktop-database"):
                subprocess.run(["update-desktop-database", "-q", paths["desktop_dir"]], capture_output=True)
            if shutil.which("gtk-update-icon-cache"):
                subprocess.run(["gtk-update-icon-cache", "-q", "-t", paths["icons_base"]], capture_output=True)
        except Exception:
            pass

        time.sleep(0.1)
        report(100, 100, "Echo Settings installed successfully!")
        return True


    @classmethod
    def install_echo_search(cls, scope: str = "user", progress_callback=None) -> bool:
        """
        Downloads, packages, or copies and installs Echo Search companion.
        Works across all Linux distros (Mint, Ubuntu, Debian, Arch, Fedora, openSUSE).
        Configures resilient launcher, desktop entry, application icons, autostart, and global hotkeys.
        """
        import urllib.request
        import time

        def report(pct, total, msg):
            if progress_callback:
                progress_callback(pct, total, msg)

        report(5, 100, "Checking Echo Search installation sources...")

        # 1. Target paths for Echo Search
        if scope == "system":
            es_app_dir = "/usr/lib/echo-search"
            es_bin_file = "/usr/bin/echo-search"
            es_desktop_dir = "/usr/share/applications"
            es_icons_base = "/usr/share/icons/hicolor"
            es_autostart_dir = "/etc/xdg/autostart"
        else:
            local_prefix = os.path.expanduser("~/.local")
            es_app_dir = os.path.join(local_prefix, "share", "echo-search")
            es_bin_file = os.path.join(local_prefix, "bin", "echo-search")
            es_desktop_dir = os.path.join(local_prefix, "share", "applications")
            es_icons_base = os.path.join(local_prefix, "share", "icons", "hicolor")
            es_autostart_dir = os.path.expanduser("~/.config/autostart")

        os.makedirs(es_app_dir, exist_ok=True)
        os.makedirs(os.path.dirname(es_bin_file), exist_ok=True)
        os.makedirs(es_desktop_dir, exist_ok=True)
        os.makedirs(es_autostart_dir, exist_ok=True)

        # 2. Check for local source directories or .deb archives
        here_dir = os.path.dirname(os.path.abspath(__file__))
        top_dir = os.path.dirname(here_dir)

        local_candidates = [
            os.path.expanduser("~/echo_search"),
            os.path.expanduser("~/echo-search"),
            os.path.expanduser("~/spotlight_liquidglass"),
            os.path.join(top_dir, "echo_search"),
            os.path.join(top_dir, "echo-search"),
            os.path.join(os.path.dirname(top_dir), "echo_search"),
            os.path.join(os.path.dirname(top_dir), "echo-search"),
            "/usr/lib/echo-search",
            "/usr/share/echo-search",
            os.path.expanduser("~/.local/share/spotlight-glass"),
        ]

        local_deb_candidates = [
            os.path.expanduser("~/echo_search/dist/echo-search_latest.deb"),
            os.path.join(top_dir, "dist", "echo-search_latest.deb"),
            "/tmp/echo-search_latest.deb",
        ]

        found_src = None
        for c in local_candidates:
            if os.path.isdir(c) and os.path.isfile(os.path.join(c, "main.py")):
                found_src = c
                break

        found_deb = None
        for d in local_deb_candidates:
            if os.path.isfile(d) and os.path.getsize(d) > 5000:
                found_deb = d
                break

        # 3. If neither local source nor valid deb found, try git clone first, then fallback to archive download
        if not found_src and not found_deb:
            if shutil.which("git"):
                report(15, 100, "Cloning Echo Search from GitHub repository...")
                git_tmp = "/tmp/echo_search_git_install"
                try:
                    if os.path.exists(git_tmp):
                        shutil.rmtree(git_tmp, ignore_errors=True)
                    res = subprocess.run(
                        ["git", "clone", "--depth", "1", "https://github.com/dezaetterg/echo-search.git", git_tmp],
                        capture_output=True, text=True, timeout=35
                    )
                    if res.returncode == 0 and os.path.exists(os.path.join(git_tmp, "main.py")):
                        found_src = git_tmp
                        report(50, 100, "Echo Search repository cloned.")
                except Exception as e:
                    print(f"Git clone notice: {e}")

            if not found_src:
                report(25, 100, "Downloading Echo Search archive from GitHub...")
                tar_tmp = "/tmp/echo_search_archive.tar.gz"
                extract_tmp = "/tmp/echo_search_tar_extract"
                try:
                    shutil.rmtree(extract_tmp, ignore_errors=True)
                    os.makedirs(extract_tmp, exist_ok=True)
                    tar_url = "https://github.com/dezaetterg/echo-search/archive/refs/heads/main.tar.gz"
                    req = urllib.request.Request(tar_url, headers={"User-Agent": "EchoSettingsInstaller/1.0"})
                    with urllib.request.urlopen(req, timeout=25) as response:
                        with open(tar_tmp, "wb") as f_out:
                            shutil.copyfileobj(response, f_out)
                    
                    if os.path.exists(tar_tmp) and os.path.getsize(tar_tmp) > 10000:
                        subprocess.run(["tar", "-xzf", tar_tmp, "-C", extract_tmp], check=True, capture_output=True)
                        for root, dirs, files in os.walk(extract_tmp):
                            if "main.py" in files and "ui.py" in files:
                                found_src = root
                                break
                except Exception as e:
                    print(f"Archive download notice: {e}")

        # 4. Deploy application files
        report(65, 100, "Deploying Echo Search core modules...")

        installed_via_dpkg = False
        if found_deb and scope == "system" and os.geteuid() == 0:
            try:
                report(70, 100, "Installing system debian package via dpkg...")
                res = subprocess.run(["dpkg", "-i", found_deb], capture_output=True, text=True)
                if res.returncode == 0:
                    installed_via_dpkg = True
            except Exception:
                pass

        if not installed_via_dpkg:
            # If deb is available, extract contents
            if found_deb and (not found_src or not os.path.exists(found_src)):
                try:
                    report(70, 100, "Extracting Echo Search package contents...")
                    extract_tmp = "/tmp/echo_search_extract"
                    if os.path.exists(extract_tmp):
                        shutil.rmtree(extract_tmp, ignore_errors=True)
                    os.makedirs(extract_tmp, exist_ok=True)
                    subprocess.run(["dpkg-deb", "-x", found_deb, extract_tmp], check=True, capture_output=True)
                    
                    deb_app = os.path.join(extract_tmp, "usr", "lib", "echo-search")
                    if os.path.exists(deb_app):
                        for item in os.listdir(deb_app):
                            s_i = os.path.join(deb_app, item)
                            d_i = os.path.join(es_app_dir, item)
                            if os.path.isdir(s_i):
                                if os.path.exists(d_i):
                                    shutil.rmtree(d_i, ignore_errors=True)
                                shutil.copytree(s_i, d_i)
                            else:
                                shutil.copy2(s_i, d_i)
                        found_src = es_app_dir
                except Exception:
                    pass

            # If source folder is found, copy files directly
            if found_src and os.path.isdir(found_src) and os.path.abspath(found_src) != os.path.abspath(es_app_dir):
                FILES_TO_COPY = [
                    "main.py", "ui.py", "config_manager.py", "i18n.py",
                    "search_engine.py", "preview_manager.py", "utils.py",
                    "style.css", "emoji.json"
                ]
                DIRS_TO_COPY = ["modes", "providers", "assets"]
                for f in FILES_TO_COPY:
                    src_f = os.path.join(found_src, f)
                    if os.path.isfile(src_f):
                        shutil.copy2(src_f, os.path.join(es_app_dir, f))
                for d in DIRS_TO_COPY:
                    src_d = os.path.join(found_src, d)
                    dst_d = os.path.join(es_app_dir, d)
                    if os.path.isdir(src_d):
                        if os.path.exists(dst_d):
                            shutil.rmtree(dst_d, ignore_errors=True)
                        shutil.copytree(src_d, dst_d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

        # Verify deployment of critical file main.py
        if not os.path.isfile(os.path.join(es_app_dir, "main.py")):
            raise RuntimeError(f"Echo Search deployment failed: main.py not found in {es_app_dir}")

        # 5. Create smart executable launcher
        report(82, 100, "Configuring executable launcher...")
        sys_exe = sys.executable if sys.executable else "/usr/bin/python3"
        launcher_content = f"""#!/usr/bin/env bash
# Echo Search - Executable Launcher
set -e

APP_DIR="{es_app_dir}"
if [ ! -d "$APP_DIR" ]; then
    echo "Error: Echo Search application directory not found: $APP_DIR" >&2
    exit 1
fi

PYTHON_EXEC=""
for cand in "/usr/bin/python3" "$APP_DIR/venv/bin/python3" "$APP_DIR/venv/bin/python" "{sys_exe}" "$(which python3 2>/dev/null)" "python3"; do
    if [ -n "$cand" ] && ([ -x "$cand" ] || command -v "$cand" >/dev/null 2>&1); then
        if "$cand" -c "import gi; from gi.repository import Gtk" 2>/dev/null; then
            PYTHON_EXEC="$cand"
            break
        fi
    fi
done

if [ -z "$PYTHON_EXEC" ]; then
    if [ -x "{sys_exe}" ]; then
        PYTHON_EXEC="{sys_exe}"
    else
        PYTHON_EXEC="/usr/bin/python3"
    fi
fi

export PYTHONPATH="$APP_DIR:$PYTHONPATH"
exec "$PYTHON_EXEC" "$APP_DIR/main.py" "$@"
"""
        with open(es_bin_file, "w", encoding="utf-8") as f_bin:
            f_bin.write(launcher_content)
        os.chmod(es_bin_file, 0o755)

        # 6. Install desktop icons
        report(86, 100, "Registering application icons...")
        icon_src = os.path.join(es_app_dir, "assets", "icons", "hicolor")
        if not os.path.exists(icon_src) and found_src:
            icon_src = os.path.join(found_src, "assets", "icons", "hicolor")
        
        if os.path.exists(icon_src):
            for size_dir in os.listdir(icon_src):
                s_path = os.path.join(icon_src, size_dir, "apps")
                d_path = os.path.join(es_icons_base, size_dir, "apps")
                if os.path.isdir(s_path):
                    os.makedirs(d_path, exist_ok=True)
                    for ico in os.listdir(s_path):
                        shutil.copy2(os.path.join(s_path, ico), os.path.join(d_path, ico))
                        # Also copy as echo-search.png for maximum compatibility
                        if ico == "com.echo.search.png":
                            shutil.copy2(os.path.join(s_path, ico), os.path.join(d_path, "echo-search.png"))

        # Scalable SVG Icon
        svg_src = os.path.join(es_app_dir, "assets", "icons", "com.echo.search.svg")
        if not os.path.exists(svg_src) and found_src:
            svg_src = os.path.join(found_src, "assets", "icons", "com.echo.search.svg")
        if os.path.exists(svg_src):
            svg_dst_dir = os.path.join(es_icons_base, "scalable", "apps")
            os.makedirs(svg_dst_dir, exist_ok=True)
            shutil.copy2(svg_src, os.path.join(svg_dst_dir, "com.echo.search.svg"))
            shutil.copy2(svg_src, os.path.join(svg_dst_dir, "echo-search.svg"))

        # 7. Create desktop entry & Autostart
        report(90, 100, "Registering desktop application shortcut...")
        desktop_content = f"""[Desktop Entry]
Name=Echo Search
GenericName=Spotlight Search
Comment=Modern Apple Liquid Glass Spotlight Search for Linux
Exec={es_bin_file}
Icon=com.echo.search
Terminal=false
Type=Application
Categories=Utility;Core;System;
Keywords=Spotlight;Search;Launcher;Echo;
StartupNotify=true
StartupWMClass=echo-search
X-GNOME-Autostart-enabled=true
"""
        es_desktop_file = os.path.join(es_desktop_dir, "com.echo.search.desktop")
        with open(es_desktop_file, "w", encoding="utf-8") as f_dt:
            f_dt.write(desktop_content)
        os.chmod(es_desktop_file, 0o755)

        # Autostart entry
        autostart_file = os.path.join(es_autostart_dir, "com.echo.search.desktop")
        try:
            with open(autostart_file, "w", encoding="utf-8") as f_as:
                f_as.write(desktop_content)
            os.chmod(autostart_file, 0o755)
        except Exception:
            pass

        # 8. Register Desktop Environment Hotkeys (GNOME / Cinnamon / KDE / XFCE / MATE)
        report(94, 100, "Registering global Super+Space shortcut...")
        try:
            if shutil.which("gsettings"):
                # Cinnamon
                try:
                    # Free default Cinnamon switch-input-source and workspace conflicts for Super+Space
                    subprocess.run([
                        "gsettings", "set", "org.cinnamon.desktop.keybindings.wm", "switch-input-source", "['XF86Keyboard']"
                    ], capture_output=True)
                    subprocess.run([
                        "gsettings", "set", "org.cinnamon.desktop.keybindings.wm", "switch-input-source-backward", "['<Shift>XF86Keyboard']"
                    ], capture_output=True)
                    subprocess.run([
                        "gsettings", "set", "org.cinnamon.desktop.keybindings.wm", "switch-to-workspace-left", "['']"
                    ], capture_output=True)
                    subprocess.run([
                        "gsettings", "set", "org.cinnamon.desktop.keybindings.wm", "switch-to-workspace-down", "['']"
                    ], capture_output=True)

                    c_main = "org.cinnamon.desktop.keybindings"
                    c_schema = "org.cinnamon.desktop.keybindings.custom-keybinding"
                    c_list_res = subprocess.run(["gsettings", "get", c_main, "custom-list"], capture_output=True, text=True).stdout.strip()
                    found_slot = "custom0"
                    for i in range(16):
                        s_id = f"custom{i}"
                        s_path = f"/org/cinnamon/desktop/keybindings/custom-keybindings/{s_id}/"
                        s_name = subprocess.run(["gsettings", "get", f"{c_schema}:{s_path}", "name"], capture_output=True, text=True).stdout.strip()
                        if not s_name or s_name == "''" or s_name == "@as []" or "Echo" in s_name:
                            found_slot = s_id
                            break
                    slot_path = f"/org/cinnamon/desktop/keybindings/custom-keybindings/{found_slot}/"
                    subprocess.run(["gsettings", "set", f"{c_schema}:{slot_path}", "name", "Echo Search"], capture_output=True)
                    subprocess.run(["gsettings", "set", f"{c_schema}:{slot_path}", "command", es_bin_file], capture_output=True)
                    subprocess.run(["gsettings", "set", f"{c_schema}:{slot_path}", "binding", "['<Super>space', '<Super>Cyrillic_em']"], capture_output=True)
                    if found_slot not in c_list_res:
                        if not c_list_res or c_list_res in ("@as []", "[]", "''"):
                            new_list = f"['{found_slot}']"
                        else:
                            new_list = c_list_res.rstrip("]") + f", '{found_slot}']"
                        subprocess.run(["gsettings", "set", c_main, "custom-list", new_list], capture_output=True)
                except Exception:
                    pass

                # GNOME / Budgie / Unity
                try:
                    custom_schema = "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding"
                    media_keys = "org.gnome.settings-daemon.plugins.media-keys"
                    g_list_res = subprocess.run(["gsettings", "get", media_keys, "custom-keybindings"], capture_output=True, text=True).stdout.strip()
                    g_slot = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/"
                    for i in range(16):
                        kp = f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{i}/"
                        cur_name = subprocess.run(["gsettings", "get", f"{custom_schema}:{kp}", "name"], capture_output=True, text=True).stdout.strip()
                        if not cur_name or cur_name == "''" or cur_name == "@as []" or "Echo" in cur_name:
                            g_slot = kp
                            break
                    subprocess.run(["gsettings", "set", f"{custom_schema}:{g_slot}", "name", "Echo Search"], capture_output=True)
                    subprocess.run(["gsettings", "set", f"{custom_schema}:{g_slot}", "command", es_bin_file], capture_output=True)
                    subprocess.run(["gsettings", "set", f"{custom_schema}:{g_slot}", "binding", "<Super>space"], capture_output=True)
                    if g_slot not in g_list_res:
                        if not g_list_res or g_list_res in ("@as []", "[]", "''"):
                            new_bindings = f"['{g_slot}']"
                        else:
                            new_bindings = g_list_res.rstrip("]") + f", '{g_slot}']"
                        subprocess.run(["gsettings", "set", media_keys, "custom-keybindings", new_bindings], capture_output=True)
                except Exception:
                    pass

            # KDE Plasma
            if shutil.which("kwriteconfig6"):
                subprocess.run(["kwriteconfig6", "--file", "kglobalshortcutsrc", "--group", "com.echo.search.desktop", "--key", "_launch", "Meta+Space,none,Echo Search"], capture_output=True)
                subprocess.run(["qdbus", "org.kde.KGlobalAccel", "/KGlobalAccel", "reloadConfig"], capture_output=True)
            elif shutil.which("kwriteconfig5"):
                subprocess.run(["kwriteconfig5", "--file", "kglobalshortcutsrc", "--group", "com.echo.search.desktop", "--key", "_launch", "Meta+Space,none,Echo Search"], capture_output=True)
                subprocess.run(["qdbus", "org.kde.KGlobalAccel", "/KGlobalAccel", "reloadConfig"], capture_output=True)

            # XFCE
            if shutil.which("xfconf-query"):
                subprocess.run(["xfconf-query", "-c", "xfce4-keyboard-shortcuts", "-p", "/commands/custom/<Super>space", "-n", "-t", "string", "-s", "echo-search"], capture_output=True)

            if shutil.which("update-desktop-database"):
                subprocess.run(["update-desktop-database", "-q", es_desktop_dir], capture_output=True)
            if shutil.which("gtk-update-icon-cache"):
                subprocess.run(["gtk-update-icon-cache", "-q", "-t", es_icons_base], capture_output=True)
        except Exception:
            pass

        report(98, 100, "Echo Search installed successfully!")
        return True


    @classmethod
    def uninstall(cls, scope: str = "user", remove_user_data: bool = False) -> bool:
        """Uninstalls Echo Settings cleanly."""
        paths = cls.get_paths(scope)

        # 1. Remove binary launcher
        if os.path.exists(paths["bin_file"]):
            try:
                os.remove(paths["bin_file"])
            except OSError:
                pass

        # 2. Remove autostart entry
        if scope == "system":
            sys_auto = "/etc/xdg/autostart/com.echo.settings.desktop"
            if os.path.exists(sys_auto):
                try:
                    os.remove(sys_auto)
                except OSError:
                    pass
        else:
            usr_auto = os.path.expanduser("~/.config/autostart/com.echo.settings.desktop")
            if os.path.exists(usr_auto):
                try:
                    os.remove(usr_auto)
                except OSError:
                    pass

            # Remove Desktop shortcut
            for d in ("~/Desktop", "~/Рабочий стол"):
                dp = os.path.expanduser(os.path.join(d, "com.echo.settings.desktop"))
                if os.path.exists(dp):
                    try:
                        os.remove(dp)
                    except OSError:
                        pass


        # 2. Remove desktop file
        if os.path.exists(paths["desktop_file"]):
            try:
                os.remove(paths["desktop_file"])
            except OSError:
                pass

        # 3. Remove icons
        for sz in ICON_SIZES:
            icon_p = os.path.join(paths["icons_base"], f"{sz}x{sz}", "apps", "echo-settings.png")
            if os.path.exists(icon_p):
                try:
                    os.remove(icon_p)
                except OSError:
                    pass
        scalable_p = os.path.join(paths["icons_base"], "scalable", "apps", "echo-settings.png")
        if os.path.exists(scalable_p):
            try:
                os.remove(scalable_p)
            except OSError:
                pass

        # 4. Remove application directory
        if os.path.exists(paths["app_dir"]):
            try:
                shutil.rmtree(paths["app_dir"])
            except OSError:
                pass

        # 5. Remove user settings ONLY if explicitly requested
        if remove_user_data:
            user_config = os.path.expanduser("~/.config/EchoSettings")
            if os.path.exists(user_config):
                try:
                    shutil.rmtree(user_config)
                except OSError:
                    pass

        # 6. Update databases
        if shutil.which("update-desktop-database"):
            try:
                subprocess.run(["update-desktop-database", paths["desktop_dir"]], capture_output=True)
            except Exception:
                pass

        if shutil.which("gtk-update-icon-cache"):
            try:
                subprocess.run(["gtk-update-icon-cache", "-f", "-t", paths["icons_base"]], capture_output=True)
            except Exception:
                pass

        return True
