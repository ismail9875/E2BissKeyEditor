#!/bin/bash
# ==================================================
# E2BissKeyEditor Unified Installer / Updater
# Author : Ismail9875
# Logic  : Safe Update + Semantic Versioning
# ==================================================

PLUGIN_NAME="E2BissKeyEditor"
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/${PLUGIN_NAME}"
REMOTE_BASE="https://raw.githubusercontent.com/ismail9875/E2BissKeyEditor/refs/heads/main"
TMP_DIR="/tmp/${PLUGIN_NAME}_update"
BACKUP_DIR="/tmp/${PLUGIN_NAME}_backup_$(date +%Y%m%d_%H%M%S)"

FILES=(
 "__init__.py"
 "plugin.py"
 "settings"
 "version"
 "usingMode.py"
 "plugin.png"
)

# ==================================================
# Converters - ملفات المحولات
# ==================================================
CONVERTER_PATH="/usr/lib/enigma2/python/Components/Converter"

CONVERTER_FILES=(
 "E2BissKeyEditorClockToText.py"
 "E2BissKeyEditorCryptInfo.py"
 "E2BissKeyEditorServiceName2.py"
)

# --------------------------------------------------
msg() {
 case $1 in
  green)  echo -e "\033[32m$2\033[0m";;
  red)    echo -e "\033[31m$2\033[0m";;
  yellow) echo -e "\033[33m$2\033[0m";;
  blue)   echo -e "\033[34m$2\033[0m";;
  *)      echo "$2";;
 esac
}

# --------------------------------------------------
semantic_compare() {
  # returns: 0 equal | 1 remote newer | 2 local newer
  [ "$1" = "$2" ] && return 0
  printf '%s\n%s\n' "$1" "$2" | sort -V | head -n1 | grep -qx "$1" && return 1 || return 2
}

# --------------------------------------------------
check_internet() {
 ping -c1 -W3 raw.githubusercontent.com >/dev/null 2>&1
}

# --------------------------------------------------
get_versions() {
 LOCAL_VERSION="0.0.0"
 [ -f "$PLUGIN_PATH/version" ] && LOCAL_VERSION=$(cat "$PLUGIN_PATH/version")

 REMOTE_VERSION=$(wget -q -O- "$REMOTE_BASE/version")
 [ -z "$REMOTE_VERSION" ] && return 1
 return 0
}

# --------------------------------------------------
check_converters_installed() {
 for f in "${CONVERTER_FILES[@]}"; do
   [ ! -f "$CONVERTER_PATH/$f" ] && return 1
 done
 return 0
}

# --------------------------------------------------
check_any_converter_installed() {
 # للتحقق إذا كان هناك أي ملف محول موجود (واحد على الأقل)
 for f in "${CONVERTER_FILES[@]}"; do
   [ -f "$CONVERTER_PATH/$f" ] && return 0
 done
 return 1
}

# --------------------------------------------------
create_backup() {
 msg yellow "Creating backup..."
 
 # إنشاء مجلد النسخ الاحتياطي
 mkdir -p "$BACKUP_DIR"
 
 # نسخ ملفات الإضافة (إذا كانت موجودة)
 if [ -d "$PLUGIN_PATH" ]; then
   cp -rf "$PLUGIN_PATH/"* "$BACKUP_DIR/" 2>/dev/null || {
     msg yellow "Warning: Could not backup plugin files (may not exist)"
   }
 else
   msg yellow "Note: Plugin directory does not exist, fresh install"
 fi
 
 # نسخ ملفات المحولات (إذا كانت موجودة)
 if check_any_converter_installed; then
   msg yellow "Backing up existing converters..."
   mkdir -p "$BACKUP_DIR/Converter"
   for f in "${CONVERTER_FILES[@]}"; do
     if [ -f "$CONVERTER_PATH/$f" ]; then
       cp -f "$CONVERTER_PATH/$f" "$BACKUP_DIR/Converter/" 2>/dev/null && \
       msg blue "  Backed up: $f" || \
       msg yellow "  Warning: Could not backup $f"
     fi
   done
 else
   msg yellow "No existing converters found, skipping converter backup"
 fi
 
 return 0
}

# --------------------------------------------------
restore_backup() {
 msg yellow "Restoring backup..."
 
 # استعادة ملفات الإضافة
 if [ -d "$BACKUP_DIR" ] && [ -n "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
   rm -rf "$PLUGIN_PATH" 2>/dev/null
   mkdir -p "$PLUGIN_PATH"
   cp -rf "$BACKUP_DIR/"* "$PLUGIN_PATH/" 2>/dev/null
 else
   msg yellow "No plugin files to restore"
 fi
 
 # استعادة ملفات المحولات (إذا كانت موجودة في النسخة الاحتياطية)
 if [ -d "$BACKUP_DIR/Converter" ] && [ -n "$(ls -A "$BACKUP_DIR/Converter" 2>/dev/null)" ]; then
   msg yellow "Restoring converters..."
   mkdir -p "$CONVERTER_PATH"
   for f in "${CONVERTER_FILES[@]}"; do
     if [ -f "$BACKUP_DIR/Converter/$f" ]; then
       cp -f "$BACKUP_DIR/Converter/$f" "$CONVERTER_PATH/" 2>/dev/null && \
       msg blue "  Restored: $f" || \
       msg yellow "  Warning: Could not restore $f"
     fi
   done
 else
   msg yellow "No converter backup to restore"
 fi
}

# --------------------------------------------------
download_to_tmp() {
 rm -rf "$TMP_DIR"
 mkdir -p "$TMP_DIR"

 for f in "${FILES[@]}"; do
   msg blue "Downloading $f"
   wget -q -O "$TMP_DIR/$f" "$REMOTE_BASE/$f" || return 1
   [ ! -s "$TMP_DIR/$f" ] && return 1
 done
 return 0
}

# --------------------------------------------------
download_converters() {
 msg yellow "Downloading converters..."
 
 local download_success=true
 for f in "${CONVERTER_FILES[@]}"; do
   msg blue "  Downloading: $f"
   wget -q -O "$TMP_DIR/$f" "$REMOTE_BASE/$f"
   
   if [ $? -ne 0 ] || [ ! -s "$TMP_DIR/$f" ]; then
     msg red "  Failed to download: $f"
     download_success=false
   else
     msg green "  ✓ Downloaded: $f"
   fi
 done
 
 if [ "$download_success" = false ]; then
   msg red "Some converters failed to download"
   return 1
 fi
 return 0
}

# --------------------------------------------------
install_files() {
 msg yellow "Installing plugin files..."
 
 mkdir -p "$PLUGIN_PATH"
 local install_success=true
 
 for f in "${FILES[@]}"; do
   if [ -f "$TMP_DIR/$f" ]; then
     cp -f "$TMP_DIR/$f" "$PLUGIN_PATH/$f" && \
     chmod 755 "$PLUGIN_PATH/$f" 2>/dev/null && \
     msg green "  ✓ Installed: $f" || {
       msg red "  ✗ Failed to install: $f"
       install_success=false
     }
   else
     msg red "  ✗ File not found: $f"
     install_success=false
   fi
 done
 
 [ "$install_success" = false ] && return 1
 return 0
}

# --------------------------------------------------
install_converters() {
 msg yellow "Installing converters..."
 
 mkdir -p "$CONVERTER_PATH"
 local install_success=true
 local converters_found=0
 local converters_installed=0
 
 for f in "${CONVERTER_FILES[@]}"; do
   if [ -f "$TMP_DIR/$f" ]; then
     converters_found=$((converters_found + 1))
     msg blue "  Installing: $f"
     
     cp -f "$TMP_DIR/$f" "$CONVERTER_PATH/$f" && \
     chmod 755 "$CONVERTER_PATH/$f" 2>/dev/null && {
       converters_installed=$((converters_installed + 1))
       msg green "    ✓ Installed to: $CONVERTER_PATH/$f"
     } || {
       msg red "    ✗ Failed to install: $f"
       install_success=false
     }
   else
     msg yellow "  ⚠ Skipping: $f (not downloaded)"
   fi
 done
 
 if [ $converters_found -eq 0 ]; then
   msg yellow "No converter files found to install"
   return 0
 fi
 
 if [ $converters_installed -eq 0 ]; then
   msg red "Failed to install any converters"
   return 1
 fi
 
 if [ "$install_success" = false ]; then
   msg yellow "Some converters failed to install"
   return 1
 fi
 
 msg green "✓ Successfully installed $converters_installed converter(s)"
 return 0
}

# --------------------------------------------------
restart_gui() {
 msg yellow "Restarting Enigma2 GUI..."
 systemctl restart enigma2 2>/dev/null || (init 4 && sleep 2 && init 3)
}

# ===================== MAIN ========================

msg blue "Starting ${PLUGIN_NAME} Installer / Updater"

check_internet || { msg red "No internet connection"; exit 1; }

get_versions || { msg red "Failed to read versions"; exit 1; }

msg blue "Local Version  : $LOCAL_VERSION"
msg blue "Remote Version : $REMOTE_VERSION"

semantic_compare "$LOCAL_VERSION" "$REMOTE_VERSION"
case $? in
 0)
   msg green "Plugin version is up to date"
   if check_converters_installed; then
     msg green "Converters already installed"
     exit 0
   else
     msg yellow "Missing converters detected, installing..."
   fi
   ;;
 2)
   msg green "Local version is newer"
   exit 0
   ;;
esac

msg yellow "Update process started"

# إنشاء نسخة احتياطية (لن تفشل إذا لم توجد ملفات محولات)
create_backup

# تنزيل الملفات الأساسية
download_to_tmp || {
 msg red "Main files download failed"
 restore_backup
 exit 1
}

# تنزيل المحولات (لا تفشل العملية كاملة إذا فشل بعضها)
if ! download_converters; then
 msg yellow "Warning: Some converters failed to download, continuing..."
fi

# تثبيت الملفات الأساسية
install_files || {
 msg red "Plugin files install failed"
 restore_backup
 exit 1
}

# تثبيت المحولات (لا تفشل العملية كاملة إذا فشل بعضها)
if ! install_converters; then
 msg yellow "Warning: Some converters failed to install"
fi

# تنظيف الملفات المؤقتة
rm -rf "$TMP_DIR" "$BACKUP_DIR"
msg green "Update completed successfully"

restart_gui
exit 0
