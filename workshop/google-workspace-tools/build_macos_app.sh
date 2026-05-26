#!/usr/bin/env bash
# build_macos_app.sh
# Compiles three standalone macOS app wrappers: Google Sheets, Google Docs, and Google Slides.
# Sets their bundle identifiers, registers them, and configures default associations via duti.

set -euo pipefail

OUTPUT_DIR="/Users/frankie/Documents/GitHub/vidaFS/workshop/google-workspace-tools"
NODE_PATH="/opt/homebrew/bin/node"
HANDLER_JS="/Users/frankie/.openclaw/workspace/open_in_google.js"
LSREGISTER="/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister"

# Helper function to compile and configure an app
build_app() {
  local app_name="$1"
  local bundle_id="$2"
  local desc="$3"
  local output_path="${OUTPUT_DIR}/${app_name}.app"

  echo "🔨 Compiling ${app_name}.app..."
  if [ -d "$output_path" ]; then
    rm -rf "$output_path"
  fi

  osacompile -o "$output_path" -e "
  on open theFiles
      repeat with theFile in theFiles
          set thePath to POSIX path of theFile
          do shell script \"${NODE_PATH} ${HANDLER_JS} \" & quoted form of thePath
      end repeat
  end open

  on run
      display dialog \"${desc}: Set me as the default app for associated files in Finder (Right-click file -> Get Info -> Open With -> Change All).\" buttons {\"OK\"} default button \"OK\" with icon note
  end run
  "

  # Set bundle identifier
  plutil -insert CFBundleIdentifier -string "$bundle_id" "${output_path}/Contents/Info.plist"
  
  # Register with Launch Services
  "$LSREGISTER" -f "$output_path"
  echo "✅ Standalone app '${app_name}' created and registered."
}

# 1. Build Google Sheets
build_app "Google Sheets" "com.wescope.GoogleSheets" "Google Sheets Handler"

# 2. Build Google Docs
build_app "Google Docs" "com.wescope.GoogleDocs" "Google Docs Handler"

# 3. Build Google Slides
build_app "Google Slides" "com.wescope.GoogleSlides" "Google Slides Handler"

echo "🔗 Configuring file associations programmatically..."

# Sheets associations
duti -s com.wescope.GoogleSheets .csv all
duti -s com.wescope.GoogleSheets .xlsx all
duti -s com.wescope.GoogleSheets .xls all

# Docs associations
duti -s com.wescope.GoogleDocs .docx all
duti -s com.wescope.GoogleDocs .doc all
duti -s com.wescope.GoogleDocs .rtf all

# Slides associations
duti -s com.wescope.GoogleSlides .pptx all
duti -s com.wescope.GoogleSlides .ppt all

echo "🚀 DONE! All file extensions associated natively with Google Sheets, Google Docs, and Google Slides apps!"
