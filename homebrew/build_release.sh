#!/bin/bash
set -e

# Configuration
APP_NAME="clean-up-clawd"
VERSION="1.0.1"
DIST_DIR="dist"
RELEASE_DIR="release"
TAR_NAME="${APP_NAME}-v${VERSION}-macos.tar.gz"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Building ${APP_NAME}...${NC}"

# Clean previous builds
rm -rf build dist

# Build with PyInstaller
uv run pyinstaller clean-up-clawd.spec --noconfirm

# Create release directory
mkdir -p "$RELEASE_DIR"

# Create tarball
echo -e "${BLUE}Creating tarball...${NC}"
cd "$DIST_DIR"
tar -czf "../$RELEASE_DIR/$TAR_NAME" "$APP_NAME"
cd ..

# Calculate SHA256
SHA256=$(shasum -a 256 "$RELEASE_DIR/$TAR_NAME" | awk '{print $1}')

echo -e "${GREEN}Build Complete!${NC}"
echo -e "Artifact: ${RELEASE_DIR}/${TAR_NAME}"
echo -e "SHA256: ${SHA256}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Upload '$RELEASE_DIR/$TAR_NAME' to improved GitHub Release."
echo "2. Update 'homebrew/Formula/${APP_NAME}.rb' with:"
echo "   - url: <link to your new release asset>"
echo "   - sha256: \"$SHA256\""
echo "3. Push the formula to your homebrew-tap repository."
