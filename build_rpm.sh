#!/bin/bash
set -e

# ==============================================================================
# Echo Settings - RPM Package Builder (.rpm)
# Compatible with Fedora, RHEL, CentOS, AlmaLinux, Rocky Linux, openSUSE
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VERSION=$(grep -m1 '^Version:' echo-settings.spec | awk '{print $2}')
RELEASE=$(grep -m1 '^Release:' echo-settings.spec | awk '{print $2}' | sed 's/%{?dist}//')
RPM_TOPDIR="$SCRIPT_DIR/build/rpm_tree"

echo "=========================================="
echo "📦 Сборка RPM-пакета: echo-settings v${VERSION}"
echo "=========================================="

if ! command -v rpmbuild &>/dev/null; then
    echo "⚠ Предупреждение: rpmbuild не установлен в системе."
    echo "  Установите: sudo dnf install rpm-build (Fedora) или sudo apt install rpm (Debian/Ubuntu)"
    echo "  Либо используйте автоматическую сборку через GitHub Actions."
    exit 1
fi

rm -rf "$RPM_TOPDIR"
mkdir -p "$RPM_TOPDIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
mkdir -p dist

cp echo-settings.spec "$RPM_TOPDIR/SPECS/"

rpmbuild --define "_topdir $RPM_TOPDIR"          --define "_sourcedir $SCRIPT_DIR"          -bb "$RPM_TOPDIR/SPECS/echo-settings.spec"

find "$RPM_TOPDIR/RPMS" -name "*.rpm" -exec cp {} dist/ \;
LATEST_RPM=$(find dist/ -maxdepth 1 -name "echo-settings-${VERSION}*.rpm" | head -n 1)
if [ -n "$LATEST_RPM" ]; then
    cp "$LATEST_RPM" dist/echo-settings_latest.noarch.rpm
    cd dist
    sha256sum "$(basename "$LATEST_RPM")" > "$(basename "$LATEST_RPM").sha256"
    cd ..
fi

rm -rf "$RPM_TOPDIR"
echo "=========================================="
echo "✅ RPM-пакет успешно собран в каталоге dist/"
ls -lh dist/*.rpm
echo "=========================================="
