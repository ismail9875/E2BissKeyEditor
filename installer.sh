#!/bin/bash
# =====================================================================
# cmd : wget --no-check-certificate -O - https://raw.githubusercontent.com/ismail9875/E2BissKeyEditor/refs/heads/main/installer.sh | /bin/bash
# =====================================================================


echo """
# ==================================================
#               Installer Process
#               E2Biss Key Editor
#                By: Ismail9875
# ==================================================
"""

pluginPath="/usr/lib/enigma2/python/Plugins/Extensions/E2BissKeyEditor"
cmd="wget -q --timeout=30 --tries=2 -O"
pluginRemote="https://raw.githubusercontent.com/ismail9875/E2BissKeyEditor/refs/heads/main/"
backupPath="/tmp/E2BissKeyEditor_backup_$(date +%Y%m%d_%H%M%S)"
backupCreated=false
downloadFailed=false
allFilesDownloadedSuccessfully=false

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

# Check and create plugin directory if not exists
check_and_create_plugin_directory() {
    print_message "blue" "Checking plugin directory..."
    
    if [ ! -d "$pluginPath" ]; then
        print_message "yellow" "⚠ Plugin directory does not exist: $pluginPath"
        print_message "blue" "Creating plugin directory..."
        
        if mkdir -p "$pluginPath" 2>/dev/null; then
            print_message "green" "✓ Plugin directory created successfully: $pluginPath"
            return 0
        else
            print_message "red" "✗ Failed to create plugin directory: $pluginPath"
            return 1
        fi
    else
        print_message "green" "✓ Plugin directory exists: $pluginPath"
        return 0
    fi
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

        # تأكد من وجود مجلد الإضافة قبل الاستعادة
        if ! check_and_create_plugin_directory; then
            print_message "red" "✗ Cannot restore backup - failed to create plugin directory"
            return 1
        fi

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

    # تأكد من وجود مجلد الإضافة قبل التحميل
    if ! check_and_create_plugin_directory; then
        print_message "red" "✗ Cannot download files - plugin directory creation failed"
        return 2
    fi

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
        allFilesDownloadedSuccessfully=true
        return 0
    elif [ $successCount -gt 0 ]; then
        print_message "yellow" "⚠ Partial download: $successCount of $totalFiles files"
        allFilesDownloadedSuccessfully=false
        return 1
    else
        print_message "red" "✗ All downloads failed"
        allFilesDownloadedSuccessfully=false
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

# Restart Enigma2 GUI
restart_enigma2() {
    echo ""
    echo "========================================"
    print_message "yellow" "All files downloaded successfully!"
    print_message "blue" "Restarting Enigma2 GUI to apply changes..."
    
    # محاولة إعادة التشغيل باستخدام systemctl
    if systemctl restart enigma2 2>/dev/null; then
        print_message "green" "✓ Enigma2 GUI restart initiated via systemctl"
        echo "GUI will restart in a few seconds..."
        return 0
    fi
    
    # محاولة إعادة التشغيل باستخدام init (للأنظمة القديمة)
    print_message "blue" "Trying alternative restart method..."
    if init 4 2>/dev/null && sleep 2 && init 3 2>/dev/null; then
        print_message "green" "✓ Enigma2 GUI restart initiated via init"
        echo "GUI will restart in a few seconds..."
        return 0
    fi
    
    # إذا فشلت الطرق التلقائية
    print_message "red" "✗ Could not restart Enigma2 GUI automatically"
    print_message "yellow" "⚠ Please restart Enigma2 GUI manually from your receiver:"
    echo ""
    print_message "blue" "Manual restart options:"
    echo "  1. Menu -> Standby/Restart -> Restart GUI"
    echo "  2. Using telnet/ssh: 'systemctl restart enigma2'"
    echo "  3. Or: 'init 4 && sleep 2 && init 3'"
    echo ""
    print_message "yellow" "Note: Changes will take effect after GUI restart"
    return 1
}

# === MAIN EXECUTION ===

print_message "blue" "Starting E2BissKeyEditor update process"
echo "========================================"

if ! check_internet; then
    print_message "red" "Process aborted: No internet connection"
    exit 1
fi

# التحقق من وجود مجلد الإضافة وإنشائه في بداية العملية
if ! check_and_create_plugin_directory; then
    print_message "red" "Process aborted: Cannot create plugin directory"
    exit 1
fi

check_version
create_backup

if download_files; then
    # التحقق من أن جميع الملفات تم تحميلها بنجاح
    if [ "$allFilesDownloadedSuccessfully" = true ]; then
        print_message "blue" "Verifying update..."
        if check_version; then
            print_message "green" "✓ Update completed successfully"
        else
            print_message "green" "✓ Files updated successfully"
        fi
        cleanup_backup
        
        # إعادة تشغيل واجهة الإنيجما2 فقط عند اكتمال تحميل جميع الملفات
        restart_enigma2
        
        exit 0
    else
        # حالة التحميل الجزئي (بعض الملفات فشلت)
        downloadFailed=true
        print_message "red" "✗ Some files failed to download"
        
        if restore_backup; then
            print_message "yellow" "Original files restored due to partial download"
        fi
        
        # لا تقم بإعادة التشغيل في حالة التحميل الجزئي
        print_message "red" "⚠ Enigma2 GUI restart skipped - not all files were downloaded"
        exit 1
    fi
else
    # حالة فشل التحميل بالكامل
    downloadFailed=true
    print_message "red" "✗ Download process failed"

    if restore_backup; then
        print_message "yellow" "Original files restored"
    else
        print_message "red" "⚠ Backup restoration failed"
    fi

    for file in "${files[@]}"; do
        [ -f "$pluginPath/$file" ] && rm -f "$pluginPath/$file" 2>/dev/null
    done

    print_message "red" "✗ Update process failed"
    
    # لا تقم بإعادة التشغيل إذا فشل التحديث
    print_message "yellow" "⚠ Enigma2 GUI restart skipped due to update failure"
    
    exit 1
fi
