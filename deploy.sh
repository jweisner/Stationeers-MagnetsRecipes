#!/usr/bin/env bash
# Build and install into the Stationeers local mods folder (Proton prefix).
set -euo pipefail
cd "$(dirname "$0")"
MODS="${STATIONEERS_MODS:-$HOME/.local/share/Steam/steamapps/compatdata/544550/pfx/drive_c/users/steamuser/Documents/My Games/Stationeers/mods}"
DEST="$MODS/MagnetsRecipes"
dotnet build -c Release src/MagnetsRecipes.csproj
mkdir -p "$DEST/About" "$DEST/GameData"
cp About/About.xml About/thumb.png About/Preview.png "$DEST/About/"
cp GameData/*.xml "$DEST/GameData/"
cp src/bin/Release/net472/MagnetsRecipes.dll LICENSE "$DEST/"
echo "Installed to $DEST"
