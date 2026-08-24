Name:           echo-settings
Version:        1.0.3
Release:        1%{?dist}
Summary:        Modern Liquid Glass System Control Center for Linux
License:        GPL-3.0-or-later
URL:            https://github.com/dezaetterg/echo-settings
BuildArch:      noarch

Requires:       python3 >= 3.10
Requires:       python3-pyside6
Requires:       python3-psutil

Recommends:     NetworkManager
Recommends:     bluez
Recommends:     wireplumber
Recommends:     brightnessctl

%description
Echo Settings is an elegant, modular system control center built with Qt6/PySide6.
Provides native controls for Appearance, Display, Network, Sound, Power,
Privacy, Storage, Bluetooth, Keyboard, and Echo Search launcher configuration.

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/echo-settings
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/licenses/echo-settings
mkdir -p %{buildroot}%{_docdir}/echo-settings

for sz in 16 32 48 64 128 256 512; do
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${sz}x${sz}/apps
done

# Copy application files
cp -rp %{_sourcedir}/assets %{buildroot}%{_datadir}/echo-settings/
cp -rp %{_sourcedir}/backends %{buildroot}%{_datadir}/echo-settings/
cp -rp %{_sourcedir}/components %{buildroot}%{_datadir}/echo-settings/
cp -rp %{_sourcedir}/models %{buildroot}%{_datadir}/echo-settings/
cp -rp %{_sourcedir}/pages %{buildroot}%{_datadir}/echo-settings/
cp -rp %{_sourcedir}/services %{buildroot}%{_datadir}/echo-settings/
cp -rp %{_sourcedir}/styles %{buildroot}%{_datadir}/echo-settings/
cp -rp %{_sourcedir}/theme %{buildroot}%{_datadir}/echo-settings/
cp -rp %{_sourcedir}/installer %{buildroot}%{_datadir}/echo-settings/
cp -p %{_sourcedir}/*.py %{buildroot}%{_datadir}/echo-settings/

# Clean pycache if any
find %{buildroot}%{_datadir}/echo-settings -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find %{buildroot}%{_datadir}/echo-settings -name "*.pyc" -delete 2>/dev/null || true

# Launcher wrapper
cat << 'BIN_EOF' > %{buildroot}%{_bindir}/echo-settings
#!/usr/bin/env bash
export PYTHONPATH="/usr/share/echo-settings:$PYTHONPATH"
exec python3 /usr/share/echo-settings/main.py "$@"
BIN_EOF
chmod 755 %{buildroot}%{_bindir}/echo-settings

# Desktop entry
cat << 'DESK_EOF' > %{buildroot}%{_datadir}/applications/echo-settings.desktop
[Desktop Entry]
Type=Application
Name=Echo Settings
GenericName=System Settings
Comment=Modern System Control Center for Linux
Exec=/usr/bin/echo-settings %U
Icon=echo-settings
Terminal=false
Categories=Settings;HardwareSettings;DesktopSettings;Qt;
Keywords=Preferences;Settings;Control;Center;Echo;Display;Appearance;WiFi;Network;Bluetooth;Power;Sound;Storage;Keyboard;
StartupWMClass=Echo_Settings
StartupNotify=true
SingleMainWindow=true
DESK_EOF
chmod 644 %{buildroot}%{_datadir}/applications/echo-settings.desktop

# Icons
if [ -f %{_sourcedir}/icon.png ]; then
    cp -p %{_sourcedir}/icon.png %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/echo-settings.png
    for sz in 16 32 48 64 128 256 512; do
        cp -p %{_sourcedir}/icon.png %{buildroot}%{_datadir}/icons/hicolor/${sz}x${sz}/apps/echo-settings.png
    done
fi

# License & Docs
cp -p %{_sourcedir}/LICENSE %{buildroot}%{_datadir}/licenses/echo-settings/LICENSE
cp -p %{_sourcedir}/LICENSE %{buildroot}%{_docdir}/echo-settings/copyright
cp -p %{_sourcedir}/README.md %{buildroot}%{_docdir}/echo-settings/README.md

%files
%{_bindir}/echo-settings
%{_datadir}/echo-settings
%{_datadir}/applications/echo-settings.desktop
%{_datadir}/icons/hicolor/*/apps/echo-settings.png
%{_datadir}/licenses/echo-settings/LICENSE
%{_docdir}/echo-settings/README.md
%{_docdir}/echo-settings/copyright

%post
if [ $1 -eq 1 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
fi
/usr/bin/update-desktop-database &> /dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
/usr/bin/update-desktop-database &> /dev/null || :

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%changelog
* Mon Aug 24 2026 Echo Contributors <https://github.com/dezaetterg/echo-settings> - 1.0.2-1
- Release 1.0.2 with welcome installer self-deletion fix and multi-distro support
