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
 "plugin.png"
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
  IFS='.' read -r a b c <<< "$1"
  IFS='.' read -r x y z <<< "$2"

  for i in a b c; do
    eval l=\$$i
    eval r=\$$(echo {x,y,z} | cut -d',' -f$((i=="a"?1:i=="b"?2:3)))
  done

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
create_backup() {
 mkdir -p "$BACKUP_DIR"
 cp -rf "$PLUGIN_PATH/"* "$BACKUP_DIR/" 2>/dev/null
}

# --------------------------------------------------
restore_backup() {
 msg yellow "Restoring backup..."
 rm -rf "$PLUGIN_PATH"
 mkdir -p "$PLUGIN_PATH"
 cp -rf "$BACKUP_DIR/"* "$PLUGIN_PATH/"
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
install_files() {
 mkdir -p "$PLUGIN_PATH"
 cp -rf "$TMP_DIR/"* "$PLUGIN_PATH/"
 chmod 755 "$PLUGIN_PATH"/*.py 2>/dev/null
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
 0) msg green "Already up to date"; exit 0;;
 2) msg green "Local version is newer"; exit 0;;
esac

msg yellow "New update available"

create_backup || { msg red "Backup failed"; exit 1; }

download_to_tmp || {
 msg red "Download failed"
 restore_backup
 exit 1
}

install_files || {
 msg red "Install failed"
 restore_backup
 exit 1
}

rm -rf "$TMP_DIR" "$BACKUP_DIR"
msg green "Update completed successfully"

restart_gui
exit 0
