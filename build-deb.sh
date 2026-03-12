#!/usr/bin/env bash
# Build a .deb package for md-reader
set -euo pipefail

APP_NAME="md-reader"
VERSION="0.1.0"
ARCH="all"
INSTALL_DIR="/opt/${APP_NAME}"
PKG_DIR="${APP_NAME}_${VERSION}_${ARCH}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Building ${APP_NAME} ${VERSION} .deb package"

# Clean previous build
rm -rf "${SCRIPT_DIR}/${PKG_DIR}" "${SCRIPT_DIR}/${PKG_DIR}.deb"

# Create directory structure
mkdir -p "${PKG_DIR}/DEBIAN"
mkdir -p "${PKG_DIR}${INSTALL_DIR}"
mkdir -p "${PKG_DIR}/usr/bin"
mkdir -p "${PKG_DIR}/usr/share/applications"
mkdir -p "${PKG_DIR}/usr/share/icons/hicolor/scalable/apps"

# --- Copy application files ---
echo "==> Copying application files"
cp "${SCRIPT_DIR}/main.py" "${PKG_DIR}${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/core" "${PKG_DIR}${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/config" "${PKG_DIR}${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/ui" "${PKG_DIR}${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/resources" "${PKG_DIR}${INSTALL_DIR}/"

# Remove __pycache__ directories
find "${PKG_DIR}${INSTALL_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# --- Create launcher script ---
echo "==> Creating launcher script"
cat > "${PKG_DIR}/usr/bin/${APP_NAME}" << 'LAUNCHER'
#!/usr/bin/env bash
exec python3 /opt/md-reader/main.py "$@"
LAUNCHER
chmod 755 "${PKG_DIR}/usr/bin/${APP_NAME}"

# --- Install desktop file and icon ---
cp "${SCRIPT_DIR}/resources/md-reader.desktop" "${PKG_DIR}/usr/share/applications/"
cp "${SCRIPT_DIR}/resources/md-reader.svg" "${PKG_DIR}/usr/share/icons/hicolor/scalable/apps/"

# --- Calculate installed size ---
INSTALLED_SIZE=$(du -sk "${PKG_DIR}" | cut -f1)

# --- Create DEBIAN/control ---
cat > "${PKG_DIR}/DEBIAN/control" << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: text
Priority: optional
Architecture: ${ARCH}
Installed-Size: ${INSTALLED_SIZE}
Depends: python3 (>= 3.10), python3-pyqt6, python3-pyqt6.qtwebengine, python3-markdown2, python3-pygments
Maintainer: tio <tio@local>
Description: A simple GUI markdown viewer
 Markdown Reader is a desktop application for viewing markdown files
 with syntax highlighting, table of contents navigation, search,
 and light/dark theme support. Built with PyQt6.
Homepage: https://github.com/tio/md-reader
EOF

# --- Create postinst to update desktop database ---
cat > "${PKG_DIR}/DEBIAN/postinst" << 'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database > /dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache > /dev/null 2>&1; then
    gtk-update-icon-cache -q /usr/share/icons/hicolor || true
fi
EOF
chmod 755 "${PKG_DIR}/DEBIAN/postinst"

# --- Create postrm to clean up ---
cat > "${PKG_DIR}/DEBIAN/postrm" << 'EOF'
#!/bin/sh
set -e
if [ "$1" = "purge" ]; then
    rm -rf /opt/md-reader
fi
if command -v update-desktop-database > /dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
EOF
chmod 755 "${PKG_DIR}/DEBIAN/postrm"

# --- Set correct permissions ---
find "${PKG_DIR}" -type d -exec chmod 755 {} +
find "${PKG_DIR}" -type f -exec chmod 644 {} +
chmod 755 "${PKG_DIR}/usr/bin/${APP_NAME}"
chmod 755 "${PKG_DIR}/DEBIAN/postinst"
chmod 755 "${PKG_DIR}/DEBIAN/postrm"

# --- Build the package ---
echo "==> Building .deb package"
dpkg-deb --build --root-owner-group "${PKG_DIR}"

echo ""
echo "==> Package built: ${PKG_DIR}.deb"
echo "    Install with: sudo apt install ./${PKG_DIR}.deb"
echo "    Remove with:  sudo apt remove ${APP_NAME}"

# Clean up build directory
rm -rf "${PKG_DIR}"
