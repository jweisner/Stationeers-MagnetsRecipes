#!/usr/bin/env bash
# Build a downloadable mod zip in dist/. With --publish, also create a GitHub release for it.
set -euo pipefail
cd "$(dirname "$0")"

PUBLISH=0
case "${1:-}" in
  "") ;;
  --publish) PUBLISH=1 ;;
  *) echo "usage: $0 [--publish]" >&2; exit 2 ;;
esac

VERSION=$(sed -n 's|.*<Version>\(.*\)</Version>.*|\1|p' About/About.xml)
PLUGIN_VERSION=$(sed -n 's|.*PluginVersion = "\(.*\)";.*|\1|p' src/Plugin.cs)
if [ -z "$VERSION" ] || [ "$VERSION" != "$PLUGIN_VERSION" ]; then
  echo "Version mismatch: About.xml '$VERSION', Plugin.cs '$PLUGIN_VERSION'" >&2
  exit 1
fi
TAG="v$VERSION"
ZIP="FurnaceRecipes-$VERSION.zip"

if [ "$PUBLISH" = 1 ]; then
  if [ -n "$(git status --porcelain)" ]; then
    echo "Working tree is not clean; commit before publishing." >&2
    exit 1
  fi
  git fetch -q origin
  if [ "$(git rev-parse HEAD)" != "$(git rev-parse @{u})" ]; then
    echo "HEAD is not the same as its upstream; push (or pull) before publishing." >&2
    exit 1
  fi
  if gh release view "$TAG" >/dev/null 2>&1; then
    echo "Release $TAG already exists; bump the version in About.xml and Plugin.cs." >&2
    exit 1
  fi
fi

# Stage exactly what deploy.sh installs, then zip it with the mod folder at the top level.
STAGE="$PWD/dist/stage"
rm -rf "$STAGE" "dist/$ZIP"
STATIONEERS_MODS="$STAGE" ./deploy.sh
(cd "$STAGE" && zip -qr "../$ZIP" FurnaceRecipes)
rm -rf "$STAGE"
echo "Built dist/$ZIP"
unzip -l "dist/$ZIP"

if [ "$PUBLISH" = 1 ]; then
  gh release create "$TAG" "dist/$ZIP" --target "$(git rev-parse HEAD)" \
    --title "Furnace Recipes $VERSION" --generate-notes
  # A listed asset is not proof it downloads; fetch it.
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  URL="https://github.com/$REPO/releases/download/$TAG/$ZIP"
  CODE=$(curl -sL -o /dev/null -w '%{http_code}' "$URL")
  echo "$URL -> HTTP $CODE"
  [ "$CODE" = 200 ]
fi
