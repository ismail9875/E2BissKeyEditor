#!/bin/bash
# =====================================================================
# cmd : wget "--no-check-certificate" https://raw.githubusercontent.com/ismail9875/E2BissKeyEditor/refs/heads/main/installer.sh | /bin/sh
# =====================================================================

echo """
# ==================================================
#               Installer Process
#               E2Biss Key Editor
#               By: Ismail
# ==================================================
"""

#pluginPath="/usr/lib/enigma2/python/Plugins/Extensions/E2BissKeyEditor"
pluginPatg="/media/hdd/scripts"
cmd="wget -q --timeout=30 --tries=2 -O"
pluginRemote="https://raw.githubusercontent.com/ismail9875/E2BissKeyEditor/refs/heads/main/"
backupPath="/tmp/E2BissKeyEditor_backup_$(date +%Y%m%d_%H%M%S)"
backupCreated=false
downloadFailed=false

# Required files list
files=(
    "__init__.py"
    "plugin.py"
    "settings"
    "version"
    "plugin.png"
)

# Colored message printer
print_message() {
    local color=$1
    local message=$2
    case $color in
        "red") echo -e "\033[31m$message\033[0m" ;;
        "green") echo -e "\033[32m$message\033[0m" ;;
        "yellow") echo -e "\033[33m$message\033[0m" ;;
        "blue") echo -e "\033[34m$message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# Internet connection check
check_internet() {
    print_message "blue" "Checking internet connection..."
    if ping -c 2 -W 3 raw.githubusercontent.com > /dev/null 2>&1; then
        print_message "green" "✓ Internet connection available"
        return 0
    else
        print_message "red" "✗ No internet connection"
        return 1
    fi
}

# Create backup
create_backup() {
    if [ -d "$pluginPath" ] && [ -n "$(ls -A "$pluginPath" 2>/dev/null)" ]; then
        print_message "blue" "Creating backup of existing files..."
        mkdir -p "$backupPath"

        for file in "${files[@]}"; do
            if [ -f "$pluginPath/$file" ]; then
                cp -f "$pluginPath/$file" "$backupPath/" 2>/dev/null
            fi
        done

        cp -rf "$pluginPath/"* "$backupPath/" 2>/dev/null

        if [ -n "$(ls -A "$backupPath" 2>/dev/null)" ]; then
            print_message "green" "✓ Backup created at: $backupPath"
            backupCreated=true
            return 0
        else
            print_message "yellow" "⚠ Backup directory is empty, no backup needed"
            return 1
        fi
    else
        print_message "yellow" "⚠ Plugin directory does not exist or is empty, fresh install"
        return 1
    fi
}

# Restore backup
restore_backup() {
    if [ "$backupCreated" = true ] && [ -d "$backupPath" ]; then
        print_message "yellow" "Restoring backup due to download failure..."

        mkdir -p "$pluginPath"

        if [ -n "$(ls -A "$backupPath" 2>/dev/null)" ]; then
            cp -rf "$backupPath/"* "$pluginPath/" 2>/dev/null
            print_message "green" "✓ Backup restored successfully"
            return 0
        fi
    fi
    return 1
}

# Version check
check_version() {
    local localVersion=""
    local remoteVersion=""

    if [ -f "$pluginPath/version" ]; then
        localVersion=$(head -n1 "$pluginPath/version" | tr -d '\n\r ')
    fi

    print_message "blue" "Checking remote version..."
    remoteVersion=$(wget -q --timeout=10 -O- "${pluginRemote}version" | head -n1 | tr -d '\n\r ')

    if [ -z "$remoteVersion" ]; then
        print_message "red" "✗ Failed to fetch remote version"
        return 2
    fi

    if [ -z "$localVersion" ]; then
        print_message "yellow" "ℹ Local version: not installed"
        print_message "green" "ℹ Remote version: $remoteVersion"
        return 1
    else
        print_message "blue" "ℹ Local version: $localVersion"
        print_message "blue" "ℹ Remote version: $remoteVersion"

        if [ "$localVersion" = "$remoteVersion" ]; then
            print_message "green" "✓ You already have the latest version"
            return 0
        else
            print_message "yellow" "⚠ New version available: $remoteVersion"
            return 1
        fi
    fi
}

# Download files
download_files() {
    local successCount=0
    local totalFiles=${#files[@]}

    mkdir -p "$pluginPath"

    print_message "blue" "Starting download of $totalFiles files..."

    for file in "${files[@]}"; do
        print_message "blue" "Downloading: $file"

        if ${cmd} "${pluginPath}/${file}" "${pluginRemote}${file}"; then
            if [ -s "${pluginPath}/${file}" ]; then
                print_message "green" "  ✓ $file downloaded successfully"
                ((successCount++))

                if [[ "$file" == *.py ]]; then
                    chmod 755 "${pluginPath}/${file}" 2>/dev/null
                fi
            else
                print_message "red" "  ✗ $file is empty"
                rm -f "${pluginPath}/${file}" 2>/dev/null
            fi
        else
            print_message "red" "  ✗ Failed to download $file"
            rm -f "${pluginPath}/${file}" 2>/dev/null
        fi
    done

    if [ $successCount -eq $totalFiles ]; then
        print_message "green" "✓ All files downloaded successfully ($successCount/$totalFiles)"
        return 0
    elif [ $successCount -gt 0 ]; then
        print_message "yellow" "⚠ Partial download: $successCount of $totalFiles files"
        return 1
    else
        print_message "red" "✗ All downloads failed"
        return 2
    fi
}

# Cleanup backup
cleanup_backup() {
    if [ "$backupCreated" = true ] && [ "$downloadFailed" = false ]; then
        print_message "blue" "Cleaning up backup..."
        rm -rf "$backupPath" 2>/dev/null
        print_message "green" "✓ Backup cleaned"
    fi
}

# === MAIN EXECUTION ===

print_message "blue" "Starting E2BissKeyEditor update process"
echo "========================================"

if ! check_internet; then
    print_message "red" "Process aborted: No internet connection"
    exit 1
fi

check_version
create_backup

if download_files; then
    print_message "blue" "Verifying update..."
    if check_version; then
        print_message "green" "✓ Update completed successfully"
    else
        print_message "green" "✓ Files updated successfully"
    fi
    cleanup_backup
    exit 0
else
    downloadFailed=true

    if restore_backup; then
        print_message "yellow" "Original files restored"
    else
        print_message "red" "⚠ Backup restoration failed"
    fi

    for file in "${files[@]}"; do
        [ -f "$pluginPath/$file" ] && rm -f "$pluginPath/$file" 2>/dev/null
    done

    print_message "red" "✗ Update process failed"
    exit 1
fi