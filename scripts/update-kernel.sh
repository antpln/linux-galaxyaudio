#!/bin/bash
set -e

# Get latest stable kernel version
LATEST_VER=$(curl -s https://www.kernel.org/releases.json | jq -r '.releases[] | select(.moniker=="stable") | .version' | head -n 1)
CURRENT_VER=$(grep "^pkgver=" PKGBUILD | cut -d'=' -f2)

echo "Latest: $LATEST_VER"
echo "Current: $CURRENT_VER"

if [ "$LATEST_VER" != "$CURRENT_VER" ]; then
    echo "New version available!"
    sed -i "s/^pkgver=.*/pkgver=$LATEST_VER/" PKGBUILD
    # Reset pkgrel
    sed -i "s/^pkgrel=.*/pkgrel=1/" PKGBUILD
    
    # Update patch AND checksums
    echo "Updating patch..."
    bash scripts/generate-patch.sh
    
    echo "Updating checksums..."
    updpkgsums
    
    echo "::set-output name=updated::true"
    echo "::set-output name=version::$LATEST_VER"
else
    echo "Already up to date."
    echo "::set-output name=updated::false"
fi
