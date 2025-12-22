# -*- coding: utf-8 -*-
# Coded Using Ai Tools *** Ismail9875 ***
# *** *** *** *** *** ***
#       3 Dec 2025      
# *** *** *** *** *** ***
from __future__ import print_function
from __future__ import absolute_import
import sys


from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from Components.ProgressBar import ProgressBar
from Components.ConfigList import ConfigList
from Components.Sources.StaticText import StaticText
from datetime import datetime
import binascii
import os
import re
import zlib
from array import array
import subprocess
import signal
import time
import shutil
from Screens.Standby import TryQuitMainloop
from skin import parseColor
import socket
from twisted.web.client import downloadPage
import threading
from enigma import eServiceReference, iServiceInformation, eServiceCenter, eDVBDB, gRGB, eTimer
import os
import shutil
import threading
import subprocess
from enigma import eTimer


# استيرادات متوافقة مع Python 2 و 3
import sys
PY3 = sys.version_info[0] == 3
try:
    # Python 3
    from urllib.request import Request as compat_Request, urlopen as compat_urlopen
except ImportError:
    # Python 2
    from urllib2 import Request as compat_Request, urlopen as compat_urlopen

# =============================================
# مسار إعدادات البلوجين
# =============================================
PLUGIN_PATH = os.path.dirname(__file__)
PLUGIN_SETTINGS_FILE = os.path.join(PLUGIN_PATH, "settings")

# =============================================
# تهيئة الإعدادات الافتراضية
# =============================================
DEFAULT_SETTINGS = {
    'restart_emu': 'True',
    'UseCustomPath': 'False',
    'HashLogic': 'CRC32 Original',
    'custom_save_path': '/etc/tuxbox/config/SoftCam.Key'
}

# =============================================
# دوال قراءة/كتابة إعدادات البلوجين
# =============================================

def ensure_settings_file():
    """التأكد من وجود ملف إعدادات البلوجين وإنشاؤه بالقيم الافتراضية إذا لم يكن موجوداً"""
    try:
        if not os.path.exists(PLUGIN_SETTINGS_FILE):
            print(f"Creating plugin settings file: {PLUGIN_SETTINGS_FILE}")
            with open(PLUGIN_SETTINGS_FILE, 'w', encoding='utf-8' if PY3 else None) as f:
                for key, value in DEFAULT_SETTINGS.items():
                    f.write(f"{key}={value}\n")
            print("Plugin settings file created with default values")
            return True
        return True
    except Exception as e:
        print(f"ERROR creating settings file: {e}")
        return False

def read_settings():
    """قراءة جميع الإعدادات من ملف البلوجين"""
    settings = DEFAULT_SETTINGS.copy()  # البدء بالقيم الافتراضية
    
    try:
        ensure_settings_file()  # التأكد من وجود الملف
        
        if os.path.exists(PLUGIN_SETTINGS_FILE):
            with open(PLUGIN_SETTINGS_FILE, 'r', encoding='utf-8' if PY3 else None) as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line:
                        # تجاهل التعليقات
                        if '#' in line:
                            line = line.split('#')[0].strip()
                        
                        if line:  # التأكد من أن السطر ليس فارغاً بعد إزالة التعليق
                            key, value = line.split('=', 1)
                            settings[key.strip()] = value.strip()
    except Exception as e:
        print(f"ERROR reading plugin settings: {e}")
    
    return settings

def get_setting(key, default=None):
    """الحصول على قيمة إعداد معين من ملف بلوجين"""
    settings = read_settings()
    value = settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))
    print(f"DEBUG - Getting setting: {key} = {value}")
    return value

def save_setting(key, value):
    """حفظ إعداد جديد في ملف بلوجين"""
    try:
        print(f"DEBUG - Saving plugin setting: {key}={value}")
        
        ensure_settings_file()  # التأكد من وجود الملف
        
        # قراءة جميع الإعدادات الحالية
        settings = read_settings()
        
        # تحديث القيمة
        settings[key] = value
        
        # كتابة جميع الإعدادات إلى الملف
        with open(PLUGIN_SETTINGS_FILE, 'w', encoding='utf-8' if PY3 else None) as f:
            for k, v in settings.items():
                f.write(f"{k}={v}\n")
        
        print(f"DEBUG - Successfully saved plugin setting")
        return True
    except Exception as e:
        print(f"ERROR saving plugin setting {key}={value}: {e}")
        return False

def save_all_settings(new_settings):
    """حفظ جميع الإعدادات مرة واحدة"""
    try:
        print(f"DEBUG - Saving all plugin settings")
        
        ensure_settings_file()  # التأكد من وجود الملف
        
        # دمج الإعدادات الجديدة مع الافتراضية
        all_settings = DEFAULT_SETTINGS.copy()
        all_settings.update(new_settings)
        
        # كتابة جميع الإعدادات إلى الملف
        with open(PLUGIN_SETTINGS_FILE, 'w', encoding='utf-8' if PY3 else None) as f:
            for k, v in all_settings.items():
                f.write(f"{k}={v}\n")
        
        print(f"DEBUG - Successfully saved all plugin settings")
        return True
    except Exception as e:
        print(f"ERROR saving all plugin settings: {e}")
        return False

# =============================================
# دوال مساعدة للحصول على إعدادات محددة
# =============================================

def get_restart_emu():
    """الحصول على إعداد إعادة تشغيل المحاكي - True/False"""
    value = get_setting('restart_emu', 'True')
    return value.lower() == 'true'

def get_use_custom_path():
    """الحصول على إعداد استخدام المسار المخصص - True/False"""
    value = get_setting('UseCustomPath', 'False')
    return value.lower() == 'true'

def get_hash_logic():
    """الحصول على منطق حساب الهاش"""
    return get_setting('HashLogic', 'CRC32 Original')

def get_custom_path():
    """الحصول على المسار المخصص"""
    return get_setting('custom_save_path', '/etc/tuxbox/config/SoftCam.Key')

# =============================================
# دالة تصحيح الأخطاء
# =============================================
def debug_trace():
    """طباعة traceback للخطأ الحالي"""
    import traceback
    traceback.print_exc()

# =============================================
# معالج استثناءات عام
# =============================================
def handle_exception(e):
    """معالجة الاستثناءات وعرض معلومات التصحيح"""
    print(f"=== EXCEPTION OCCURRED ===")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")
    debug_trace()
    print(f"=== END EXCEPTION ===")

# =============================================
# دالة الكشف الذكي عن مسارات SoftCam.Key
# =============================================
def detect_softcam_key_paths():
    """الكشف عن جميع مسارات SoftCam.Key الموجودة على النظام"""
    
    # قائمة شاملة بجميع المسارات المحتملة لملفات SoftCam.Key
    all_possible_paths = [
        "/etc/tuxbox/config/SoftCam.Key",
        "/etc/tuxbox/config/oscam/SoftCam.Key",
        "/etc/tuxbox/config/ncam/SoftCam.Key",
        "/etc/tuxbox/config/cccam/SoftCam.Key",
        "/etc/tuxbox/config/mgcamd/SoftCam.Key",
        "/usr/keys/SoftCam.Key",
        "/usr/keys/oscam/SoftCam.Key",
        "/usr/local/keys/SoftCam.Key",
        "/var/keys/SoftCam.Key",
        "/var/oscam/SoftCam.Key",
        "/etc/SoftCam.Key",
        "/var/etc/SoftCam.Key",
        "/var/tuxbox/config/SoftCam.Key",
        "/var/tuxbox/config/oscam/SoftCam.Key",
        "/etc/cccam/SoftCam.Key",
        "/etc/mgcamd/SoftCam.Key",
        "/etc/camd3/SoftCam.Key",
        "/home/root/SoftCam.Key",
        "/root/SoftCam.Key",
        "/usr/emu/SoftCam.Key",
        "/usr/scam/SoftCam.Key",
        "/usr/camscript/SoftCam.Key",
        "/etc/gbox/SoftCam.Key",
        "/etc/wicardd/SoftCam.Key",
        "/etc/cam/SoftCam.Key",
        "/etc/tuxbox/config/SoftCam.Key.bak",
        "/usr/keys/SoftCam.Key.bak",
        "/etc/SoftCam.Key.bak",
    ]
    
    # تصفية فقط المسارات الموجودة فعلياً
    found_paths = []
    for path in all_possible_paths:
        if os.path.exists(path):
            # التحقق من أن الملف قابل للكتابة
            dir_path = os.path.dirname(path)
            if dir_path == '':
                dir_path = '/'
            if os.access(dir_path, os.W_OK):
                found_paths.append(path)
            else:
                print(f"Found but not writable: {path}")
    
    return found_paths


def get_default_path_for_image():
    """الحصول على المسار الافتراضي بناءً على نوع الصورة"""
    
    # محاولة اكتشاف نوع الصورة من ملفات النظام
    image_info = {
        "openatv": "/etc/image-version",
        "openpli": "/etc/issue",
        "openvix": "/etc/vixversion",
        "openbh": "/etc/bhversion",
        "openvision": "/etc/visionversion",
        "pure2": "/etc/pure2version",
        "egami": "/etc/egamiversion",
        "satdreamgr": "/etc/sdversion",
        "blackhole": "/etc/bhversion",
    }
    
    detected_image = "unknown"
    
    # محاولة الكشف عن الصورة
    for image_name, version_file in image_info.items():
        if os.path.exists(version_file):
            detected_image = image_name
            break
    
    print(f"Detected image: {detected_image}")
    
    # مسارات افتراضية بناءً على الصورة المكتشفة
    default_paths = {
        "openatv": "/etc/tuxbox/config/SoftCam.Key",
        "openpli": "/etc/tuxbox/config/SoftCam.Key",
        "openvix": "/etc/tuxbox/config/SoftCam.Key",
        "openbh": "/etc/tuxbox/config/SoftCam.Key",
        "openvision": "/etc/tuxbox/config/SoftCam.Key",
        "pure2": "/etc/tuxbox/config/SoftCam.Key",
        "egami": "/etc/tuxbox/config/SoftCam.Key",
        "satdreamgr": "/etc/tuxbox/config/SoftCam.Key",
        "blackhole": "/etc/tuxbox/config/SoftCam.Key",
        "unknown": "/etc/tuxbox/config/SoftCam.Key",
    }
    
    return default_paths.get(detected_image, "/etc/tuxbox/config/SoftCam.Key")


def ensure_softcam_key_file():
    """التأكد من وجود ملف SoftCam.Key وإنشائه إذا لم يكن موجوداً"""
    
    # 1. البحث عن الملفات الموجودة
    found_paths = detect_softcam_key_paths()
    
    if found_paths:
        print(f"Found existing SoftCam.Key files: {found_paths}")
        return found_paths
    
    # 2. إذا لم توجد ملفات، إنشاء ملف جديد في المسار الافتراضي
    default_path = get_default_path_for_image()
    
    print(f"No SoftCam.Key files found. Creating new file at: {default_path}")
    
    try:
        # التأكد من وجود المجلد
        directory = os.path.dirname(default_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError:
                pass
        
        # إنشاء الملف مع رأسية أساسية
        header = f"""
#" **************************************** "
#           SoftCam.Key file                "
#       Created by E2 BISS Key Editor       "
#        Creation date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}          "
#                                           "
#   Format: F HASH 00 KEY ; Comment         "
#                                           "
#" **************************************** "
=== === === === === === === === === === ===
===             BISS Keys:              ===
=== === === === === === === === === === ===
"""
        
        if PY3:
            with open(default_path, 'w', encoding='utf-8') as f:
                f.write(header)
        else:
            with open(default_path, 'w') as f:
                f.write(header)
        
        print(f"Successfully created SoftCam.Key at: {default_path}")
        
        # جعل الملف قابلاً للكتابة للجميع (اختياري)
        os.chmod(default_path, 0o666)
        
        return [default_path]
        
    except Exception as e:
        print(f"Error creating SoftCam.Key: {e}")
        
        # محاولة مسار بديل
        alternative_paths = [
            "/etc/SoftCam.Key",
            "/usr/keys/SoftCam.Key",
            "/var/keys/SoftCam.Key",
        ]
        
        for alt_path in alternative_paths:
            try:
                directory = os.path.dirname(alt_path)
                if directory and not os.path.exists(directory):
                    try:
                        os.makedirs(directory)
                    except OSError:
                        pass
                
                if PY3:
                    with open(alt_path, 'w', encoding='utf-8') as f:
                        f.write("# SoftCam.Key - Created by E2 BISS Key Editor\n")
                else:
                    with open(alt_path, 'w') as f:
                        f.write("# SoftCam.Key - Created by E2 BISS Key Editor\n")
                
                print(f"Created SoftCam.Key at alternative path: {alt_path}")
                os.chmod(alt_path, 0o666)
                return [alt_path]
                
            except Exception as e2:
                print(f"Failed to create at {alt_path}: {e2}")
                continue
        
        print("ERROR: Could not create SoftCam.Key file!")
        return []


def save_key_to_all_paths(key_line, existing_paths=None):
    """حفظ الشفرة في جميع مسارات SoftCam.Key"""
    
    # استخراج الهاش من سطر المفتاح
    try:
        parts = key_line.split()
        if len(parts) < 4:
            print("❌ Invalid key line format")
            return False, "Invalid key line format"
        
        new_hash = parts[1].upper()
        new_key = parts[3]
        print(f"🔑 New hash: {new_hash}, New key: {new_key}")
    except Exception as e:
        print(f"❌ Error parsing key line: {e}")
        return False, f"Error parsing key line: {e}"
    
    # ✅ تحديد مسارات الحفظ بناءً على إعدادات المستخدم
    target_paths = []
    
    # استخدام الإعدادات من ملف settings
    use_custom_path = get_use_custom_path()
    custom_path = get_custom_path()
    
    if use_custom_path and custom_path:
        # استخدام المسار المخصص فقط
        # إذا كان المسار مجلداً، نضيف اسم الملف
        if os.path.isdir(custom_path):
            target_paths = [os.path.join(custom_path, "SoftCam.Key")]
        elif not custom_path.endswith("SoftCam.Key"):
            # إذا كان مسار ملف مختلف، نستخدمه كما هو
            target_paths = [custom_path]
        else:
            target_paths = [custom_path]
            
        print(f"📁 Using custom save path: {target_paths[0]}")
    else:
        # استخدام المسار الافتراضي
        default_path = "/etc/tuxbox/config/SoftCam.Key"
        target_paths = [default_path]
        print(f"📁 Using default save path: {default_path}")
        
    print(f"📁 Saving to {len(target_paths)} location(s): {target_paths}")
    
    success_paths = []
    failed_paths = []
    replaced_paths = []  # المسارات التي تم استبدال الشفرة فيها
    
    for path in target_paths:
        try:
            # التأكد من وجود المجلد
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"📂 Created directory: {dir_path}")
                except OSError as e:
                    print(f"❌ Failed to create directory {dir_path}: {str(e)}")
                    failed_paths.append((path, "Directory creation failed"))
                    continue
            
            # التحقق من أن الملف قابل للكتابة أو إنشاؤه
            if not os.path.exists(path):
                try:
                    # إنشاء ملف جديد مع رأسية
                    header = f"""# SoftCam.Key
# Created by E2 BISS Key Editor
# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 
# Format: F HASH 00 KEY ; Comment
# BISS Keys:

"""
                    if PY3:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(header)
                    else:
                        with open(path, 'w') as f:
                            f.write(header)
                    print(f"📄 Created new file: {path}")
                except Exception as e:
                    print(f"❌ Failed to create file {path}: {str(e)}")
                    failed_paths.append((path, "File creation failed"))
                    continue
            
            # قراءة المحتوى الحالي
            old_content = ""
            if PY3:
                with open(path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
            else:
                with open(path, 'r') as f:
                    old_content = f.read()
            
            # تقسيم المحتوى إلى أسطر
            lines = old_content.split('\n')
            new_lines = []
            old_key_found = False
            old_key_line = ""
            
            # البحث عن السطر الذي يحمل نفس الهاش
            for line in lines:
                line_stripped = line.strip()
                
                # تجاهل الأسطر الفارغة والتعليقات
                if not line_stripped or line_stripped.startswith('#'):
                    new_lines.append(line)
                    continue
                
                # التحقق من صيغة السطر
                if line_stripped.startswith('F '):
                    parts_line = line_stripped.split()
                    if len(parts_line) >= 4:
                        line_hash = parts_line[1].upper()
                        
                        # إذا كان الهاش مطابقًا، نتجاهل السطر القديم
                        if line_hash == new_hash:
                            old_key_found = True
                            old_key_line = line_stripped
                            old_key = parts_line[3] if len(parts_line) >= 4 else "Unknown"
                            print(f"🔄 Replacing old key at {path}: Hash={line_hash}, OldKey={old_key}, NewKey={new_key}")
                            # لا نضيف السطر القديم إلى new_lines
                            continue
                
                # إضافة جميع الأسطر الأخرى
                new_lines.append(line)
            
            # إضافة السطر الجديد في النهاية (بعد جميع الأسطر الأخرى)
            new_lines.append(key_line)
            
            # كتابة المحتوى المحدث
            new_content = '\n'.join(new_lines)
            
            if PY3:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            else:
                with open(path, 'w') as f:
                    f.write(new_content)
            
            # تسجيل النتيجة
            if old_key_found:
                print(f"✅ Key replaced at: {path}")
                replaced_paths.append((path, old_key_line))
                success_paths.append(path)
            else:
                print(f"✅ Key added at: {path}")
                success_paths.append(path)
            
        except (IOError, OSError) as e:
            print(f"❌ Permission denied: {path} - {e}")
            failed_paths.append((path, "Permission denied"))
            
        except Exception as e:
            print(f"❌ Error saving to {path}: {e}")
            failed_paths.append((path, str(e)))
    
    # إنشاء تقرير النتائج
    if success_paths:
        # بناء رسالة النتائج
        message_parts = []
        
        if replaced_paths:
            message_parts.append(f"🔄 Key replaced in {len(replaced_paths)} location(s)")
            for path, old_key in replaced_paths[:3]:  # عرض أول 3 مسارات فقط
                path_display = os.path.basename(path)
                message_parts.append(f"   📍 {path_display}")
        else:
            message_parts.append(f"✅ Key added to {len(success_paths)} location(s)")
        
        # إضافة معلومات المسار المخصص إذا كان مستخدماً
        if get_use_custom_path():
            custom_path = get_custom_path()
            if len(custom_path) > 50:
                custom_path = "..." + custom_path[-47:]
            message_parts.append(f"📁 Custom path: {custom_path}")
        
        # إضافة معلومات عن الفشل إذا وجدت
        if failed_paths:
            message_parts.append(f"⚠️ Failed in {len(failed_paths)} location(s)")
            for path, error in failed_paths[:3]:  # عرض أول 3 أخطاء فقط
                path_display = os.path.basename(os.path.dirname(path)) + "/" + os.path.basename(path)
                message_parts.append(f"   ❌ {path_display}: {error}")
        
        return True, '\n'.join(message_parts)
    else:
        message = "❌ Failed to save key to any location\n"
        if failed_paths:
            message += "Errors:\n"
            for path, error in failed_paths:
                path_display = os.path.basename(os.path.dirname(path)) + "/" + os.path.basename(path)
                message += f"  {path_display}: {error}\n"
        return False, message.strip()

# =============================================
# جدول CRC32 المطلوب للحساب (مأخوذ من السكريبت الأصلي)
# =============================================
crc_table = array("L")
for byte in range(256):
    crc = 0
    for bit in range(8):
        if (byte ^ crc) & 1:
            crc = (crc >> 1) ^ 0xEDB88320
        else:
            crc >>= 1
        byte >>= 1
    crc_table.append(crc)

def crc32(string):
    """دالة CRC32 المطابقة للسكريبت الأصلي للكايد 2600"""
    value = 0x2600 ^ 0xffffffff
    if PY3:
        if isinstance(string, str):
            # Python 3: str -> bytes
            string = string.encode('utf-8')
        for ch in string:
            value = crc_table[(ch ^ value) & 0xff] ^ (value >> 8)
    else:
        if isinstance(string, unicode):
            # Python 2: unicode -> str
            string = string.encode('utf-8')
        for ch in string:
            value = crc_table[(ord(ch) ^ value) & 0xff] ^ (value >> 8)
    return value ^ 0xffffffff

# =============================================
# دالة إعادة تشغيل المحاكي
# =============================================
def restart_emu():
    """إعادة تشغيل المحاكي بعد حفظ الشفرة - نسخة محسنة"""
    # التحقق من تفعيل الإعادة التلقائية
    auto_restart_enabled = get_restart_emu()
    
    print(f"DEBUG: Auto restart setting from plugin settings: {auto_restart_enabled}")
    
    if not auto_restart_enabled:
        print("Auto restart is disabled. Skipping emulator restart.")
        return False
    
    try:
        print("=" * 50)
        print("Starting emulator restart process...")
        print("=" * 50)
        
        # التحقق من سكريبت softcam لمعرفة المحاكي النشط
        softcam_script_path = '/etc/init.d/softcam'
        active_emu = None
        restart_cmd = None
        
        if os.path.exists(softcam_script_path):
            print(f"Reading softcam script from: {softcam_script_path}")
            try:
                with open(softcam_script_path, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    line_lower = line.lower()
                    if 'oscam' in line_lower:
                        active_emu = 'oscam'
                        restart_cmd = ['/etc/init.d/softcam.OSCam*', 'stop', '&&', 'sleep', '1', '&&', '/etc/init.d/softcam.OSCam*', 'start']
                        print(f"Found OSCam in softcam script")
                        break
                    elif 'ncam' in line_lower:
                        active_emu = 'ncam'
                        restart_cmd = ['/etc/init.d/softcam.ncam*', 'stop', '&&', 'sleep', '1', '&&', '/etc/init.d/softcam.ncam*', 'start']
                        print(f"Found NCam in softcam script")
                        break
                    
                if active_emu:
                    print(f"Active emulator detected from script: {active_emu}")
            except Exception as e:
                print(f"Error reading softcam script: {e}")
        
        # قائمة شاملة لأوامر إعادة تشغيل المحاكي
        restart_commands = []
        
        # إذا تم تحديد المحاكي من السكريبت، أضف أمره أولاً
        if restart_cmd:
            restart_commands.append(restart_cmd)
            print(f"Added primary restart command for {active_emu}")
        
        # إضافة الأوامر العامة للمحاكيات
        restart_commands.extend([
            # أوامر عامة للمحاكيات
            ['/etc/init.d/softcam.OSCam*', 'restart'],  # OSCAM
            ['/etc/init.d/softcam.ncam*', 'restart'],  # NCAM
            ['/etc/init.d/softcam', 'restart'],        # softcam العام
        ])
        
        # محاولة إيجاد وإعادة تشغيل المحاكي الفعلي الموجود على النظام
        print("\nScanning for running emulators...")
        running_emus = []
        
        # قائمة المحاكيات المحتملة
        possible_emus = ['oscam', 'ncam']
        
        for emu in possible_emus:
            try:
                # التحقق من وجود العملية
                if PY3:
                    check_proc = subprocess.run(['pgrep', '-x', emu], 
                                              capture_output=True, text=True, timeout=5)
                else:
                    check_proc = subprocess.Popen(['pgrep', '-x', emu], 
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = check_proc.communicate()
                    check_proc.returncode = check_proc.returncode
                    check_proc.stdout = stdout
                    check_proc.stderr = stderr
                
                if check_proc.returncode == 0:
                    running_emus.append(emu)
                    print(f"Found running emulator: {emu} (PID: {check_proc.stdout.strip()}")
            except:
                continue
        
        # إذا وجدنا محاكي يعمل، ركز على إعادة تشغيله
        if running_emus:
            print(f"Found {len(running_emus)} running emulator(s): {', '.join(running_emus)}")
            
            # ترتيب الأوامر حسب المحاكي الموجود
            prioritized_commands = []
            
            # إضافة أوامر للمحاكيات النشطة أولاً
            for emu in running_emus:
                # إذا كان هذا المحاكي هو المحدد من السكريبت، فهو لديه الأولوية القصوى
                if active_emu and emu.lower() == active_emu.lower():
                    print(f"Prioritizing {emu} (active from softcam script)")
                
                # إضافة أوامر systemd للمحاكي الموجود
                prioritized_commands.append(['systemctl', 'restart', emu])
                prioritized_commands.append(['service', emu, 'restart'])
                prioritized_commands.append([f'/etc/init.d/{emu}', 'restart'])
            
            # دمج القوائم مع الحفاظ على الأولويات
            if prioritized_commands:
                # إضافة أوامر softcam العامة بعد الأولويات
                prioritized_commands.append(['/etc/init.d/softcam', 'restart'])
                prioritized_commands.append(['/usr/bin/restartcam'])
                prioritized_commands.append(['/etc/init.d/camd', 'restart'])
                
                # دمج القوائم مع إعطاء الأولوية للأوامر المحددة
                restart_commands = prioritized_commands + restart_commands
        
        # إزالة التكرارات من القائمة مع الحفاظ على الترتيب
        unique_commands = []
        seen_commands = set()
        
        for cmd in restart_commands:
            cmd_str = ' '.join(cmd)
            if cmd_str not in seen_commands:
                seen_commands.add(cmd_str)
                unique_commands.append(cmd)
        
        restart_commands = unique_commands
        
        # سجل المحاولات
        attempts_log = []
        success = False
        
        print(f"\nTrying {len(restart_commands)} restart commands...")
        print("-" * 40)
        
        # محاولة تنفيذ أوامر إعادة التشغيل
        for idx, cmd in enumerate(restart_commands, 1):
            try:
                cmd_str = ' '.join(cmd)
                print(f"Attempt {idx}: {cmd_str}")
                
                # استخدام shell=True للأوامر المعقدة
                if '&&' in cmd_str or '*' in cmd_str:
                    if PY3:
                        result = subprocess.run(cmd_str, shell=True, 
                                              capture_output=True, text=True, timeout=5)
                    else:
                        result = subprocess.Popen(cmd_str, shell=True, 
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = result.communicate()
                        result.returncode = result.returncode
                        result.stdout = stdout
                        result.stderr = stderr
                else:
                    if PY3:
                        result = subprocess.run(cmd, capture_output=True, 
                                              text=True, timeout=5)
                    else:
                        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE)
                        stdout, stderr = result.communicate()
                        result.returncode = result.returncode
                        result.stdout = stdout
                        result.stderr = stderr
                
                attempts_log.append({
                    'command': cmd_str,
                    'returncode': result.returncode,
                    'stdout': (result.stdout[:100] if result.stdout else '') if PY3 else (result.stdout[:100] if result.stdout else ''),
                    'stderr': (result.stderr[:100] if result.stderr else '') if PY3 else (result.stderr[:100] if result.stderr else '')
                })
                
                if result.returncode == 0:
                    print(f"✓ Success with: {cmd_str}")
                    success = True
                    
                    # التحقق من أن المحاكي يعمل بعد إعادة التشغيل
                    time.sleep(3)  # انتظار قليل
                    
                    # التحقق من جميع المحاكيات المحتملة
                    for emu in possible_emus:
                        try:
                            if PY3:
                                check = subprocess.run(['pgrep', '-x', emu], 
                                                     capture_output=True, text=True, timeout=5)
                            else:
                                check = subprocess.Popen(['pgrep', '-x', emu], 
                                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                stdout, stderr = check.communicate()
                                check.returncode = check.returncode
                            if check.returncode == 0:
                                print(f"✓ Emulator {emu} is running (PID: {check.stdout.strip()}")
                        except:
                            pass
                    
                    break
                else:
                    print(f"✗ Failed (code: {result.returncode})")
                    if result.stderr:
                        error_msg = result.stderr.strip() if PY3 else result.stderr.decode('utf-8', errors='ignore').strip()
                        print(f"  Error: {error_msg[:100]}")
                    
            except subprocess.TimeoutExpired if PY3 else Exception as e:
                if PY3 and isinstance(e, subprocess.TimeoutExpired):
                    print(f"⚠ Timeout for: {cmd_str}")
                    attempts_log.append({
                        'command': cmd_str,
                        'error': 'Timeout'
                    })
                else:
                    print(f"⚠ Timeout for: {cmd_str}")
                    attempts_log.append({
                        'command': cmd_str,
                        'error': 'Timeout'
                    })
                continue
            except (IOError, OSError):
                print(f"⚠ Command not found: {cmd_str}")
                attempts_log.append({
                    'command': cmd_str,
                    'error': 'FileNotFound'
                })
                continue
            except Exception as e:
                error_msg = str(e)
                print(f"⚠ Error: {error_msg[:50]}...")
                attempts_log.append({
                    'command': cmd_str,
                    'error': error_msg[:100]
                })
                continue
        
        # إذا فشلت جميع الأوامر، حاول بإعادة تشغيل الخدمات العامة
        if not success:
            print("\nTrying fallback methods...")
            print("-" * 40)
            
            fallback_methods = [
                ('systemctl daemon-reload', ['systemctl', 'daemon-reload']),
                ('restart softcam service', ['/etc/init.d/softcam', 'restart']),
                ('restart camd service', ['/etc/init.d/camd', 'restart']),
                ('killall softcam processes', ['pkill', '-9', 'softcam']),
                ('killall emu processes', ['pkill', '-9', 'oscam', 'ncam']),
            ]
            
            for method_name, cmd in fallback_methods:
                try:
                    print(f"Fallback: {method_name}")
                    
                    if method_name == 'killall emu processes':
                        # قتل جميع عمليات المحاكيات
                        for emu in possible_emus:
                            subprocess.run(['pkill', '-9', emu], timeout=3)
                        time.sleep(2)
                        # إعادة تشغيل softcam
                        subprocess.run(['/etc/init.d/softcam', 'restart'], timeout=5)
                    else:
                        if isinstance(cmd, list) and '&&' in ' '.join(cmd):
                            if PY3:
                                subprocess.run(' '.join(cmd), shell=True, timeout=10)
                            else:
                                subprocess.Popen(' '.join(cmd), shell=True).wait()
                        else:
                            if PY3:
                                subprocess.run(cmd, timeout=5)
                            else:
                                subprocess.Popen(cmd).wait()
                    
                    print(f"✓ Fallback {method_name} executed")
                    
                    # انتظار وتأكيد
                    time.sleep(3)
                    
                    # التحقق من وجود أي محاكي يعمل
                    for emu in possible_emus:
                        try:
                            if PY3:
                                check = subprocess.run(['pgrep', emu], 
                                                     capture_output=True, text=True, timeout=5)
                            else:
                                check = subprocess.Popen(['pgrep', emu], 
                                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                stdout, stderr = check.communicate()
                                check.returncode = check.returncode
                            if check.returncode == 0:
                                print(f"✓ Found {emu} after fallback")
                                success = True
                        except:
                            continue
                    
                    if success:
                        break
                        
                except Exception as e:
                    error_msg = str(e)
                    print(f"✗ Fallback failed: {error_msg[:50]}...")
                    continue
        
        # تسجيل النتائج
        print("\n" + "=" * 50)
        print("RESTART PROCESS SUMMARY")
        print("=" * 50)
        print(f"Total attempts: {len(attempts_log)}")
        print(f"Success: {'YES' if success else 'NO'}")
        
        if active_emu:
            print(f"Active emulator from softcam script: {active_emu}")
        if running_emus:
            print(f"Running emulators detected: {', '.join(running_emus)}")
        
        if not success:
            print("\nFailed attempts details:")
            for attempt in attempts_log[-5:]:  # عرض آخر 5 محاولات فاشلة
                if 'error' in attempt:
                    print(f"  - {attempt['command'][:50]}... : {attempt['error']}")
                else:
                    print(f"  - {attempt['command'][:50]}... : Code {attempt['returncode']}")
        
        print("\n" + "=" * 50)
        
        if success:
            # إضافة رسالة نجاح إضافية
            print("Emulator restart completed successfully!")
            
            # محاولة تحديث قاعدة بيانات الخدمات
            try:
                print("Updating service database...")
                db = eDVBDB.getInstance()
                db.reloadServicelist()
                print("✓ Service database updated")
            except:
                print("⚠ Could not update service database (non-critical)")
        
        return success
        
    except Exception as e:
        print(f"Critical error in restart_emu: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# =============================================
# BISS-CA 8-Cell Key Validation & Auto-Fix (Correct 2028 Logic)
# Cell d = (a + b + c) & 0xFF
# Cell h = (e + f + g) & 0xFF
# =============================================
def validate_and_fix_biss_8cells(cells):
    """التحقق من صحة الشيفرة وتصحيحها تلقائياً"""
    try:
        a, b, c, d, e, f, g, h = cells
        
        # التحقق من أن جميع الخلايا تحتوي على قيم hex صالحة
        for i, cell in enumerate(cells):
            if not re.match(r'^[0-9A-Fa-f]{2}$', cell):
                return None, False, "Invalid hex pair in cell %d: %s. Must be exactly 2 hex characters." % (i+1, cell)

        # تحويل القيم إلى أعداد
        A = int(a, 16)
        B = int(b, 16)
        C = int(c, 16)
        D = int(d, 16)
        E = int(e, 16)
        F_val = int(f, 16)
        G = int(g, 16)
        H = int(h, 16)

        # حساب القيم الصحيحة
        d_correct = (A + B + C) & 0xFF
        h_correct = (E + F_val + G) & 0xFF

        d_should = "%02X" % d_correct
        h_should = "%02X" % h_correct

        # إنشاء الخلايا المصححة
        fixed_cells = [a, b, c, d_should, e, f, g, h_should]
        fixed_key = "".join(fixed_cells)
        pretty_key = " ".join(fixed_cells)

        # التحقق من الأخطاء
        errors = []
        if d.upper() != d_should:
            errors.append("Cell d → should be %s (was %s)" % (d_should, d))
        if h.upper() != h_should:
            errors.append("Cell h → should be %s (was %s)" % (h_should, h))

        if not errors:
            return fixed_cells, True, "Key is 100%% valid\n%s" % pretty_key

        msg = "\n".join(errors) + "\n\nAuto-fixed key:\n%s" % pretty_key
        return fixed_cells, False, msg

    except Exception as e:
        return None, False, "Validation error: %s" % str(e)

def get_service_info(session):
    """الحصول على معلومات الخدمة الحالية بطريقة محسنة"""
    try:
        service = session.nav.getCurrentService()
        if not service:
            return None, "No service", 0, 0, 0, 0, 0, False

        # الحصول على المرجع الحالي
        service_ref = session.nav.getCurrentlyPlayingServiceReference()
        if not service_ref:
            return None, "No service reference", 0, 0, 0, 0, 0, False

        # الحصول على SID
        sid = service_ref.getUnsignedData(1)  # SID
        
        # الحصول على TSID و ONID و Namespace
        tsid = service_ref.getUnsignedData(2)  # TSID
        onid = service_ref.getUnsignedData(3)  # ONID
        namespace = service_ref.getUnsignedData(4)  # Namespace
        
        # الحصول على اسم القناة
        service_handler = eServiceCenter.getInstance()
        service_info = service_handler.info(service_ref)
        channel_name = service_info.getName(service_ref) if service_info else "Unknown"

        # الحصول على معلومات الخدمة
        info = service.info()
        if not info:
            return channel_name, sid, 0, 0, 0, namespace, False

        # الحصول على PIDs
        vpid = info.getInfo(iServiceInformation.sVideoPID)
        apid = info.getInfo(iServiceInformation.sAudioPID)
        pmtpid = info.getInfo(iServiceInformation.sPMTPID)
        
        # تصحيح القيم غير الصالحة
        if vpid == -1 or vpid >= 8192:
            vpid = 0
        if apid == -1:
            apid = 0
        if pmtpid == -1:
            pmtpid = 0

        # التحقق من حالة التشفير
        is_encrypted = info.getInfo(iServiceInformation.sIsCrypted) == 1

        print("Service Info - Name: %s, SID: %04X, VPID: %04X, APID: %04X, PMT: %04X, Namespace: %08X, Encrypted: %s" % 
              (channel_name, sid, vpid, apid, pmtpid, namespace, is_encrypted))
        
        return channel_name, sid, vpid, apid, pmtpid, namespace, is_encrypted

    except Exception as e:
        print("Error getting service info: %s" % str(e))
        return None, "Error", 0, 0, 0, 0, 0, False

def get_orbital_position(session):
    """الحصول على الموقع المداري للقناة (مأخوذ من السكريبت الأصلي)"""
    ref = session.nav.getCurrentlyPlayingServiceReference()
    orbpos = ref.getUnsignedData(4) >> 16
    if orbpos == 0xFFFF:
        desc = "C"
    elif orbpos == 0xEEEE:
        desc = "T"
    else:
        if orbpos > 1800:
            orbpos = 3600 - orbpos
            h = "W"
        else:
            h = "E"
        desc = ("%d.%d%s") % (orbpos / 10, orbpos % 10, h)
    return desc

def get_hash_original(session):
    """دالة حساب الهاش الأصلية من السكريبت (للكايد 2600)"""
    ref = session.nav.getCurrentlyPlayingServiceReference()
    sid = ref.getUnsignedData(1)
    tsid = ref.getUnsignedData(2)
    onid = ref.getUnsignedData(3)
    namespace = ref.getUnsignedData(4) | 0xA0000000

    # check if we have stripped or full namespace
    if namespace & 0xFFFF == 0:
        # Namespace without frequency - Calculate hash with srvid, tsid, onid and namespace
        data = "%04X%04X%04X%08X" % (sid, tsid, onid, namespace)
    else:
        # Full namespace - Calculate hash with srvid and namespace only
        data = "%04X%08X" % (sid, namespace)
    
    # استخدام دالة CRC32 الأصلية مع البيانات كـ bytes
    data_bytes = binascii.unhexlify(data)
    return crc32(data_bytes)

def get_selected_hash(session):
    """الحصول على الهاش بناءً على المنطق المختار"""
    try:
        channel_name, sid, vpid, apid, pmtpid, namespace, is_encrypted = get_service_info(session)
        
        if sid == 0:
            return None, "Cannot get SID from current service"
        
        # الحصول على منطق الهاش من الإعدادات
        hash_logic = get_hash_logic()
        
        hash_value = None
        logic_name = ""
        
        print("Generating hash with logic: %s" % hash_logic)
        print("Available PIDs - SID: %04X, VPID: %04X, APID: %04X, PMT: %04X, Namespace: %08X" % 
              (sid, vpid, apid, pmtpid, namespace))
        
        if hash_logic == "SID+VPID":
            # SID + VPID
            if vpid > 0:
                hash_value = "%04X%04X" % (sid, vpid)
                logic_name = "SID+VPID"
            else:
                return None, "VPID not available for current service"
                
        elif hash_logic == "CRC32 Original":
            # المنطق الأصلي من السكريبت (للكايد 2600)
            try:
                hash_value_int = get_hash_original(session)
                hash_value = "%08X" % hash_value_int  # Capital letters
                logic_name = "CRC32 ORIGINAL"
            except Exception as e:
                return None, "Error in CRC32 Original: %s" % str(e)
            
        else:
            # Default to CRC32 Original if unknown
            try:
                hash_value_int = get_hash_original(session)
                hash_value = "%08X" % hash_value_int
                logic_name = "CRC32 ORIGINAL"
            except Exception as e:
                return None, "Error in CRC32 Original: %s" % str(e)
            
        if hash_value:
            return hash_value.upper(), logic_name  # تأكيد الحروف الكبيرة
        else:
            return None, "Unknown hash logic: %s" % hash_logic
            
    except Exception as e:
        print("Error in get_selected_hash: %s" % str(e))
        return None, "Error generating hash: %s" % str(e)

# =============================================
# دالة قراءة وعرض شفرات البيس المحفوظة
# =============================================
def get_all_biss_keys():
    """قراءة جميع شفرات البيس المحفوظة في جميع الملفات"""
    try:
        # الحصول على جميع مسارات الملفات
        all_paths = detect_softcam_key_paths()
        
        # إذا لم توجد ملفات، إنشاء ملف جديد
        if not all_paths:
            ensure_softcam_key_file()
            all_paths = detect_softcam_key_paths()
        
        biss_keys = []
        
        for path in all_paths:
            try:
                if PY3:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                else:
                    with open(path, 'r') as f:
                        content = f.read()
                
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    # تجاهل الأسطر الفارغة والتعليقات
                    if not line or line.startswith('#'):
                        continue
                    
                    # البحث عن أسطر شفرات البيس
                    if line.startswith('F '):
                        parts = line.split()
                        if len(parts) >= 4:
                            hash_value = parts[1]
                            key_value = parts[3]
                            
                            # التحقق من أن الشفرة هي شفرة بيس (16 حرف سداسي عشري)
                            if len(key_value) == 16 and all(c in '0123456789ABCDEFabcdef' for c in key_value):
                                # استخراج التعليق إذا وجد
                                comment = ""
                                if len(parts) > 4:
                                    comment = " ".join(parts[4:])
                                    if comment.startswith(';'):
                                        comment = comment[1:].strip()
                                
                                # إضافة الشفرة إلى القائمة
                                biss_keys.append({
                                    'hash': hash_value.upper(),
                                    'key': key_value.upper(),
                                    'comment': comment,
                                    'file': os.path.basename(path),
                                    'line': line_num
                                })
                                
            except Exception as e:
                print(f"Error reading file {path}: {e}")
                continue
        
        return biss_keys
        
    except Exception as e:
        print(f"Error getting BISS keys: {e}")
        return []


# =============================================
# متصفح الملفات المخصص مع تعديل سلوك الأزرار + إضافة وظائف الإعدادات
# =============================================
class FileBrowserScreen(Screen):
    """شاشة متصفح المجلدات المخصصة لاختيار مسار حفظ الشفرات مع إضافة وظائف الإعدادات"""
    
    skin = """
    <screen position="center,center" flags="wfNoBorder" size="1000,490" title="File Browser" backgroundColor="#0D000000" cornerRadius="25">
        <!-- العنوان -->
        <widget name="title" position="center,0" size="450,60" font="Regular;40" halign="center" valign="center" borderWidth="2" borderColor="#22FFFFFF" cornerRadius="15" foregroundColor="red" backgroundColor="#0D000000" />

        <!-- معلومات المسار والإعدادات -->
        <widget name="current_path" position="50,70" size="600,40" font="Regular;28" halign="left" valign="center" foregroundColor="#DD0053" backgroundColor="#0D000000" cornerRadius="10" />

        <!-- قائمة المجلدات فقط -->
        <widget name="filelist" position="50,118" size="720,350" font="Bold;35" itemHeight="45" scrollbarMode="showOnDemand" transparent="0" backgroundColor="#854442" foregroundColor="#FFFFFF" foregroundColorSelected="red" backgroundColorSelected="#21000000" halign="left" valign="center" />
        
        <!-- التاريخ والوقت -->
        <widget source="global.CurrentTime" render="Label" position="750,0" size="250,70" font="Regular;50" halign="center" valign="center" foregroundColor="white" backgroundColor="#0D000000" transparent="1">
            <convert type="ClockToText">Format: %-H:%M:%S</convert>
        </widget>
        <widget source="global.CurrentTime" render="Label" position="0,0" size="250,70" font="Regular;40" halign="center" valign="center" foregroundColor="white" backgroundColor="#0D000000" transparent="1">
            <convert type="ClockToText">Format:%d %b %Y</convert>
        </widget>
        
        <!-- أزرار التحكم -->
        <widget name="key_red" position="860,70" size="180,50" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="red" transparent="1" />
        <eLabel name="red_Button" position="810,80" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="red" />
        <eLabel name="redButtonEffect" position="820,90" zPosition="3" size="10,10" cornerRadius="10" backgroundColor="#0D000000" />
        
        <widget name="key_green" position="860,120" size="180,50" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="green" transparent="1" />
        <eLabel name="green_Button" position="810,130" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="green" />
        <eLabel name="greenButtonEffect" position="820,140" zPosition="3" size="10,10" cornerRadius="10" backgroundColor="#0D000000" />

        <widget name="key_yellow" position="860,170" size="180,50" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="yellow" transparent="1" />
        <eLabel name="yellow_Button" position="810,180" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="yellow" />
        <eLabel name="yellowButtonEffect" position="820,190" zPosition="3" size="10,10" cornerRadius="10" backgroundColor="#0D000000" />
        
        <widget name="key_blue" position="860,220" size="180,50" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="blue" transparent="1" />
        <eLabel name="blue_Button" position="810,230" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="blue" />
        <eLabel name="blueButtonEffect" position="820,240" zPosition="3" size="10,10" cornerRadius="10" backgroundColor="#0D000000" />
        
    </screen>
    """
    
    def __init__(self, session, mode="settings", windowTitle="Select Folder", text="Choose directory for saving", 
                 currDir="/", minFree=None, bookmarks=None, autoAdd=False, 
                 editDir=False, inhibitDirs=None, inhibitMounts=None):
        Screen.__init__(self, session)
        
        self.session = session
        self.mode = mode  # "settings" أو "browse"
        self.windowTitle = windowTitle
        self.text = text
        self.currDir = currDir if currDir and os.path.exists(currDir) else "/"
        self.selectedPath = ""
        self.selecting_directory = True  # نحن نختار المجلدات فقط
        
        # مسار صورة أيقونة المجلد
        self.folder_icon_path = "/usr/lib/enigma2/python/Plugins/Extensions/E2BissKyEditor/icons/folder.png"
        
        # التحقق من وجود صورة المجلد
        self.has_folder_icon = os.path.exists(self.folder_icon_path)
        
        # تعريف العناصر
        self["title"] = Label(windowTitle)
        self["help"] = Label(text)
        self["settings_label"] = Label("")  # ملصق الإعدادات
        self["current_path"] = Label(self.currDir)
        self["status_info"] = Label("")  # معلومات الحالة
        self["filelist"] = MenuList([])
        self["key_red"] = Label("Cancel")
        self["key_green"] = Label("Select")
        self["key_yellow"] = Label("Parent")
        self["key_blue"] = Label("Info")
        
        # خريطة الإجراءات المعدلة
        self["actions"] = ActionMap(["ColorActions", "OkCancelActions", "DirectionActions", "MenuActions"],
            {
                "cancel": self.cancel,
                "red": self.cancel,
                "green": self.saveCurrentDirectory,  # زر أخضر لحفظ المجلد الحالي
                "yellow": self.goParent,
                "blue": self.showSettingsInfo,  # زر أزرق لعرض معلومات الإعدادات
                "ok": self.openSelectedItem,  # زر OK لفتح المجلد المحدد
                "left": self.left,
                "right": self.right,
                "up": self.up,
                "down": self.down,
                "menu": self.toggleSettingsMode,  # زر Menu للتبديل بين وضعي الإعدادات والتصفح
            }, -1)
        
        self.onLayoutFinish.append(self.initScreen)

    def initScreen(self):
        """تهيئة الشاشة بناءً على الوضع"""
        if self.mode == "settings":
            self.setupSettingsMode()
        else:
            self.setupBrowseMode()
        
        self.loadDirectory()

    def setupSettingsMode(self):
        """تهيئة وضع الإعدادات"""
        self["title"].setText("Save Path Settings")
        self["help"].setText("Configure where to save BISS keys")
        self["key_green"].setText("Set Path")
        self["key_blue"].setText("Reset")
        self["key_yellow"].setText("Parent")
        self.updateSettingsDisplay()

    def setupBrowseMode(self):
        """تهيئة وضع التصفح"""
        self["title"].setText(self.windowTitle)
        self["help"].setText(self.text)
        self["key_green"].setText("Select Folder")
        self["key_blue"].setText("Info")
        self["key_yellow"].setText("Parent")
        self.updateHelpText()

    def updateSettingsDisplay(self):
        """تحديث عرض الإعدادات"""
        try:
            default_path = "/etc/tuxbox/config/SoftCam.Key"
            
            # استخدام الإعدادات من ملف البلوجين
            use_custom_path = get_use_custom_path()
            custom_path = get_custom_path()
            
            if use_custom_path and custom_path:
                current_path = custom_path
                # تقصير المسار الطويل
                if len(current_path) > 60:
                    display_path = "..." + current_path[-57:]
                else:
                    display_path = current_path
                self["current_path"].setText(f"📁 Path: {display_path}")
                self["status_info"].setText("✅ Custom Path Active")
                self["status_info"].instance.setForegroundColor(gRGB(0x98FB98))  # أخضر فاتح
            else:
                self["current_path"].setText(f"📁 Path: {default_path}")
                self["status_info"].setText("ℹ️ Default Path Active")
                self["status_info"].instance.setForegroundColor(gRGB(0x4169E1))  # أزرق
            
            # معلومات إضافية
            self["settings_label"].setText("Save Location Configuration")
            
        except Exception as e:
            print(f"Error updating settings display: {e}")
            self["current_path"].setText("Error loading path")
            self["status_info"].setText("Error")

    def updateHelpText(self):
        """تحديث نص التعليمات بناءً على الوضع الحالي"""
        help_text = f"OK: Open Folder | Green: Select Current Folder | Folders: {len(self.file_items) if hasattr(self, 'file_items') else 0}"
        self["key_green"].setText("Select Folder")
        self["help"].setText(help_text)

    def toggleSettingsMode(self):
        """التبديل بين وضعي الإعدادات والتصفح"""
        if self.mode == "settings":
            # التبديل إلى وضع التصفح
            self.mode = "browse"
            self.setupBrowseMode()
        else:
            # التبديل إلى وضع الإعدادات
            self.mode = "settings"
            self.setupSettingsMode()
        
        self.loadDirectory()

    def loadDirectory(self):
        """تحميل المجلدات فقط من المجلد الحالي مع أيقونات"""
        try:
            if not os.path.exists(self.currDir):
                self.currDir = "/"
            
            # الحصول على قائمة المحتويات (المجلدات فقط)
            contents = []
            
            # إضافة ".." للرجوع للخلف
            parent_dir = os.path.dirname(self.currDir.rstrip('/'))
            if parent_dir and parent_dir != self.currDir:
                if self.has_folder_icon:
                    # استخدام الصورة مع المسار
                    display_name = f"\u200B{parent_dir}\u200C"  # استخدام أحرف غير مرئية للحفاظ على الهيكل
                    contents.append((display_name, parent_dir, "dir", True))  # True يعني أنه مجلد أعلى
                else:
                    contents.append(("📁 .. (Parent Directory)", parent_dir, "dir", True))
            
            # إضافة المجلدات فقط
            try:
                items = os.listdir(self.currDir)
                for item in sorted(items):
                    full_path = os.path.join(self.currDir, item)
                    if os.path.isdir(full_path):
                        if self.has_folder_icon:
                            # استخدام الصورة مع اسم المجلد
                            display_name = f"\u200B{item}\u200C"
                            contents.append((display_name, full_path, "dir", False))
                        else:
                            contents.append((f"📁 {item}/", full_path, "dir", False))
            except (OSError, PermissionError):
                pass
            
            # تحديث القائمة
            self.file_items = contents
            
            # إنشاء قائمة العرض مع الأيقونات إذا كانت الصورة موجودة
            display_list = []
            for item in contents:
                display_name = item[0]
                if self.has_folder_icon and item[3]:  # مجلد أعلى
                    display_list.append(f".. (Parent Directory)")
                elif self.has_folder_icon:
                    display_list.append(f"{item[0].split(chr(0x200C))[0]}")  # استخراج الاسم فقط
                else:
                    display_list.append(item[0])
            
            self["filelist"].setList(display_list)
            
        except Exception as e:
            print(f"Error loading directory: {e}")

    def getSelectedItem(self):
        """الحصول على العنصر المحدد"""
        try:
            index = self["filelist"].getSelectedIndex()
            if 0 <= index < len(self.file_items):
                return self.file_items[index]
        except:
            pass
        return None

    def openSelectedItem(self):
        """زر OK: فتح المجلد المحدد فقط"""
        selected = self.getSelectedItem()
        if selected:
            path, full_path, item_type = selected[1], selected[1], selected[2]
            
            if item_type == "dir":
                # الانتقال إلى المجلد
                self.currDir = full_path
                self.loadDirectory()
                # تحديث عرض المسار الحالي
                self["current_path"].setText(self.currDir)
        else:
            # إذا لم يكن هناك عنصر محدد، نبقى في المجلد الحالي
            pass

    def saveCurrentDirectory(self):
        """زر أخضر: حفظ المجلد الحالي كمسار للحفظ"""
        if self.mode == "settings":
            # في وضع الإعدادات، نختار المجلد الحالي للإعدادات
            self.setCurrentPathAsSavePath()
        else:
            # في وضع التصفح العادي، نستخدم المجلد الحالي
            if os.path.isdir(self.currDir):
                # استخدام المجلد الحالي
                path = os.path.join(self.currDir, "SoftCam.Key")
                self.close(path)
            else:
                # إذا لم يكن مجلداً صالحاً
                self.session.open(
                    MessageBox,
                    "Invalid folder selected",
                    MessageBox.TYPE_ERROR,
                    timeout=2
                )

    def setCurrentPathAsSavePath(self):
        """تعيين المسار الحالي كمسار حفظ للشفرات"""
        if os.path.isdir(self.currDir):
            # استخدام المجلد الحالي
            path = os.path.join(self.currDir, "SoftCam.Key")
        else:
            path = os.path.join(self.currDir, "SoftCam.Key")
        
        # حفظ المسار المختار في ملف بلوجين
        try:
            # حفظ المسار المخصص
            save_setting('custom_save_path', path)
            # تفعيل استخدام المسار المخصص
            save_setting('UseCustomPath', 'True')
            
            # تحديث العرض
            self.updateSettingsDisplay()
            
            # عرض رسالة تأكيد
            self.session.open(
                MessageBox,
                f"✓ Save path updated!\n\nKeys will be saved to:\n{path}",
                MessageBox.TYPE_INFO,
                timeout=3
            )
            
        except Exception as e:
            print(f"Error saving path: {e}")
            self.session.open(
                MessageBox,
                f"Error saving path: {str(e)}",
                MessageBox.TYPE_ERROR,
                timeout=2
            )

    def goParent(self):
        """زر أصفر: الانتقال إلى المجلد الأعلى"""
        parent = os.path.dirname(self.currDir.rstrip('/'))
        if parent and os.path.exists(parent):
            self.currDir = parent
            self.loadDirectory()
            # تحديث عرض المسار الحالي
            self["current_path"].setText(self.currDir)

    def showSettingsInfo(self):
        """زر أزرق: عرض معلومات مفصلة عن المسارات أو إعادة التعيين"""
        if self.mode == "settings":
            # في وضع الإعدادات، زر أزرق لإعادة التعيين
            self.resetToDefault()
        else:
            # في وضع التصفح، زر أزرق لعرض معلومات المجلد
            self.showFolderInfo()

    def resetToDefault(self):
        """إعادة تعيين إلى المسار الافتراضي"""
        try:
            # تعطيل استخدام المسار المخصص
            save_setting('UseCustomPath', 'False')
            # إفراغ المسار المخصص
            save_setting('custom_save_path', '')
            
            self.updateSettingsDisplay()
            self.session.open(
                MessageBox,
                "✓ Reset to default path\n\nKeys will be saved to:\n/etc/tuxbox/config/SoftCam.Key",
                MessageBox.TYPE_INFO,
                timeout=3
            )
            
        except Exception as e:
            print(f"Error resetting to default: {e}")

    def showFolderInfo(self):
        """عرض معلومات عن المجلد الحالي"""
        try:
            if os.path.isdir(self.currDir):
                # الحصول على معلومات المجلد
                dir_items = os.listdir(self.currDir)
                folder_count = 0
                
                for item in dir_items:
                    full_path = os.path.join(self.currDir, item)
                    if os.path.isdir(full_path):
                        folder_count += 1
                
                # الحصول على مساحة القرص
                try:
                    stat = os.statvfs(self.currDir)
                    free_space = (stat.f_bavail * stat.f_frsize) / (1024 * 1024 * 1024)  # GB
                    total_space = (stat.f_blocks * stat.f_frsize) / (1024 * 1024 * 1024)  # GB
                    used_space = total_space - free_space
                    used_percent = (used_space / total_space * 100) if total_space > 0 else 0
                    
                    space_info = f"Disk Space: {used_space:.1f}GB / {total_space:.1f}GB ({used_percent:.1f}% used)\nFree: {free_space:.1f}GB"
                except:
                    space_info = "Disk Space: Unknown"
                
                info_text = f"📁 Current Folder\n\nPath: {self.currDir}\n\nFolders: {folder_count}\n\n{space_info}"
                
                self.session.open(
                    MessageBox,
                    info_text,
                    MessageBox.TYPE_INFO,
                    timeout=5
                )
        except Exception as e:
            print(f"Error getting folder info: {e}")
            self.session.open(
                MessageBox,
                f"Error: {str(e)}",
                MessageBox.TYPE_ERROR,
                timeout=2
            )

    def cancel(self):
        """زر أحمر: إلغاء العملية"""
        self.close(None)

    def left(self):
        """حركة يسار"""
        self["filelist"].pageUp()

    def right(self):
        """حركة يمين"""
        self["filelist"].pageDown()

    def up(self):
        """حركة أعلى"""
        self["filelist"].up()

    def down(self):
        """حركة أسفل"""
        self["filelist"].down()

# ==========================
# OptionMenu Screen
# ==========================
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Screens.MessageBox import MessageBox
import os
import threading
import subprocess
from enigma import eTimer

# رابط التثبيت الموحد
INSTALLER_CMD = (
    "wget -q -O - "
    "https://raw.githubusercontent.com/ismail9875/E2BissKeyEditor/refs/heads/main/installer.sh "
    "| /bin/bash"
)

class OptionMenuScreen(Screen):
    """شاشة الإعدادات مع خيارات بسيطة"""
    
    skin = """
    <screen position="center,center" flags="wfNoBorder" cornerRadius="20" size="850,400" backgroundColor="#0D000000" title="BISS Key Editor Options">
        <widget name="title" position="center,5" size="500,60" font="Regular;35" borderWidth="1" borderColor="red" halign="center" valign="center" foregroundColor="#FFD700" backgroundColor="#3C110011" cornerRadius="15" transparent="1" />
        <widget name="menu" position="50,80" size="750,250" itemHeight="50" font="bold,28" scrollbarMode="showOnDemand" />
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 50" zPosition="5" noWrap="1" valign="center" halign="center" position="630,0" render="Label" size="220,70" source="global.CurrentTime" transparent="1">
            <convert type="ClockToText">Format: %-H:%M:%S</convert>
        </widget>
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 40" zPosition="5" noWrap="1" valign="center" halign="left" position="20,0" render="Label" size="250,70" source="global.CurrentTime" transparent="1">
            <convert type="ClockToText">Format:%d %b %Y</convert>
        </widget>
        <widget name="key_yellow" position="360,350" size="140,40" zPosition="1" font="Regular;25" halign="center" valign="center" backgroundColor="#63000000" foregroundColor="white" transparent="1" />
        <eLabel name="yellow_button" position="340,360" size="20,20" zPosition="2" cornerRadius="10" backgroundColor="yellow" />
        <widget name="key_green"  position="520,350" size="140,40" zPosition="1" font="Regular;25" halign="center" valign="center" backgroundColor="#63000000" foregroundColor="white" transparent="1" />
        <eLabel name="green_button" position="500,360" size="20,20" zPosition="2" cornerRadius="10" backgroundColor="green" />
        <widget name="key_red" position="200,350" size="140,40" zPosition="1" font="Regular;25" halign="center" valign="center" backgroundColor="#63000000" foregroundColor="white" transparent="1" />
        <eLabel name="red_button" position="180,360" size="20,20" zPosition="2" cornerRadius="10" backgroundColor="red" />
        <widget name="info" position="50,310" size="750,25" font="Regular;22" halign="center" valign="center" foregroundColor="#98FB98" backgroundColor="#3C110011" transparent="1" />
    </screen>
    """

    # ===============================
    # INIT
    # ===============================
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.update_message = None

        self["title"] = Label("BISS Key Editor Options")
        self["menu"] = MenuList([])
        self["info"] = Label("Use UP/DOWN and OK")
        self["key_red"] = Label("Cancel")
        self["key_yellow"] = Label("Update")
        self["key_green"] = Label("Save")

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "ok": self.keyOk,
                "cancel": self.keyCancel,
                "red": self.keyCancel,
                "yellow": self.keyYellow,
                "green": self.keySave,
                "up": self.keyUp,
                "down": self.keyDown,
            },
            -2
        )

        self.onShown.append(self.setupMenuList)

    # ===============================
    # Menu
    # ===============================
    def setupMenuList(self):
        ensure_settings_file()
        self["menu"].setList([
            "Hash Logic: %s" % get_hash_logic(),
            "Auto Restart: %s" % ("Enabled" if get_restart_emu() else "Disabled"),
            "Custom Path: %s" % ("Enabled" if get_use_custom_path() else "Disabled"),
            "Version: %s" % self.get_current_version(),
        ])
        self["info"].setText("OK = change | Yellow = update")

    # ===============================
    # Current version
    # ===============================
    def get_current_version(self):
        path = "/usr/lib/enigma2/python/Plugins/Extensions/E2BissKeyEditor/version"
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read().strip()
        except Exception as e:
            print("[BISS] get_current_version error:", e)
        return "0.0.0"

    # ===============================
    # Manual update (installer.sh)
    # ===============================
    def keyYellow(self):
        self.session.openWithCallback(
            self.confirmUpdate,
            MessageBox,
            "سيتم فحص الإصدار وتنفيذ التحديث إن وجد.\n\nهل تريد المتابعة؟",
            MessageBox.TYPE_YESNO
        )

    def confirmUpdate(self, answer):
        if not answer:
            return

        self.update_message = self.session.open(
            MessageBox,
            "جاري تنفيذ التحديث...\n\nيرجى الانتظار",
            MessageBox.TYPE_INFO,
            timeout=2
        )

        from enigma import eConsoleAppContainer
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.updateFinished)
        self.container.execute(INSTALLER_CMD)

    def updateFinished(self, retval):
        if self.update_message:
            self.update_message.close()

        if retval == 0:
            self.session.open(
                MessageBox,
                "تم تنفيذ عملية التحديث بنجاح.\n\nقد يتم إعادة تشغيل الواجهة تلقائيًا.",
                MessageBox.TYPE_INFO,
                timeout=6
            )
        else:
            self.session.open(
                MessageBox,
                "فشل التحديث أو لا يوجد إصدار أحدث.\n\nتم الحفاظ على النسخة الحالية.",
                MessageBox.TYPE_WARNING,
                timeout=6
            )

    # ===============================
    # UI actions
    # ===============================
    def keyOk(self):
        item = self["menu"].getCurrent()
        if not item:
            return

        if item.startswith("Hash Logic"):
            save_setting(
                "HashLogic",
                "SID+VPID" if get_hash_logic() == "CRC32 Original" else "CRC32 Original"
            )
            self.setupMenuList()

        elif item.startswith("Auto Restart"):
            save_setting("restart_emu", "False" if get_restart_emu() else "True")
            self.setupMenuList()

        elif item.startswith("Version"):
            self.keyYellow()

    def keySave(self):
        self.close()

    def keyCancel(self):
        self.close()

    def keyUp(self):
        self["menu"].up()

    def keyDown(self):
        self["menu"].down()

    def restart_gui(self, answer=False):
        if answer:
            from Screens.Standby import TryQuitMainloop
            self.session.open(TryQuitMainloop, 3)

# =============================================
# شاشة EditBissKey
# =============================================
class EditBissKeyScreen(Screen):
    """شاشة تعديل شفرة BISS موجودة"""
    
    skin = """
    <screen position="center,center" flags="wfNoBorder" size="1000,600" title="Edit BISS Key" backgroundColor="#0D000000" cornerRadius="15" >
        <widget name="title" borderWidth="1" borderColor="#FFFF17" position="center,0" size="450,60" font="Regular;40" halign="center" valign="center" cornerRadius="15" foregroundColor="red" backgroundColor="#0D000000" />
        <widget name="help" position="center,70" size="880,40" font="Regular;25" halign="center" valign="center" cornerRadius="15" foregroundColor="yellow" backgroundColor="#0D000000" />
        
        <!-- معلومات الهاش والشفر الحالية -->
        <widget name="hash_label" position="50,120" size="150,40" font="Regular;25" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" zPosition="5" transparent="1" />
        <widget name="hash_value" transparent="1" position="50,120" size="900,40" font="Regular;25" halign="right" valign="center" foregroundColor="red" backgroundColor="#3DFF1515" zPosition="3" cornerRadius="10" />
        <eLabel name="hash_Effect" cornerRadius="24" position="40,120" size="920,40" backgroundColor="#0DCCEEFF" zPosition="1"/>
        
        <!-- عرض الخلايا بشكل أفقي >
        <widget name="cells_display" position="50,180" size="900,40" font="Regular;30" halign="center" valign="center" foregroundColor="white" backgroundColor="#0D000000" transparent="1" /-->
        
        <!-- خلايا منفصلة لعرض القيم -->
        <widget name="cell_0" position="120,230" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_1" position="220,230" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_2" position="320,230" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_3" position="420,230" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_4" position="520,230" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_5" position="620,230" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_6" position="720,230" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_7" position="820,230" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        
        <!-- أزرار الأحرف بشكل عمودي على اليسار -->
        <widget name="key_a" position="10,220" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_b" position="10,280" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_c" position="10,340" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_d" position="10,400" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_e" position="10,460" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_f" position="10,520" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        
        <!-- حقل التعليق -->
        <widget name="comment_label" zPosition="5" position="50,170" size="150,40" font="Regular;25" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" transparent="1" />
        <widget name="comment_value" zPosition="2" transparent="1" position="50,170" size="900,40" font="Regular;25" halign="right" valign="center" foregroundColor="red" backgroundColor="#3DFF1515" cornerRadius="10" />
        <eLabel name="Comment_Effect" cornerRadius="24" position="40,170" size="920,40" backgroundColor="#0DCCEEFF" zPosition="1"/>

        <!-- معلومات الملف -->
        <widget name="file_info" position="center,380" size="600,40" font="Regular;22" halign="left" valign="center" foregroundColor="#98FB98" backgroundColor="#0D000000" transparent="1" />
        
        <!-- الساعة والتاريخ -->
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 50" zPosition="5" noWrap="1" valign="center" halign="center" position="750,0" render="Label" size="250,70" source="global.CurrentTime" transparent="1"  >
            <convert type="ClockToText">Format: %-H:%M:%S</convert>
        </widget>
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 40" zPosition="5" noWrap="1" valign="center" halign="center" position="0,0" render="Label" size="250,70" source="global.CurrentTime" transparent="1"  >
            <convert type="ClockToText">Format:%d %b %Y</convert>
        </widget>
        
        <!-- أزرار التحكم -->
        <widget name="key_red" position="830,300" size="180,40" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="red" transparent="1" />
        <eLabel name="red_Button" position="770,310" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="red" />


        <widget name="key_green" position="830,360" size="180,40" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="green" transparent="1" />
        <eLabel name="green_Button" position="770,370" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="green" />
        
        <widget name="key_yellow" position="830,420" size="180,40" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="yellow" transparent="1" />
        <eLabel name="yellow_Button" position="770,430" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="yellow" />
        
        <widget name="key_blue" position="830,480" size="180,40" zPosition="1" font="Regular;30" halign="lefr" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="blue" transparent="1" />
        <eLabel name="blue_Button" position="770,490" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="blue" />


    </screen>
    """

    def __init__(self, session, biss_key_data):
        """
        تهيئة شاشة تعديل شفرة BISS
        
        Args:
            session: جلسة enigma2
            biss_key_data: قاموس يحتوي على بيانات الشفرة
                {
                    'hash': 'ABCDEF12',
                    'key': '0011223344556677',
                    'comment': 'تعليق الشفرة',
                    'file': 'SoftCam.Key',
                    'line': 10
                }
        """
        Screen.__init__(self, session)
        self.session = session
        self.biss_key_data = biss_key_data
        
        # تحميل الشفرة من البيانات الممررة
        self.cells = []
        self.original_cells = []
        self.original_key = biss_key_data.get('key', '')
        self.original_comment = biss_key_data.get('comment', '')
        
        # تقسيم الشفرة إلى خلايا (8 خلايا كل خلية 2 حرف)
        if len(self.original_key) == 16:
            self.cells = [self.original_key[i:i+2].upper() for i in range(0, 16, 2)]
            self.original_cells = self.cells.copy()
        else:
            # إذا كانت الشفرة غير صحيحة، نستخدم قيم افتراضية
            self.cells = ["00", "00", "00", "00", "00", "00", "00", "00"]
            self.original_cells = self.cells.copy()
        
        self.current_cell = 0
        self.current_char = 0
        self.selected_letter_index = 0
        
        # قائمة الأحرف
        self.letters = ["A", "B", "C", "D", "E", "F"]
        
        # تعريف جميع العناصر
        self["title"] = Label("Edit BISS Key")
        self["help"] = Label("Use 0-9 keys for numbers, UP/DOWN for letters, LEFT/RIGHT for cells")
        
        # معلومات الهاش
        self["hash_label"] = Label("Hash ")
        self["hash_value"] = Label(biss_key_data.get('hash', ''))
        
        # عرض الخلايا
        self["cells_display"] = Label("")
        
        # تعريف الخلايا المنفصلة
        for i in range(8):
            self["cell_%d" % i] = Label("00")
        
        # أزرار الأحرف بشكل عمودي
        self["key_a"] = Label("A")
        self["key_b"] = Label("B")
        self["key_c"] = Label("C")
        self["key_d"] = Label("D")
        self["key_e"] = Label("E")
        self["key_f"] = Label("F")
        
        # حقل التعليق
        self["comment_label"] = Label("Comment ")
        self["comment_value"] = Label(self.original_comment if self.original_comment else "(No comment)")
        
        # معلومات الملف
        file_info = f"📁 File: {biss_key_data.get('file', '')} | 📄 Line: {biss_key_data.get('line', 0)}"
        self["file_info"] = Label(file_info)
        
        # أزرار التحكم
        self["key_green"] = Label("Save")
        self["key_yellow"] = Label("Comment")
        self["key_blue"] = Label("Validate")
        self["key_red"] = Label("Cancel")
        
        # خريطة الإجراءات
        self["actions"] = ActionMap(["ColorActions", "OkCancelActions", "DirectionActions", "NumberActions", "MenuActions"],
            {
                "up": self.up,
                "down": self.down,
                "left": self.left,
                "right": self.right,
                "ok": self.input_selected_letter,
                "cancel": self.close,
                "green": self.save_changes,
                "red": self.close,
                "yellow": self.edit_comment,
                "blue": self.validate_key,
                "0": lambda: self.input_char("0"),
                "1": lambda: self.input_char("1"),
                "2": lambda: self.input_char("2"),
                "3": lambda: self.input_char("3"),
                "4": lambda: self.input_char("4"),
                "5": lambda: self.input_char("5"),
                "6": lambda: self.input_char("6"),
                "7": lambda: self.input_char("7"),
                "8": lambda: self.input_char("8"),
                "9": lambda: self.input_char("9"),
            }, -1)
        
        # إضافة أزرار الأحرف إلى ActionMap للإدخال المباشر
        self.letter_actions = {
            "a": lambda: self.input_char("A"),
            "b": lambda: self.input_char("B"),
            "c": lambda: self.input_char("C"),
            "d": lambda: self.input_char("D"),
            "e": lambda: self.input_char("E"),
            "f": lambda: self.input_char("F"),
        }
        
        for key, action in self.letter_actions.items():
            self["actions"].actions[key] = action
        
        self.onLayoutFinish.append(self.update_display)
        self.onLayoutFinish.append(self.update_letter_buttons)
        
        print(f"EditBissKeyScreen initialized with key: {self.original_key}")

    def update_display(self):
        """تحديث جميع عناصر العرض"""
        try:
            # تحديث الخلايا المنفصلة
            for i in range(8):
                cell_widget = self["cell_%d" % i]
                cell_value = self.cells[i] if i < len(self.cells) else "00"
                cell_widget.setText(cell_value)
                
                # تحديث الألوان بناءً على الخلية النشطة
                if i == self.current_cell:
                    # الخلية النشطة - خلفية زرقاء فاتحة ونص أسود
                    cell_widget.instance.setBackgroundColor(gRGB(0x926F34))  # ذهبي
                    cell_widget.instance.setForegroundColor(gRGB(0xFFFFFF))  # أبيض
                else:
                    # الخلايا غير النشطة - خلفية داكنة ونص أبيض
                    cell_widget.instance.setBackgroundColor(gRGB(0xE8FFF1))  # بني داكن
                    cell_widget.instance.setForegroundColor(gRGB(0x000000))  # أصفر فاقع
            
            # تحديث ألوان أزرار الأحرف
            self.update_letter_buttons()
            
            # تحديث العرض النصي للخلايا
            cells_display = " ".join(self.cells)
            self["cells_display"].setText(f"Key: {cells_display}")
            
            # تحديث التعليق
            comment = self["comment_value"].text
            if not comment or comment == "(No comment)":
                self["comment_value"].setText(self.original_comment if self.original_comment else "(No comment)")
            
        except Exception as e:
            print(f"Error in update_display: {e}")

    def update_letter_buttons(self):
        """تحديث ألوان أزرار الأحرف بناءً على الحرف المختار"""
        try:
            for i, letter in enumerate(self.letters):
                widget = self["key_%s" % letter.lower()]
                if i == self.selected_letter_index:
                    # الحرف المختار - خلفية برتقالية ونص أسود
                    widget.instance.setBackgroundColor(gRGB(0xFFA500))  # برتقالي
                    widget.instance.setForegroundColor(gRGB(0x000000))  # أسود
                else:
                    # الأحرف غير المختارة - خلفية زرقاء ونص أبيض
                    widget.instance.setBackgroundColor(gRGB(0x4169E1))  # أزرق ملكي
                    widget.instance.setForegroundColor(gRGB(0xFFFFFF))  # أبيض
        except Exception as e:
            print(f"Error updating letter buttons: {e}")

    def is_valid_hex_char(self, char):
        """التحقق إذا كان الحرف مسموحاً به (0-9, A-F, a-f)"""
        return char in '0123456789ABCDEFabcdef'

    def input_char(self, char):
        """إدخال حرف في الموضع الحالي مع التحقق من الصحة"""
        # التحقق من أن الحرف مسموح به
        if not self.is_valid_hex_char(char):
            return
        
        # تحويل الحرف إلى uppercase للتأكد من التنسيق
        char = char.upper()
        
        if self.current_cell < len(self.cells):
            current_value = self.cells[self.current_cell]
            
            if self.current_char == 0:
                # استبدال الحرف الأول
                new_value = char + current_value[1]
            else:
                # استبدال الحرف الثاني
                new_value = current_value[0] + char
            
            self.cells[self.current_cell] = new_value
            
            # الانتقال التلقائي للحرف التالي
            self.auto_move_next()
            
            self.update_display()

    def input_selected_letter(self):
        """إدخال الحرف المحدد بالأزرار العلوية والسفلية"""
        selected_letter = self.letters[self.selected_letter_index]
        self.input_char(selected_letter)

    def auto_move_next(self):
        """الانتقال التلقائي للحرف أو الخلية التالية"""
        if self.current_char == 0:
            # الانتقال إلى الحرف الثاني في نفس الخلية
            self.current_char = 1
        else:
            # الانتقال إلى الخلية التالية (الحرف الأول)
            self.current_char = 0
            if self.current_cell < len(self.cells) - 1:
                self.current_cell += 1

    def up(self):
        """التنقل بين الأحرف (UP) - للأعلى في العمود"""
        if self.selected_letter_index > 0:
            self.selected_letter_index -= 1
        else:
            self.selected_letter_index = len(self.letters) - 1  # الانتقال للأسفل
        self.update_display()

    def down(self):
        """التنقل بين الأحرف (DOWN) - للأسفل في العمود"""
        if self.selected_letter_index < len(self.letters) - 1:
            self.selected_letter_index += 1
        else:
            self.selected_letter_index = 0  # الانتقال للأعلى
        self.update_display()

    def left(self):
        """الانتقال إلى الخلية السابقة (LEFT) - في الصف الأفقي"""
        if self.current_cell > 0:
            self.current_cell -= 1
            self.current_char = 0
            self.update_display()

    def right(self):
        """الانتقال إلى الخلية التالية (RIGHT) - في الصف الأفقي"""
        if self.current_cell < len(self.cells) - 1:
            self.current_cell += 1
            self.current_char = 0
            self.update_display()

    def edit_comment(self):
        """تحرير التعليق (الزر الأصفر)"""
        try:
            from Screens.VirtualKeyBoard import VirtualKeyBoard
            
            current_comment = self["comment_value"].text
            if current_comment == "(No comment)":
                current_comment = ""
            
            self.session.openWithCallback(
                self.comment_edited,
                VirtualKeyBoard,
                title="Edit Comment",
                text=current_comment
            )
        except Exception as e:
            print(f"Error opening virtual keyboard: {e}")
            self.session.open(
                MessageBox,
                "Virtual keyboard not available",
                MessageBox.TYPE_ERROR,
                timeout=2
            )

    def comment_edited(self, new_comment):
        """Callback بعد تحرير التعليق"""
        if new_comment is not None:
            if new_comment.strip():
                self["comment_value"].setText(new_comment.strip())
            else:
                self["comment_value"].setText("(No comment)")

    def validate_key(self):
        """التحقق من صحة الشفرة (الزر الأزرق)"""
        try:
            # التحقق من صحة الشيفرة وتصحيحها تلقائياً
            fixed_cells, valid, msg = validate_and_fix_biss_8cells(self.cells)
            
            if fixed_cells is None:
                self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR, timeout=3)
                return
            
            if valid:
                message = f"✅ Key is 100% valid!\n\n"
            else:
                message = f"⚠️ Key needs correction:\n{msg}\n\n"
            
            # إضافة معلومات الشفرة
            key_display = " ".join(fixed_cells)
            message += f"🔑 Key: {key_display}\n"
            message += f"🔐 Full: {''.join(fixed_cells)}"
            
            # إذا كانت هناك تصحيحات، تحديث الخلايا
            if not valid:
                self.cells = fixed_cells
                self.update_display()
                message += "\n\n✓ Auto-corrected key has been applied"
            
            self.session.open(
                MessageBox,
                message,
                MessageBox.TYPE_INFO if valid else MessageBox.TYPE_WARNING,
                timeout=4
            )
            
        except Exception as e:
            print(f"Error validating key: {e}")
            self.session.open(
                MessageBox,
                f"Validation error: {str(e)}",
                MessageBox.TYPE_ERROR,
                timeout=3
            )

    def save_changes(self):
        """حفظ التعديلات (الزر الأخضر)"""
        try:
            # التحقق إذا كان هناك تغييرات
            current_key = "".join(self.cells)
            current_comment = self["comment_value"].text
            if current_comment == "(No comment)":
                current_comment = ""
            
            # التحقق من التغييرات
            changes_detected = False
            changes_list = []
            
            if current_key != self.original_key:
                changes_detected = True
                changes_list.append(f"Key changed: {self.original_key} → {current_key}")
            
            if current_comment != self.original_comment:
                changes_detected = True
                old_comment = self.original_comment if self.original_comment else "(No comment)"
                new_comment = current_comment if current_comment else "(No comment)"
                changes_list.append(f"Comment changed: {old_comment} → {new_comment}")
            
            if not changes_detected:
                self.session.open(
                    MessageBox,
                    "No changes detected. Nothing to save.",
                    MessageBox.TYPE_INFO,
                    timeout=2
                )
                return
            
            # تأكيد الحفظ
            self.session.openWithCallback(
                self.confirm_save,
                MessageBox,
                "Save changes?\n\n" + "\n".join(changes_list),
                MessageBox.TYPE_YESNO
            )
            
        except Exception as e:
            print(f"Error in save_changes: {e}")
            self.session.open(
                MessageBox,
                f"Error preparing save: {str(e)}",
                MessageBox.TYPE_ERROR,
                timeout=3
            )

    def confirm_save(self, result):
        """تأكيد الحفظ"""
        if result:
            try:
                # التحقق من صحة الشفرة قبل الحفظ
                fixed_cells, valid, msg = validate_and_fix_biss_8cells(self.cells)
                
                if fixed_cells is None:
                    self.session.open(MessageBox, f"Cannot save: {msg}", MessageBox.TYPE_ERROR, timeout=3)
                    return
                
                # استخدام الشفرة المصححة
                self.cells = fixed_cells
                final_key = "".join(self.cells)
                final_comment = self["comment_value"].text
                if final_comment == "(No comment)":
                    final_comment = ""
                
                # الحصول على بيانات الشفرة الأصلية
                hash_value = self.biss_key_data.get('hash', '')
                file_path = self.biss_key_data.get('file', '')
                line_num = self.biss_key_data.get('line', 0)
                
                if not hash_value or not file_path:
                    self.session.open(MessageBox, "Missing hash or file information", MessageBox.TYPE_ERROR, timeout=3)
                    return
                
                # تحديث الشفرة في الملف
                success, message = self.update_key_in_file(
                    hash_value, 
                    final_key, 
                    final_comment, 
                    file_path, 
                    line_num
                )
                
                if success:
                    # تحديث البيانات الأصلية
                    self.original_key = final_key
                    self.original_comment = final_comment
                    self.original_cells = self.cells.copy()
                    
                    # إعادة تشغيل المحاكي إذا كان الإعداد مفعلاً
                    if get_restart_emu():
                        restart_success = restart_emu()
                        if restart_success:
                            message += "\n🔄 Emulator restarted automatically"
                        else:
                            message += "\n⚠️ Emulator restart failed"
                    else:
                        message += "\n⏸️ Emulator restart skipped (Auto Restart: Disabled)"
                    
                    self.session.open(
                        MessageBox,
                        message,
                        MessageBox.TYPE_INFO,
                        timeout=5
                    )
                    
                    # إغلاق الشاشة بعد الحفظ الناجح
                    self.close()
                else:
                    self.session.open(
                        MessageBox,
                        f"Save failed:\n{message}",
                        MessageBox.TYPE_ERROR,
                        timeout=4
                    )
                    
            except Exception as e:
                print(f"Error in confirm_save: {e}")
                self.session.open(
                    MessageBox,
                    f"Save error: {str(e)}",
                    MessageBox.TYPE_ERROR,
                    timeout=3
                )

    def update_key_in_file(self, hash_value, new_key, new_comment, file_path, line_num):
        """
        تحديث الشفرة في الملف المحدد
        
        Args:
            hash_value: قيمة الهاش
            new_key: الشفرة الجديدة (16 حرف)
            new_comment: التعليق الجديد
            file_path: مسار الملف أو اسم الملف (من البيانات الأصلية)
            line_num: رقم السطر (استرشادي)
        
        Returns:
            tuple: (success, message)
        """
        try:
            # ✅ تحديد مسار الحفظ بناءً على إعدادات المستخدم
            save_path = self.get_save_path()
            
            if not save_path:
                return False, "No save path configured. Please set save path in settings."
            
            print(f"DEBUG: Using save path: {save_path}")
            print(f"DEBUG: Hash: {hash_value}, Key: {new_key}")
            
            # التأكد من وجود المجلد
            dir_path = os.path.dirname(save_path)
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"DEBUG: Created directory: {dir_path}")
                except Exception as e:
                    return False, f"Cannot create directory {dir_path}: {str(e)}"
            
            # قراءة الملف الحالي إذا كان موجوداً
            file_exists = os.path.exists(save_path)
            lines = []
            
            if file_exists:
                try:
                    if PY3:
                        with open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    else:
                        with open(save_path, 'r') as f:
                            content = f.read()
                    lines = content.split('\n')
                except Exception as e:
                    return False, f"Cannot read file {save_path}: {str(e)}"
            else:
                print(f"DEBUG: File does not exist, creating new: {save_path}")
                # إنشاء محتوى أولي للملف الجديد
                header = f"""# SoftCam.Key
    # Updated by E2 BISS Key Editor
    # {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    # 
    # Format: F HASH 00 KEY ; Comment
    # BISS Keys:
    
    """
                lines = header.split('\n')
            
            # إنشاء سطر المفتاح الجديد
            new_key_line = f"F {hash_value} 00 {new_key}"
            if new_comment and new_comment.strip():
                new_key_line += f" ; {new_comment.strip()}"
            
            updated = False
            found_line_num = -1
            
            # البحث عن السطر الحالي الذي يحتوي على نفس الهاش
            for i in range(len(lines)):
                line = lines[i].strip()
                if line.startswith('F '):
                    parts = line.split()
                    if len(parts) >= 4:
                        line_hash = parts[1].upper()
                        if line_hash == hash_value.upper():
                            # ✅ وجدنا السطر القديم، نستبدله
                            lines[i] = new_key_line
                            updated = True
                            found_line_num = i + 1
                            print(f"DEBUG: Replaced line {found_line_num} (hash: {hash_value})")
                            break
            
            if not updated:
                # ✅ إذا لم نجد السطر، نضيفه في نهاية قسم BISS Keys
                print(f"DEBUG: Key not found, adding as new line")
                
                # البحث عن مكان مناسب للإضافة (بعد عنوان BISS Keys إذا وجد)
                insert_pos = len(lines)
                for i, line in enumerate(lines):
                    if "BISS Keys:" in line or "=== BISS Keys ===" in line:
                        insert_pos = i + 2  # إضافة بعد سطر فارغ من العنوان
                        break
                
                lines.insert(insert_pos, new_key_line)
                found_line_num = insert_pos + 1
                print(f"DEBUG: Added new key at line {found_line_num}")
            
            # ✅ كتابة المحتوى المحدث
            try:
                if PY3:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                else:
                    with open(save_path, 'w') as f:
                        f.write('\n'.join(lines))
                
                print(f"DEBUG: File saved successfully: {save_path}")
                
                # ✅ أيضًا، تحديث في الملف الأصلي إذا كان مختلفاً
                if file_path and os.path.exists(file_path) and file_path != save_path:
                    print(f"DEBUG: Also updating original file: {file_path}")
                    self.update_original_file(file_path, hash_value, new_key_line)
                
                # ✅ بناء رسالة النجاح
                old_key_display = " ".join([self.original_key[i:i+2] for i in range(0, 16, 2)])
                new_key_display = " ".join([new_key[i:i+2] for i in range(0, 16, 2)])
                
                message = f"✅ Key saved successfully!\n\n"
                message += f"🔑 Hash: {hash_value}\n"
                message += f"🔐 Old Key: {old_key_display}\n"
                message += f"🔐 New Key: {new_key_display}\n"
                message += f"📁 File: {os.path.basename(save_path)}"
                
                if found_line_num > 0:
                    message += f"\n📄 Line: {found_line_num}"
                
                if new_comment and new_comment.strip():
                    message += f"\n💬 Comment: {new_comment.strip()}"
                
                # ✅ إضافة معلومات المسار
                if get_use_custom_path():
                    message += f"\n📍 Custom path: {save_path}"
                else:
                    message += f"\n📍 Default path: {save_path}"
                
                return True, message
                
            except PermissionError:
                return False, f"Permission denied: Cannot write to {save_path}"
            except Exception as e:
                print(f"DEBUG: Error writing file: {e}")
                return False, f"Error saving file: {str(e)}"
                    
        except Exception as e:
            print(f"DEBUG: Error in update_key_in_file: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error updating key: {str(e)}"
    
    def get_save_path(self):
        try:
            use_custom_path = get_use_custom_path()
            custom_path = get_custom_path()
            
            if use_custom_path and custom_path:
                # استخدام المسار المخصص من FileBrowserScreen
                # إذا كان المسار مجلداً، نضيف اسم الملف
                if os.path.isdir(custom_path):
                    save_path = os.path.join(custom_path, "SoftCam.Key")
                elif not custom_path.endswith("SoftCam.Key"):
                    # إذا كان مسار ملف مختلف، نستخدمه كما هو
                    save_path = custom_path
                else:
                    save_path = custom_path
                
                print(f"DEBUG: Using custom save path: {save_path}")
                return save_path
            else:
                # استخدام المسار الافتراضي
                default_path = "/etc/tuxbox/config/SoftCam.Key"
                print(f"DEBUG: Using default save path: {default_path}")
                return default_path
                
        except Exception as e:
            print(f"DEBUG: Error getting save path: {e}")
            # استرجاع المسار الافتراضي في حالة الخطأ
            return "/etc/tuxbox/config/SoftCam.Key"

    def update_original_file(self, original_path, hash_value, new_key_line):
        """
        تحديث الملف الأصلي أيضاً (للتأكيد)
        
        Args:
            original_path: مسار الملف الأصلي
            hash_value: قيمة الهاش
            new_key_line: سطر المفتاح الجديد
        """
        try:
            if not os.path.exists(original_path):
                print(f"DEBUG: Original file not found: {original_path}")
                return
            
            print(f"DEBUG: Updating original file: {original_path}")
            
            if PY3:
                with open(original_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            else:
                with open(original_path, 'r') as f:
                    content = f.read()
            
            lines = content.split('\n')
            updated = False
            
            for i in range(len(lines)):
                line = lines[i].strip()
                if line.startswith('F '):
                    parts = line.split()
                    if len(parts) >= 4:
                        line_hash = parts[1].upper()
                        if line_hash == hash_value.upper():
                            lines[i] = new_key_line
                            updated = True
                            print(f"DEBUG: Updated original file line {i+1}")
                            break
            
            if updated:
                if PY3:
                    with open(original_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                else:
                    with open(original_path, 'w') as f:
                        f.write('\n'.join(lines))
                print(f"DEBUG: Original file updated successfully")
                
        except Exception as e:
            print(f"DEBUG: Error updating original file: {e}")


# =============================================
# شاشة عرض شفرات البيس المحفوظة - نسخة متقدمة
# =============================================
class BissKeysBrowserScreen(Screen):
    """شاشة عرض شفرات البيس مع 3 قوائم متوازية و pagination"""
    
    skin = """
    <screen position="center,center" flags="wfNoBorder" cornerRadius="25" size="1200,800" backgroundColor="#0D000000" title="BISS Keys Browser">
        <!-- العنوان -->
        <widget name="title" position="center,5" borderColor="red" borderWidth="1" size="500,50" font="Regular;35" halign="center" valign="center" foregroundColor="#FFD700" backgroundColor="#0D110011" cornerRadius="15" />
        
        <!-- Selector Widget -->
        <!--widget name="selector" position="50,130" size="1100,50" font="Regular;30" halign="center" valign="center" foregroundColor="#FF6347" backgroundColor="#0D110011" cornerRadius="10" /-->
        
        <!-- قائمة الهاشات -->
        <widget name="hash_list" backgroundColor="#0D330016" backgroundColorSelected="white" halign="center" valign="center" itemHeight="45" font="bold,26" foregroundColorSelected="black" position="50,200" size="220,450" />
        
        <!-- قائمة الشفرات -->
        <widget name="key_list" backgroundColor="#0D330016" backgroundColorSelected="white" halign="center" valign="center" itemHeight="45" font="bold,26" foregroundColorSelected="black" position="270,200" size="430,450" />
        
        <!-- قائمة التعليقات -->
        <widget name="comment_list" backgroundColor="#0D330016" backgroundColorSelected="white" halign="left" valign="center" itemHeight="45" font="bold,26" foregroundColorSelected="black" position="700,200" size="400,450" scrollbarMode="showOnDemand" />
        
        <!-- العناوين -->
        <widget name="hash_title" position="50,160" size="200,30" font="Regular;28" halign="center" valign="center" foregroundColor="black" backgroundColor="#3C110011" transparent="1" zPosition="3"/>
        <widget name="key_title" position="375,160" size="200,30" font="Regular;28" halign="center" valign="center" foregroundColor="black" backgroundColor="#3C110011" transparent="1" zPosition="3" />
        <widget name="comment_title" position="700,160" size="250,30" font="Regular;28" halign="center" valign="center" foregroundColor="black" backgroundColor="#3C110011" transparent="1" zPosition="3" />
        
        <eLabel name="header" position="50,150" size="1050,40" zPosition="2" backgroundColor="#0DCCEEFF"/>
        
        <!-- معلومات الملف -->
        <widget name="file_info" position="50,660" size="1100,40" font="Regular;22" halign="center" valign="center" foregroundColor="#FFD700" backgroundColor="#3C110011" transparent="1" />
        
        <!-- العداد ومعلومات الصفحة -->
        <widget name="counter" position="50,100" size="1100,35" font="Regular;25" halign="center" valign="center" foregroundColor="#4169E1" backgroundColor="#3C110011" transparent="1" />
        
        <!-- معلومات الصفحة -->
        <widget name="page_info" position="50,700" size="1100,30" font="Regular;22" halign="center" valign="center" foregroundColor="#FFD700" backgroundColor="#3C110011" transparent="1" />
        
        <!-- الساعة والتاريخ -->
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 50" zPosition="5" noWrap="1" valign="center" halign="center" position="930,5" render="Label" size="250,70" source="global.CurrentTime" transparent="1">
            <convert type="ClockToText">Format: %-H:%M:%S</convert>
        </widget>
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 40" zPosition="5" noWrap="1" valign="center" halign="left" position="20,5" render="Label" size="250,70" source="global.CurrentTime" transparent="1">
            <convert type="ClockToText">Format:%d %b %Y</convert>
        </widget>
        
        <!-- أزرار التحكم -->
        <widget name="key_red" transparent="1" position="250,750" size="140,40" zPosition="1" font="Regular;25" halign="center" valign="center" backgroundColor="#63000000" foregroundColor="white" />
        <eLabel name="red_button" position="230,760" size="20,20" zPosition="2" cornerRadius="10" backgroundColor="red" />

        <widget name="key_green" transparent="1" position="430,750" size="140,40" zPosition="1" font="Regular;25" halign="center" valign="center" backgroundColor="#63000000" foregroundColor="white" />
        <eLabel name="green_button" position="410,760" size="20,20" zPosition="2" cornerRadius="10" backgroundColor="green" />
        
        <widget name="key_yellow" transparent="1" position="610,750" size="140,40" zPosition="1" font="Regular;25" halign="center" valign="center" backgroundColor="#63000000" foregroundColor="white" />
        <eLabel name="yellow_button" position="590,760" size="20,20" zPosition="2" cornerRadius="10" backgroundColor="yellow" />
        
        <widget name="key_blue" transparent="1" position="810,750" size="140,40" zPosition="1" font="Regular;25" halign="center" valign="center" backgroundColor="#63000000" foregroundColor="white" />
        <eLabel name="blue_button" position="790,760" size="20,20" zPosition="2" cornerRadius="10" backgroundColor="blue" />

    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.biss_keys = []
        self.current_page = 0
        self.items_per_page = 10  # عدد العناصر في كل صفحة
        self.current_index = 0
        self.displayed_keys = []  # المفاتيح المعروضة في الصفحة الحالية
        
        # تعريف العناصر
        self["title"] = Label("BISS Keys Browser")
        
        # القوائم الثلاثة
        self["hash_list"] = MenuList([])
        self["key_list"] = MenuList([])
        self["comment_list"] = MenuList([])
        
        # العناوين
        self["hash_title"] = Label("HASH")
        self["key_title"] = Label("KEY")
        self["comment_title"] = Label("COMMENT")
        
        # معلومات إضافية
        self["file_info"] = Label("")
        self["counter"] = Label("Loading keys...")
        self["page_info"] = Label("")  # إضافة عنصر معلومات الصفحة
        
        # أزرار التحكم
        self["key_green"] = Label("View")
        self["key_yellow"] = Label("Delete")
        self["key_blue"] = Label("Edit")
        self["key_red"] = Label("Back")
        
        # خريطة الإجراءات - إضافة أزرار التنقل بين الصفحات
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions", "ChannelSelectActions"],
            {
                "ok": self.view_selected_key,
                "green": self.view_selected_key,
                "yellow": self.delete_selected_key,
                "blue": self.edit_selected_key,
                "cancel": self.close,
                "red": self.close,
                "up": self.up,
                "down": self.down,
                "left": self.page_up,  # الصفحة السابقة
                "right": self.page_down,  # الصفحة التالية
                "pageUp": self.page_up,
                "pageDown": self.page_down,
                "nextBouquet": self.next_page,  # الصفحة التالية (زر CH+)
                "prevBouquet": self.prev_page,  # الصفحة السابقة (زر CH-)
                "menu": self.show_all_details,
            }, -2)
        
        self.onShown.append(self.load_keys)

    def load_keys(self):
        """تحميل جميع شفرات البيس"""
        try:
            self.biss_keys = get_all_biss_keys()
            
            if not self.biss_keys:
                self["counter"].setText("No BISS keys found")
                self["page_info"].setText("")  # تفريغ معلومات الصفحة
                self.clear_lists()
                return
            
            # إعادة تعيين الصفحة الحالية
            self.current_page = 0
            self.current_index = 0
            
            # حساب عدد الصفحات
            total_pages = max(1, (len(self.biss_keys) + self.items_per_page - 1) // self.items_per_page)
            
            # تحديث العداد
            self["counter"].setText(f"Found {len(self.biss_keys)} BISS key(s)")
            
            # تحديث معلومات الصفحة
            self.update_page_info()
            
            # تحميل الصفحة الأولى
            self.load_current_page()
            
        except Exception as e:
            print(f"Error loading BISS keys: {e}")
            self["counter"].setText(f"Error: {str(e)[:50]}")
            self["page_info"].setText("")  # تفريغ معلومات الصفحة
            self.clear_lists()

    def load_current_page(self):
        """تحميل وتحديث المحتوى للصفحة الحالية"""
        try:
            if not self.biss_keys:
                return
            
            # حساب بداية ونهاية العناصر في الصفحة الحالية
            start_idx = self.current_page * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(self.biss_keys))
            
            # استخراج المفاتيح للصفحة الحالية
            self.displayed_keys = self.biss_keys[start_idx:end_idx]
            
            # إنشاء القوائم الثلاثة للصفحة الحالية
            hash_list = []
            key_list = []
            comment_list = []
            
            for key in self.displayed_keys:
                # قائمة الهاشات
                hash_list.append(key['hash'])
                
                # قائمة الشفرات (بتنسيق جميل)
                formatted_key = " ".join([key['key'][i:i+2] for i in range(0, 16, 2)])
                key_list.append(formatted_key)
                
                # قائمة التعليقات
                comment = key['comment'] if key['comment'] else "(No comment)"
                # تقصير التعليق إذا كان طويلاً
                if len(comment) > 30:
                    comment = comment[:27] + "..."
                comment_list.append(comment)
            
            # تعيين القوائم
            self["hash_list"].setList(hash_list)
            self["key_list"].setList(key_list)
            self["comment_list"].setList(comment_list)
            
            # تحديد العنصر الأول
            self.current_index = 0
            self["hash_list"].moveToIndex(0)
            self["key_list"].moveToIndex(0)
            self["comment_list"].moveToIndex(0)
            
            # تحديث معلومات الملف للعنصر الأول
            self.update_file_info()
            
        except Exception as e:
            print(f"Error loading current page: {e}")

    def clear_lists(self):
        """تفريغ جميع القوائم"""
        self["hash_list"].setList(["No keys"])
        self["key_list"].setList(["No keys"])
        self["comment_list"].setList(["No keys"])

    def update_page_info(self):
        """تحديث معلومات الصفحة الحالية"""
        if not self.biss_keys:
            self["page_info"].setText("")
            return
        
        # حساب معلومات الصفحة
        total_pages = max(1, (len(self.biss_keys) + self.items_per_page - 1) // self.items_per_page)
        current_page = self.current_page + 1
        
        # تحديث معلومات الصفحة
        page_info = f"📄 Page {current_page}/{total_pages} "
        
        # إضافة تلميحات التنقل
        if total_pages > 1:
            page_info += "| 📍 Use LEFT/RIGHT or CH+/CH- to navigate pages"
        
        self["page_info"].setText(page_info)

    def up(self):
        """تحريك السهم لأعلى في جميع القوائم"""
        if self.current_index > 0:
            self.current_index -= 1
            self["hash_list"].moveToIndex(self.current_index)
            self["key_list"].moveToIndex(self.current_index)
            self["comment_list"].moveToIndex(self.current_index)
            self.update_file_info()

    def down(self):
        """تحريك السهم لأسفل في جميع القوائم"""
        if self.current_index < len(self.displayed_keys) - 1:
            self.current_index += 1
            self["hash_list"].moveToIndex(self.current_index)
            self["key_list"].moveToIndex(self.current_index)
            self["comment_list"].moveToIndex(self.current_index)
            self.update_file_info()

    def page_up(self):
        """الصفحة لأعلى أو الانتقال للصفحة السابقة"""
        # إذا كنا في أول صفحة، ننتقل للصفحة الأخيرة (دورة)
        if self.current_page == 0:
            self.current_page = max(0, (len(self.biss_keys) - 1) // self.items_per_page)
        else:
            self.current_page -= 1
        
        # إعادة تعيين الفهرس للعنصر الأول في الصفحة الجديدة
        self.current_index = 0
        
        # تحديث المحتوى
        self.load_current_page()
        self.update_page_info()

    def page_down(self):
        """الصفحة لأسفل أو الانتقال للصفحة التالية"""
        # إذا كنا في آخر صفحة، ننتقل للصفحة الأولى (دورة)
        total_pages = max(1, (len(self.biss_keys) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page >= total_pages - 1:
            self.current_page = 0
        else:
            self.current_page += 1
        
        # إعادة تعيين الفهرس للعنصر الأول في الصفحة الجديدة
        self.current_index = 0
        
        # تحديث المحتوى
        self.load_current_page()
        self.update_page_info()

    def next_page(self):
        """الانتقال للصفحة التالية (زر CH+)"""
        total_pages = max(1, (len(self.biss_keys) + self.items_per_page - 1) // self.items_per_page)
        
        if total_pages > 1:
            if self.current_page < total_pages - 1:
                self.current_page += 1
            else:
                self.current_page = 0  # العودة للصفحة الأولى
            
            # إعادة تعيين الفهرس للعنصر الأول في الصفحة الجديدة
            self.current_index = 0
            
            # تحديث المحتوى
            self.load_current_page()
            self.update_page_info()

    def prev_page(self):
        """الانتقال للصفحة السابقة (زر CH-)"""
        total_pages = max(1, (len(self.biss_keys) + self.items_per_page - 1) // self.items_per_page)
        
        if total_pages > 1:
            if self.current_page > 0:
                self.current_page -= 1
            else:
                self.current_page = total_pages - 1  # الانتقال للصفحة الأخيرة
            
            # إعادة تعيين الفهرس للعنصر الأول في الصفحة الجديدة
            self.current_index = 0
            
            # تحديث المحتوى
            self.load_current_page()
            self.update_page_info()

    def update_file_info(self):
        """تحديث معلومات الملف للعنصر المحدد"""
        try:
            if 0 <= self.current_index < len(self.displayed_keys):
                key = self.displayed_keys[self.current_index]
                file_info = f"📁 {key['file']} | 📄 Line: {key['line']}"
                self["file_info"].setText(file_info)
        except Exception as e:
            print(f"Error updating file info: {e}")
            self["file_info"].setText("")

    def view_selected_key(self):
        """عرض تفاصيل الشفرة المحددة"""
        try:
            if 0 <= self.current_index < len(self.displayed_keys):
                key = self.displayed_keys[self.current_index]
                
                # تنسيق الشفرة بشكل جميل
                formatted_key = " ".join([key['key'][i:i+2] for i in range(0, 16, 2)])
                
                # حساب الرقم الفعلي للشفرة
                global_index = self.current_page * self.items_per_page + self.current_index
                
                # بناء رسالة التفاصيل
                details = f"🔍 BISS Key Details\n"
                details += f"{'='*40}\n"
                details += f"🔢 Position: {global_index + 1} of {len(self.biss_keys)}\n"
                details += f"📄 Page: {self.current_page + 1}/{(len(self.biss_keys) + self.items_per_page - 1) // self.items_per_page}\n"
                details += f"🔑 Hash: {key['hash']}\n"
                details += f"🔐 Key: {formatted_key}\n"
                details += f"📁 File: {key['file']}\n"
                details += f"📄 Line: {key['line']}\n"
                
                if key['comment'] and key['comment'] != "(No comment)":
                    details += f"💬 Comment: {key['comment']}\n"
                
                # عرض التفاصيل
                self.session.open(
                    MessageBox,
                    details,
                    MessageBox.TYPE_INFO,
                    timeout=6
                )
                
        except Exception as e:
            print(f"Error viewing key details: {e}")
            self.session.open(
                MessageBox,
                f"Error viewing key details: {str(e)[:50]}",
                MessageBox.TYPE_ERROR,
                timeout=3
            )

    def edit_selected_key(self):
        """تحرير الشفرة المحددة"""
        try:
            if 0 <= self.current_index < len(self.displayed_keys):
                key = self.displayed_keys[self.current_index]
                
                # فتح شاشة EditBissKeyScreen مع بيانات الشفرة المحددة
                self.session.openWithCallback(
                    self.on_edit_complete,
                    EditBissKeyScreen,
                    key
                )
                
        except Exception as e:
            print(f"Error editing key: {e}")
            self.session.open(
                MessageBox,
                f"Error editing key: {str(e)[:50]}",
                MessageBox.TYPE_ERROR,
                timeout=3
            )
    
    def on_edit_complete(self, result=None):
        """Callback بعد إغلاق شاشة التحرير"""
        # إعادة تحميل القوائم لعرض التحديثات
        self.load_keys()

    def delete_selected_key(self):
        """حذف الشفرة المحددة من الملف (الزر الأصفر)"""
        try:
            if 0 <= self.current_index < len(self.displayed_keys):
                key = self.displayed_keys[self.current_index]
                
                # حساب الرقم الفعلي للشفرة
                global_index = self.current_page * self.items_per_page + self.current_index
                
                # عرض رسالة تأكيد قبل الحذف
                confirm_msg = f"Are you sure you want to delete this BISS key?\n\n"
                confirm_msg += f"🔢 Position: {global_index + 1} of {len(self.biss_keys)}\n"
                confirm_msg += f"📄 Page: {self.current_page + 1}/{(len(self.biss_keys) + self.items_per_page - 1) // self.items_per_page}\n"
                confirm_msg += f"🔑 Hash: {key['hash']}\n"
                
                # تنسيق الشفرة بشكل جميل
                formatted_key = " ".join([key['key'][i:i+2] for i in range(0, 16, 2)])
                confirm_msg += f"🔐 Key: {formatted_key}\n"
                
                if key['comment'] and key['comment'] != "(No comment)":
                    confirm_msg += f"💬 Comment: {key['comment']}\n"
                
                confirm_msg += f"📁 File: {key['file']}\n"
                confirm_msg += f"📄 Line: {key['line']}\n\n"
                confirm_msg += "⚠️ This action cannot be undone!"
                
                self.session.openWithCallback(
                    lambda result: self.confirm_delete(result, key, global_index),
                    MessageBox,
                    confirm_msg,
                    MessageBox.TYPE_YESNO
                )
            else:
                self.session.open(
                    MessageBox,
                    "No key selected",
                    MessageBox.TYPE_WARNING,
                    timeout=2
                )
                
        except Exception as e:
            print(f"Error in delete_selected_key: {e}")
            self.session.open(
                MessageBox,
                f"Error preparing deletion: {str(e)}",
                MessageBox.TYPE_ERROR,
                timeout=3
            )
    
    def confirm_delete(self, result, key, global_index):
        """تأكيد الحذف"""
        if result:
            try:
                # حذف الشفرة من الملف
                success, message = self.delete_key_from_file(key['hash'], key['file'])
                
                if success:
                    # إعادة تشغيل المحاكي إذا كان الإعداد مفعلاً
                    if get_restart_emu():
                        restart_success = restart_emu()
                        if restart_success:
                            message += "\n🔄 Emulator restarted automatically"
                        else:
                            message += "\n⚠️ Emulator restart failed"
                    else:
                        message += "\n⏸️ Emulator restart skipped (Auto Restart: Disabled)"
                    
                    self.session.open(
                        MessageBox,
                        message,
                        MessageBox.TYPE_INFO,
                        timeout=5
                    )
                    
                    # إعادة تحميل القوائم بعد الحذف
                    self.load_keys()
                else:
                    self.session.open(
                        MessageBox,
                        f"Deletion failed:\n{message}",
                        MessageBox.TYPE_ERROR,
                        timeout=4
                    )
                    
            except Exception as e:
                print(f"Error in confirm_delete: {e}")
                self.session.open(
                    MessageBox,
                    f"Deletion error: {str(e)}",
                    MessageBox.TYPE_ERROR,
                    timeout=3
                )
    
    def delete_key_from_file(self, hash_value, file_path):
        """
        حذف الشفرة من الملف المحدد
        
        Args:
            hash_value: قيمة الهاش المراد حذفها
            file_path: مسار الملف أو اسم الملف
        
        Returns:
            tuple: (success, message)
        """
        try:
            # تحديد مسار الملف
            save_path = self.get_save_path(file_path)
            
            if not save_path:
                return False, "No save path configured. Please set save path in settings."
            
            print(f"DEBUG: Deleting key from file: {save_path}")
            print(f"DEBUG: Hash to delete: {hash_value}")
            
            # التحقق من وجود الملف
            if not os.path.exists(save_path):
                return False, f"File not found: {save_path}"
            
            # قراءة الملف
            try:
                if PY3:
                    with open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                else:
                    with open(save_path, 'r') as f:
                        content = f.read()
                lines = content.split('\n')
            except Exception as e:
                return False, f"Cannot read file {save_path}: {str(e)}"
            
            # البحث عن السطر الذي يحتوي على الهاش المطلوب وحذفه
            deleted = False
            deleted_line_num = -1
            original_line = ""
            
            for i in range(len(lines)):
                line = lines[i].strip()
                if line.startswith('F '):
                    parts = line.split()
                    if len(parts) >= 4:
                        line_hash = parts[1].upper()
                        if line_hash == hash_value.upper():
                            # حفظ معلومات السطر المحذوف
                            original_line = line
                            deleted_line_num = i + 1
                            
                            # حذف السطر
                            lines.pop(i)
                            deleted = True
                            print(f"DEBUG: Deleted line {deleted_line_num} (hash: {hash_value})")
                            break
            
            if not deleted:
                return False, f"Key with hash {hash_value} not found in file"
            
            # كتابة المحتوى المحدث
            try:
                if PY3:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                else:
                    with open(save_path, 'w') as f:
                        f.write('\n'.join(lines))
                
                print(f"DEBUG: File updated successfully after deletion")
                
                # بناء رسالة النجاح
                message = f"✅ Key deleted successfully!\n\n"
                message += f"🗑️ Hash: {hash_value}\n"
                
                if deleted_line_num > 0:
                    message += f"📄 Deleted from line: {deleted_line_num}\n"
                
                message += f"📁 File: {os.path.basename(save_path)}"
                
                return True, message
                
            except PermissionError:
                return False, f"Permission denied: Cannot write to {save_path}"
            except Exception as e:
                print(f"DEBUG: Error writing file: {e}")
                return False, f"Error saving file: {str(e)}"
                    
        except Exception as e:
            print(f"DEBUG: Error in delete_key_from_file: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error deleting key: {str(e)}"
    
    def get_save_path(self, original_file_path=""):
        """
        الحصول على مسار الحفظ بناءً على الإعدادات
        
        Args:
            original_file_path: مسار الملف الأصلي (اختياري)
        """
        try:
            use_custom_path = get_use_custom_path()
            custom_path = get_custom_path()
            
            if use_custom_path and custom_path:
                # استخدام المسار المخصص من FileBrowserScreen
                # إذا كان المسار مجلداً، نضيف اسم الملف
                if os.path.isdir(custom_path):
                    save_path = os.path.join(custom_path, "SoftCam.Key")
                elif not custom_path.endswith("SoftCam.Key"):
                    # إذا كان مسار ملف مختلف، نستخدمه كما هو
                    save_path = custom_path
                else:
                    save_path = custom_path
                
                print(f"DEBUG: Using custom save path: {save_path}")
                return save_path
            else:
                # استخدام المسار الافتراضي أو مسار الملف الأصلي
                if original_file_path and os.path.exists(original_file_path):
                    print(f"DEBUG: Using original file path: {original_file_path}")
                    return original_file_path
                else:
                    default_path = "/etc/tuxbox/config/SoftCam.Key"
                    print(f"DEBUG: Using default save path: {default_path}")
                    return default_path
                
        except Exception as e:
            print(f"DEBUG: Error getting save path: {e}")
            # استرجاع المسار الافتراضي في حالة الخطأ
            return "/etc/tuxbox/config/SoftCam.Key"

    def show_all_details(self):
        """عرض جميع التفاصيل في شاشة واحدة (زر Menu)"""
        try:
            if not self.biss_keys:
                self.session.open(
                    MessageBox,
                    "No BISS keys available",
                    MessageBox.TYPE_INFO,
                    timeout=2
                )
                return
            
            # حساب عدد الصفحات
            total_pages = max(1, (len(self.biss_keys) + self.items_per_page - 1) // self.items_per_page)
            
            # إنشاء نص يحتوي على جميع الشفرات مع معلومات الصفحة
            details = f"📋 All BISS Keys ({len(self.biss_keys)})\n"
            details += f"📄 {total_pages} pages | {self.items_per_page} items per page\n"
            details += "="*50 + "\n\n"
            
            for page in range(total_pages):
                start_idx = page * self.items_per_page
                end_idx = min(start_idx + self.items_per_page, len(self.biss_keys))
                
                details += f"--- Page {page + 1}/{total_pages} (Items {start_idx + 1}-{end_idx}) ---\n"
                
                for i in range(start_idx, end_idx):
                    key = self.biss_keys[i]
                    formatted_key = " ".join([key['key'][j:j+2] for j in range(0, 16, 2)])
                    comment = key['comment'] if key['comment'] else "(No comment)"
                    
                    details += f"{i + 1}. {key['hash']}\n"
                    details += f"   Key: {formatted_key}\n"
                    details += f"   Comment: {comment[:40]}{'...' if len(comment) > 40 else ''}\n"
                    details += f"   File: {key['file']}:{key['line']}\n"
                    details += "\n"
                
                details += "-"*40 + "\n\n"
            
            # عرض في شاشة ScrollLabel
            from Screens.ScrollLabel import ScrollLabel
            
            self.session.openWithCallback(
                None,
                ScrollLabel,
                details,
                title="All BISS Keys (Paged View)"
            )
            
        except Exception as e:
            print(f"Error showing all details: {e}")

# =============================================
# شاشة معلومات عن الإضافة والمطور
# =============================================
class AboutScreen(Screen):
    """شاشة معلومات عن الإضافة والمطور"""
    skin = """
    <screen position="center,center" flags="wfNoBorder" cornerRadius="25" size="850,570" backgroundColor="#0D000000" title="About E2 BISS Key Editor">
        <widget name="title" position="center,5" size="500,60" font="Regular;35" halign="center" valign="center" foregroundColor="#FFD700" backgroundColor="#3C110011" cornerRadius="15" transparent="1" />
        
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 50" zPosition="5" noWrap="1" valign="center" halign="right" position="580,0" render="Label" size="250,70" source="global.CurrentTime" transparent="1"  >
            <convert type="ClockToText">Format: %-H:%M:%S</convert>
        </widget>
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 40" zPosition="5" noWrap="1" valign="center" halign="left" position="10,0" render="Label" size="510,70" source="global.CurrentTime" transparent="1"  >
            <convert type="ClockToText">Format:%d %b %Y</convert>
        </widget>
        
       
        <!-- معلومات المطور -->
        <widget name="developer_label" cornerRadius="10" position="50,100" size="260,40" font="Regular;25" halign="center" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        <widget name="developer_value" cornerRadius="10" position="290,100" size="490,40" font="Regular;25" halign="center" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        
        <!-- معلومات الإصدار -->
        <widget name="version_label" cornerRadius="10" position="50,150" size="260,40" font="Regular;25" halign="center" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        <widget name="version_value" cornerRadius="10" position="290,150" size="490,40" font="Regular;25" halign="center" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        
        <!-- تاريخ التطوير -->
        <widget name="date_label" cornerRadius="10" position="50,200" size="260,40" font="Regular;25" halign="center" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        <widget name="date_value" cornerRadius="10" position="290,200" size="490,40" font="Regular;25" halign="center" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        
        <!-- ميزات الإضافة -->
        <widget name="features_title" transparent="1" position="center,260" size="300,40" font="Regular;28" halign="center" valign="center" foregroundColor="#FF6347" backgroundColor="#0DCCEEFF" />
        
        <!-- قائمة الميزات -->
        <widget name="feature1" cornerRadius="10" position="50,310" size="730,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        <widget name="feature2" cornerRadius="10" position="50,350" size="730,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        <widget name="feature3" cornerRadius="10" position="50,390" size="730,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        <widget name="feature4" cornerRadius="10" position="50,430" size="730,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        <widget name="feature5" cornerRadius="10" position="50,470" size="730,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0DCCEEFF" />
        
        <!-- زر العودة -->
        <widget name="key_red" position="350,520" size="150,45" zPosition="1" font="Regular;25" halign="center" valign="center" backgroundColor="#3C110011" cornerRadius="20" foregroundColor="red" transparent="1" />
        <eLabel name="red_button" position="320,530" size="30,30" zPosition="2" cornerRadius="15" backgroundColor="red" />
        <eLabel name="red_button_effect" position="330,540" zPosition="3" size="10,10" cornerRadius="5" backgroundColor="#3C110011" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        # الحصول على مسار المكون الإضافي
        plugin_path = os.path.dirname(os.path.realpath(__file__))
        version_file_path = os.path.join(plugin_path, "version")
        
        # قراءة رقم الإصدار من الملف
        version = self.read_version_from_file(version_file_path)
        
        # تعريف العناصر
        self["title"] = Label("About Plugin")
        
        # معلومات المطور
        self["developer_label"] = Label("Developer")
        self["developer_value"] = Label("Ismail9875 + AI Tools")
        
        # معلومات الإصدار
        self["version_label"] = Label("Version")
        self["version_value"] = Label(version)
        
        # تاريخ التطوير
        self["date_label"] = Label("Development Date")
        self["date_value"] = Label("3 Dec 2025")
        
        # عنوان الميزات
        self["features_title"] = Label("••• Main Features •••")
        
        # قائمة الميزات
        self["feature1"] = Label("✓ Add & Validate BISS keys (8-cell & 16-digit)")
        self["feature2"] = Label("✓ Automatic emulator restart after saving")
        self["feature3"] = Label("✓ Multiple hash calculation methods")
        self["feature4"] = Label("✓ Auto-fix for BISS-CA keys")
        self["feature5"] = Label("✓ Channel information display")
        
        # زر العودة
        self["key_red"] = Label("Back")
        
        # خريطة الإجراءات
        self["actions"] = ActionMap(["ColorActions", "OkCancelActions"],
            {
                "red": self.close,
                "cancel": self.close,
                "ok": self.close,
            }, -1)
    
    def read_version_from_file(self, file_path):
        """
        قراءة رقم الإصدار من ملف النص
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    version = file.read().strip()
                    return version if version else "1.0"
            else:
                # إذا لم يوجد الملف، إنشاؤه بقيمة افتراضية
                with open(file_path, 'w') as file:
                    file.write("2.0")
                return "2.0"
        except Exception as e:
            print(f"[AboutScreen] Error reading version file: {e}")
            return "2.0"

# =============================================
# شاشة إدخال الشيفرة الأفقية (HorizontalHexInput) مع التعديلات
# =============================================

class HorizontalHexInput(Screen):
    skin = """
    <screen position="center,center" flags="wfNoBorder" size="1000,490" title="E2 BISS Key Editor" backgroundColor="#0D000000" cornerRadius="25" >
        <widget name="title" borderWidth="1" borderColor="#FFFF17" position="center,0" size="450,60" font="Regular;40" halign="center" valign="center" cornerRadius="15" foregroundColor="red" backgroundColor="#0D000000" />
        <widget name="help" position="center,70" size="880,40" font="Regular;25" halign="center" valign="center" cornerRadius="15" foregroundColor="yellow" backgroundColor="#0D000000" />
        
        <!-- عرض الخلايا بشكل أفقي >
        <widget name="cells" position="1040,110" size="600,60" font="Regular;35" halign="center" valign="center" backgroundColor="#3C110011" foregroundColor="#0D000000" transparent="1" /-->
        
        <!-- خلايا منفصلة لعرض القيم -->
        <widget name="cell_0" position="120,130" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_1" position="220,130" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_2" position="320,130" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_3" position="420,130" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_4" position="520,130" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_5" position="620,130" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_6" position="720,130" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        <widget name="cell_7" position="820,130" size="80,60" font="Regular;35" halign="center" valign="center" backgroundColor="#2A2A2A" foregroundColor="white" cornerRadius="15" />
        
        <!-- أزرار الأحرف بشكل عمودي على اليسار -->
        <widget name="key_a" position="10,120" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_b" position="10,180" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_c" position="10,240" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_d" position="10,300" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_e" position="10,360" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        <widget name="key_f" position="10,420" size="80,50" cornerRadius="15" zPosition="1" font="Regular;24" halign="center" valign="center" backgroundColor="#4169E1" foregroundColor="white" />
        
        <!-- معلومات القناة المفصلة على اليمين -->
        <widget name="channel_name" position="120,240" size="480,35" font="Regular;25" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#0D000000" transparent="1" />
        <widget name="sid_info" position="120,270" size="180,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" transparent="1" />
        <widget name="vpid_info" position="240,270" size="180,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" transparent="1" />
        <widget name="apid_info" position="420,270" size="180,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" transparent="1" />
        <widget name="pmtpid_info" position="600,270" size="180,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" transparent="1" />
        <widget name="tsid_info" position="120,300" size="180,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" transparent="1" />
        <widget name="onid_info" position="240,300" size="320,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" transparent="1" />
        <widget name="namespace_info" position="420,300" size="320,35" font="Regular;22" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" transparent="1" />
        <widget name="service_ref" position="120,330" size="480,35" font="Regular;25" halign="left" valign="center" foregroundColor="#4169E1" backgroundColor="#0D000000" transparent="1" />
        
        <widget source="session.CurrentService" render="Label" font="Regular_bold; 25" position="120,365" size="700,40" halign="left" valign="center" zPosition="25" backgroundColor="#0D000000" foregroundColor="#926F34" transparent="1" >
            <convert type="TransponderInfo"/>
        </widget>

        <!-- معلومات الهاش المختار -->
        <widget name="hash_logic_name" position="120,200" size="380,40" font="Regular;24" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#0D000000" transparent="1" />
        <widget name="hash_value" position="520,200" size="200,40" font="Regular;24" halign="left" zPosition="1" valign="center" foregroundColor="yellow" backgroundColor="#0D000000" cornerRadius="10" transparent="1" />
        
        <!-- حالة التشفير -->
        <widget name="encryption_status" position="520,240" cornerRadius="20" size="200,30" font="Regular;22" halign="left" valign="center" foregroundColor="yellow" backgroundColor="#0D000000" transparent="1" />
        
        <widget source="session.CurrentService" foregroundColor="yellow" render="Label" font="Regular; 20" transparent="1" size="300,80" cornerRadius="30" position="670,410" valign="center" halign="center" backgroundColor="red" zPosition="15" >
            <convert type="E2BissKeyEditorCryptInfo">CAIDs</convert>
        </widget>
        
        <!-- Clock and Date -->
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 50" zPosition="5" noWrap="1" valign="center" halign="center" position="750,0" render="Label" size="250,70" source="global.CurrentTime" transparent="1"  >
            <convert type="ClockToText">Format: %-H:%M:%S</convert>
        </widget>
        <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular; 40" zPosition="5" noWrap="1" valign="center" halign="center" position="0,0" render="Label" size="250,70" source="global.CurrentTime" transparent="1"  >
            <convert type="ClockToText">Format:%d %b %Y</convert>
        </widget>
        
        <!-- Signal Info from Skin Only -->
        <widget source="session.FrontendStatus" render="Progress" position="180,410" size="300,20" backgroundColor="#3C110011" foregroundColor="#926F34" transparent="0" zPosition="5" cornerRadius="15">
            <convert type="FrontendInfo">SNR</convert>
        </widget>
        <widget source="session.FrontendStatus" render="Progress" position="180,450" size="300,20" backgroundColor="#3C110011" transparent="0" foregroundColor="#926F34" zPosition="5" cornerRadius="15">
            <convert type="FrontendInfo">AGC</convert>
        </widget>
        
        <widget source="session.CurrentService" render="Label" position="600,300" size="120,28" font="Regular; 22" halign="left" foregroundColor="#ff00" backgroundColor="#0D000000" zPosition="2" transparent="1" text="25888" valign="center">
            <convert type="furyBitrate">VideoBitrateUnits</convert>
        </widget>         
        <widget source="session.FrontendStatus" render="Label" position="600,330" foregroundColor="yellow" size="200,40" font="Regular; 25" backgroundColor="yellow" halign="center" valign="center" transparent="1">
            <convert type="FrontendInfo">SNRdB</convert>
        </widget>
        
        <widget source="session.FrontendStatus" render="Label" position="500,400" foregroundColor="white" size="98,40" font="Regular; 30" backgroundColor="yellow" halign="center" valign="center" transparent="1">
            <convert type="FrontendInfo">SNR</convert>
        </widget>
        <widget source="session.FrontendStatus" render="Label" foregroundColor="white" position="500,440" size="98,40" font="Regular; 30" backgroundColor="yellow" halign="center" valign="center" transparent="1"  >
            <convert type="FrontendInfo">AGC</convert>
        </widget>

        <!-- AGC, SNR text -->
        <eLabel name="snr_label" position="120,405" size="60,30" foregroundColor="white" text="SNR" font="Regular_bold; 24" backgroundColor="#0D000000" halign="left" transparent="1" />
        <eLabel name="agc_label" position="120,445" size="60,30" foregroundColor="white" text="AGC" font="Regular_bold; 24" backgroundColor="#0D000000" halign="left" transparent="1" />
        
        <!-- أزرار التحكم في الأسفل -->
        <widget name="key_red" position="860,200" size="180,50" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="red" transparent="1" />
        <eLabel name="red_Button" position="810,210" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="red" />
        <eLabel name="redButtonEffect" position="820,220" zPosition="3" size="10,10" cornerRadius="10" backgroundColor="#0D000000" />
        
        <widget name="key_green" position="860,250" size="180,50" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="green" transparent="1" />
        <eLabel name="green_Button" position="810,260" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="green" />
        <eLabel name="greenButtonEffect" position="820,270" zPosition="3" size="10,10" cornerRadius="10" backgroundColor="#0D000000" />

        <widget name="key_yellow" position="860,300" size="180,50" zPosition="1" font="Regular;27" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="yellow" transparent="1" />
        <eLabel name="yellow_Button" position="810,310" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="yellow" />
        <eLabel name="yellowButtonEffect" position="820,320" zPosition="3" size="10,10" cornerRadius="10" backgroundColor="#0D000000" />
        
        <widget name="key_blue" position="860,350" size="180,50" zPosition="1" font="Regular;30" halign="left" valign="center" backgroundColor="#0D000000" cornerRadius="25" foregroundColor="blue" transparent="1" />
        <eLabel name="blue_Button" position="810,360" size="30,30" zPosition="2" cornerRadius="25" backgroundColor="blue" />
        <eLabel name="blueButtonEffect" position="820,370" zPosition="3" size="10,10" cornerRadius="10" backgroundColor="#0D000000" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.cells = ["00", "00", "00", "00", "00", "00", "00", "00"]
        self.current_cell = 0
        self.current_char = 0
        self.selected_letter_index = 0
        self.selected_hash = None
        self.hash_logic_name = ""
        self.tuner_data = {}
        self.close_directly = True
        
        # قائمة الأحرف
        self.letters = ["A", "B", "C", "D", "E", "F"]
        
        # تعريف جميع العناصر
        self["title"] = Label("E2 BISS Key Editor")
        self["help"] = Label("Use 0-9 keys for numbers, UP/DOWN for letters, LEFT/RIGHT for cells")
        self["cells"] = Label("")  # العرض القديم
        
        # تعريف الخلايا المنفصلة
        for i in range(8):
            self["cell_%d" % i] = Label("00")
        
        # معلومات القناة المفصلة
        self["channel_name"] = Label("")
        self["sid_info"] = Label("")
        self["vpid_info"] = Label("")
        self["apid_info"] = Label("")
        self["pmtpid_info"] = Label("")
        self["tsid_info"] = Label("")
        self["onid_info"] = Label("")
        self["namespace_info"] = Label("")
        self["service_ref"] = Label("")
        
        # معلومات الهاش
        self["hash_logic_name"] = Label("")
        self["hash_value"] = Label("")
        self["encryption_status"] = Label("")
        
        # معلومات الإعدادات
        self["settings_info"] = Label("")
        
        # أزرار الأحرف بشكل عمودي
        self["key_a"] = Label("A")
        self["key_b"] = Label("B")
        self["key_c"] = Label("C")
        self["key_d"] = Label("D")
        self["key_e"] = Label("E")
        self["key_f"] = Label("F")
        
        # أزرار التحكم
        self["key_green"] = Label("Save")
        self["key_red"] = Label("Exit")
        self["key_blue"] = Label("Set Path")
        self["key_yellow"] = Label("Show Keys")
        
        self["actions"] = ActionMap(["ColorActions", "OkCancelActions", "DirectionActions", "NumberActions", "MenuActions", "InfoActions"],
            {
                "up": self.up,
                "down": self.down,
                "left": self.left,
                "right": self.right,
                "ok": self.input_selected_letter,
                "cancel": self.close,
                "green": self.validate_and_save,
                "red": self.close,
                "blue": self.open_settings,
                "yellow": self.viewBissKeys,
                "menu": self.open_option_menu,                       
                "info": self.open_about_screen,
                "0": lambda: self.input_char("0"),
                "1": lambda: self.input_char("1"),
                "2": lambda: self.input_char("2"),
                "3": lambda: self.input_char("3"),
                "4": lambda: self.input_char("4"),
                "5": lambda: self.input_char("5"),
                "6": lambda: self.input_char("6"),
                "7": lambda: self.input_char("7"),
                "8": lambda: self.input_char("8"),
                "9": lambda: self.input_char("9"),
            }, -1)
        
        # إضافة أزرار الأحرف إلى ActionMap للإدخال المباشر
        self.letter_actions = {
            "a": lambda: self.input_char("A"),
            "b": lambda: self.input_char("B"),
            "c": lambda: self.input_char("C"),
            "d": lambda: self.input_char("D"),
            "e": lambda: self.input_char("E"),
            "f": lambda: self.input_char("F"),
        }
        
        for key, action in self.letter_actions.items():
            self["actions"].actions[key] = action
        
        self.onLayoutFinish.append(self.update_display)
        self.onLayoutFinish.append(self.update_channel_info)
        self.onLayoutFinish.append(self.update_hash_display)
        self.onLayoutFinish.append(self.update_letter_buttons)
        self.onLayoutFinish.append(self.update_settings_info)  # تحديث معلومات الإعدادات
        
        # حساب الهاش وتحميل الشفرة تلقائياً عند بدء التشغيل
        self.onShown.append(self.auto_calculate_hash)

    def update_settings_info(self):
        """تحديث معلومات الإعدادات الحالية"""
        try:
            # الحصول على الإعدادات الحالية من ملف البلوجين
            hash_logic = get_hash_logic()
            auto_restart = "Enabled" if get_restart_emu() else "Disabled"
            use_custom_path = "Yes" if get_use_custom_path() else "No"
            
            # تحديث النص
            settings_text = f"Settings: Hash={hash_logic}, AutoRestart={auto_restart}, CustomPath={use_custom_path}"
            self["settings_info"].setText(settings_text)
            
        except Exception as e:
            print(f"Error updating settings info: {e}")
            self["settings_info"].setText("Settings: Error")
    
    def auto_calculate_hash(self):
        """حساب الهاش تلقائياً عند بدء التشغيل باستخدام إعدادات المستخدم"""
        try:
            # أولاً، تأكد من وجود ملف الإعدادات
            ensure_settings_file()
            
            print(f"DEBUG: Current hash logic from plugin settings: {get_hash_logic()}")
            print(f"DEBUG: Auto restart setting: {get_restart_emu()}")
            print(f"DEBUG: Use custom path: {get_use_custom_path()}")
            print(f"DEBUG: Custom path: {get_custom_path()}")
            
            # حساب الهاش باستخدام إعدادات المستخدم الحالية
            hash_value, logic_info = get_selected_hash(self.session)
            
            if hash_value:
                self.selected_hash = hash_value.upper()  # Capital letters
                self.hash_logic_name = logic_info
                
                # الآن البحث عن شفرة القناة الحالية
                key_found = self.load_current_channel_key()
                
                # فقط إذا لم يتم العثور على شفرة، نقوم بتفريغ الخلايا
                if not key_found:
                    print("No key found, resetting cells to default")
                    self.auto_reset_on_startup()
                else:
                    print("Key loaded successfully, skipping reset")
                
                print(f"Auto-calculated hash using {logic_info}: {hash_value}")
            else:
                print("Auto-hash calculation failed, resetting cells")
                self.auto_reset_on_startup()
                
        except Exception as e:
            print(f"Error in auto hash calculation: {e}")
            # في حالة الخطأ، نفترض عدم وجود شفرة ونقوم بالتفريغ
            self.auto_reset_on_startup()

    def load_current_channel_key(self):
        """تحميل شفرة القناة الحالية تلقائياً عند البدء وإرجاع حالة النجاح"""
        try:
            if not self.selected_hash:
                print("No hash available, skipping key load")
                return False
            
            print(f"Searching for key with hash: {self.selected_hash}")
            
            # تحديد مسارات البحث بناءً على إعدادات المستخدم
            search_paths = []
            
            use_custom_path = get_use_custom_path()
            custom_path = get_custom_path()
            
            if use_custom_path and custom_path:
                # أولوية للمسار المخصص من قبل المستخدم
                search_paths.append(custom_path)
            else:
                # استخدام المسار الافتراضي
                search_paths.append("/etc/tuxbox/config/SoftCam.Key")
            
            # إضافة مسارات أخرى موجودة للنسخ الاحتياطي
            found_paths = detect_softcam_key_paths()
            for path in found_paths:
                if path not in search_paths:
                    search_paths.append(path)
            
            print(f"Searching in {len(search_paths)} paths: {search_paths}")
            
            found_key = None
            source_file = None
            
            # البحث في جميع الملفات
            for file_path in search_paths:
                try:
                    if os.path.exists(file_path):
                        print(f"Checking file: {file_path}")
                        
                        if PY3:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                        else:
                            with open(file_path, 'r') as f:
                                content = f.read()
                        
                        # البحث عن السطر الذي يحتوي على الهاش الحالي
                        lines = content.split('\n')
                        for line_num, line in enumerate(lines, 1):
                            line = line.strip()
                            if line.startswith('F '):
                                parts = line.split()
                                if len(parts) >= 4:
                                    line_hash = parts[1].upper()
                                    if line_hash == self.selected_hash.upper():
                                        key_part = parts[3]
                                        # التحقق من أن الشفرة صالحة (16 رمز سداسي عشر)
                                        if len(key_part) == 16 and all(c in '0123456789ABCDEFabcdef' for c in key_part):
                                            found_key = key_part.upper()
                                            source_file = file_path
                                            print(f"✓ Found key at line {line_num} in {file_path}: {found_key}")
                                            break
                        if found_key:
                            break
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
            
            if found_key:
                # تقسيم الشفرة إلى أزواج من الأحرف (خلايا)
                key_cells = [found_key[i:i+2] for i in range(0, 16, 2)]
                
                # التحقق من صحة الشفرة وتصحيحها
                fixed_cells, valid, msg = validate_and_fix_biss_8cells(key_cells)
                
                if fixed_cells:
                    # تعيين الخلايا بالشفرة المصححة
                    self.cells = fixed_cells
                    
                    # تحديث العرض
                    self.update_display()
                    
                    # تسجيل النجاح في السجل
                    key_display = " ".join(fixed_cells)
                    print(f"✓ Auto-loaded key: {key_display}")
                    
                    return True
                else:
                    print(f"✗ Found key but validation failed: {msg}")
                    return False
            else:
                print("✗ No key found for current channel hash")
                return False
                
        except Exception as e:
            print(f"Error in load_current_channel_key: {e}")
            import traceback
            traceback.print_exc()
            return False

    def auto_reset_on_startup(self):
        """تفريغ جميع الخانات إلى الحالة الافتراضية فقط"""
        try:
            # إعادة تعيين الخلايا إلى القيم الافتراضية
            self.cells = ["00", "00", "00", "00", "00", "00", "00", "00"]
            self.current_cell = 0
            self.current_char = 0
            self.selected_letter_index = 0
            
            # تحديث العرض
            self.update_display()
            
            print("✓ All BISS cells reset to default (no key found)")
        except Exception as e:
            print("Error in auto reset on startup: %s" % str(e))

    def update_display(self):
        """تحديث جميع عناصر العرض"""
        try:
            # تحديث الخلايا المنفصلة
            for i in range(8):
                cell_widget = self["cell_%d" % i]
                cell_value = self.cells[i]
                cell_widget.setText(cell_value)
                
                # تحديث الألوان بناءً على الخلية النشطة
                if i == self.current_cell:
                    # الخلية النشطة - خلفية زرقاء فاتحة ونص أسود
                    cell_widget.instance.setBackgroundColor(gRGB(0x926F34))  # ذهبي
                    cell_widget.instance.setForegroundColor(gRGB(0xFFFFFF))  # أبيض
                else:
                    # الخلايا غير النشطة - خلفية داكنة ونص أبيض
                    cell_widget.instance.setBackgroundColor(gRGB(0xE8FFF1))  # بني داكن
                    cell_widget.instance.setForegroundColor(gRGB(0x000000))  # أصفر فاقع
            
            # تحديث ألوان أزرار الأحرف
            self.update_letter_buttons()
            
            # تحديث العرض النصي القديم (للتوافق)
            self["cells"].setText(self.get_cells_display())
            
        except Exception as e:
            print("Error in update_display: %s" % str(e))

    def update_letter_buttons(self):
        """تحديث ألوان أزرار الأحرف بناءً على الحرف المختار"""
        try:
            for i, letter in enumerate(self.letters):
                widget = self["key_%s" % letter.lower()]
                if i == self.selected_letter_index:
                    # الحرف المختار - خلفية برتقالية ونص أسود
                    widget.instance.setBackgroundColor(gRGB(0xFFA500))  # برتقالي
                    widget.instance.setForegroundColor(gRGB(0x000000))  # أسود
                else:
                    # الأحرف غير المختارة - خلفية زرقاء ونص أبيض
                    widget.instance.setBackgroundColor(gRGB(0x4169E1))  # أزرق ملكي
                    widget.instance.setForegroundColor(gRGB(0xFFFFFF))  # أبيض
        except Exception as e:
            print("Error updating letter buttons: %s" % str(e))

    def get_cells_display(self):
        """الحصول على نص عرض الخلايا (للتوافق مع الكود القديم)"""
        display = ""
        for i, cell in enumerate(self.cells):
            if i == self.current_cell:
                display += "[%s] " % cell
            else:
                display += " %s  " % cell
        return display.strip()

    def close_direct(self):
        """إغلاق مباشر دون تحديث أي displays"""
        self.close_directly = True
        self.close()

    def close(self):
        """إغلاق الشاشة مع التحكم في السلوك"""
        try:
            if hasattr(self, 'signal_timer'):
                self.signal_timer.stop()
        except:
            pass
        
        if self.close_directly:
            # إغلاق مباشر دون أي عمليات إضافية
            Screen.close(self)
        else:
            # إغلاق عادي مع تحديثات (لحالات أخرى)
            Screen.close(self)
        
        self.close_directly = True  # إعادة تعيين المتغير

    def update_channel_info(self):
        """تحديث معلومات القناة المفصلة"""
        try:
            service_info = self.get_detailed_service_info()
            
            if not service_info or not service_info.get('channel_name'):
                self.set_default_channel_info()
                return
            
            # معلومات القناة الأساسية
            self["channel_name"].setText(service_info['channel_name'])
            self["sid_info"].setText("SID %04X" % service_info['sid'])
            self["vpid_info"].setText("VPID %04X" % service_info['vpid'])
            self["apid_info"].setText("APID %04X" % service_info['apid'])
            self["pmtpid_info"].setText("PMTPID %04X" % service_info['pmtpid'])
            self["tsid_info"].setText("TSID %04X" % service_info['tsid'])
            self["onid_info"].setText("ONID %04X" % service_info['onid'])
            self["namespace_info"].setText("NS %08X" % service_info['namespace'])
            self["service_ref"].setText("Ref %s" % service_info['service_ref'])
            
            # حالة التشفير
            encryption_text = "Encrypted" if service_info['is_encrypted'] else "FTA"
            self["encryption_status"].setText(encryption_text)
            
        except Exception as e:
            print("Error updating channel info: %s" % str(e))
            self.set_default_channel_info()

    def get_detailed_service_info(self):
        """الحصول على معلومات تفصيلية عن الخدمة الحالية"""
        try:
            service = self.session.nav.getCurrentService()
            if not service:
                return None

            service_ref = self.session.nav.getCurrentlyPlayingServiceReference()
            if not service_ref:
                return None

            # الحصول على المعلومات الأساسية
            service_handler = eServiceCenter.getInstance()
            service_info_obj = service_handler.info(service_ref)
            channel_name = service_info_obj.getName(service_ref) if service_info_obj else "Unknown"

            # الحصول على جميع المعرفات
            sid = service_ref.getUnsignedData(1)  # SID
            tsid = service_ref.getUnsignedData(2)  # TSID
            onid = service_ref.getUnsignedData(3)  # ONID
            namespace = service_ref.getUnsignedData(4)  # Namespace
            
            # الحصول على PIDs من معلومات الخدمة
            info = service.info()
            if info:
                vpid = info.getInfo(iServiceInformation.sVideoPID)
                apid = info.getInfo(iServiceInformation.sAudioPID)
                pmtpid = info.getInfo(iServiceInformation.sPMTPID)
                is_encrypted = info.getInfo(iServiceInformation.sIsCrypted) == 1
            else:
                vpid = apid = pmtpid = 0
                is_encrypted = False

            return {
                'channel_name': channel_name,
                'sid': sid,
                'vpid': vpid,
                'apid': apid,
                'pmtpid': pmtpid,
                'tsid': tsid,
                'onid': onid,
                'namespace': namespace,
                'service_ref': str(service_ref.toString()),
                'is_encrypted': is_encrypted
            }
            
        except Exception as e:
            print("Error getting detailed service info: %s" % str(e))
            return None

    def set_default_channel_info(self):
        """تعيين معلومات القناة الافتراضية"""
        self["channel_name"].setText("No channel info")
        self["sid_info"].setText("SID: N/A")
        self["vpid_info"].setText("VPID: N/A")
        self["apid_info"].setText("APID: N/A")
        self["pmtpid_info"].setText("PMTPID: N/A")
        self["tsid_info"].setText("TSID: N/A")
        self["onid_info"].setText("ONID: N/A")
        self["namespace_info"].setText("Namespace: N/A")
        self["service_ref"].setText("Ref: N/A")
        self["encryption_status"].setText("No signal")

    def update_hash_display(self):
        """تحديث عرض معلومات الهاش باستخدام الإعدادات الحالية"""
        try:
            # تحديث اسم منطق الهاش من الإعدادات
            current_logic = get_hash_logic()
                
            logic_map = {
                "SID+VPID": "SID+VPID",
                "CRC32 Original": "CRC32 ORIGINAL"
            }
            
            logic_name = logic_map.get(current_logic, "Unknown")
            self["hash_logic_name"].setText("Hash Logic: %s" % logic_name)
            
            # حساب الهاش باستخدام الإعدادات الحالية
            hash_value, logic_info = get_selected_hash(self.session)
            
            if hash_value:
                self.selected_hash = hash_value.upper()
                self["hash_value"].setText(self.selected_hash)
            else:
                self.selected_hash = None
                self["hash_value"].setText("")
                
        except Exception as e:
            print(f"Error updating hash display: {e}")
    
    def open_option_menu(self):
        """فتح شاشة الخيارات عند الضغط على زر Menu"""
        try:
            print("DEBUG: Opening OptionMenuScreen...")
            # افتح شاشة الإعدادات
            self.session.open(OptionMenuScreen)
        except Exception as e:
            print(f"ERROR opening option menu: {e}")
            import traceback
            traceback.print_exc()
            self.session.open(
                MessageBox,
                f"Error opening option menu:\n{str(e)[:100]}",
                MessageBox.TYPE_ERROR,
                timeout=3
            )
        
    def on_option_menu_closed(self, result=None):
        """Callback عند إغلاق شاشة الخيارات - تحديث الإعدادات"""
        try:
            print("Option menu closed, updating settings...")
            
            # تحديث معلومات الإعدادات
            self.update_settings_info()
            
            # إعادة حساب الهاش مع الإعدادات الجديدة
            self.update_hash_display()
            
            # محاولة تحميل الشفرة الجديدة للهاش الجديد
            self.load_current_channel_key()
            
            print(f"Settings updated")
            
        except Exception as e:
            print(f"Error in option menu callback: {e}")

    def is_valid_hex_char(self, char):
        """التحقق إذا كان الحرف مسموحاً به (0-9, A-F, a-f)"""
        return char in '0123456789ABCDEFabcdef'

    def input_char(self, char):
        """إدخال حرف في الموضع الحالي مع التحقق من الصحة"""
        # التحقق من أن الحرف مسموح به
        if not self.is_valid_hex_char(char):
            return
        
        # تحويل الحرف إلى uppercase للتأكد من التنسيق
        char = char.upper()
        
        current_value = self.cells[self.current_cell]
        
        if self.current_char == 0:
            # استبدال الحرف الأول
            new_value = char + current_value[1]
        else:
            # استبدال الحرف الثاني
            new_value = current_value[0] + char
        
        self.cells[self.current_cell] = new_value
        
        # الانتقال التلقائي للحرف التالي
        self.auto_move_next()
        
        self.update_display()

    def input_selected_letter(self):
        """إدخال الحرف المحدد بالأزرار العلوية والسفلية"""
        selected_letter = self.letters[self.selected_letter_index]
        self.input_char(selected_letter)

    def auto_move_next(self):
        """الانتقال التلقائي للحرف أو الخلية التالية"""
        if self.current_char == 0:
            # الانتقال إلى الحرف الثاني في نفس الخلية
            self.current_char = 1
        else:
            # الانتقال إلى الخلية التالية (الحرف الأول)
            self.current_char = 0
            if self.current_cell < 7:
                self.current_cell += 1

    def up(self):
        """التنقل بين الأحرف (UP) - للأعلى في العمود"""
        if self.selected_letter_index > 0:
            self.selected_letter_index -= 1
        else:
            self.selected_letter_index = len(self.letters) - 1  # الانتقال للأسفل
        self.update_display()

    def down(self):
        """التنقل بين الأحرف (DOWN) - للأسفل في العمود"""
        if self.selected_letter_index < len(self.letters) - 1:
            self.selected_letter_index += 1
        else:
            self.selected_letter_index = 0  # الانتقال للأعلى
        self.update_display()

    def left(self):
        """الانتقال إلى الخلية السابقة (LEFT) - في الصف الأفقي"""
        if self.current_cell > 0:
            self.current_cell -= 1
            self.current_char = 0
            self.update_display()

    def right(self):
        """الانتقال إلى الخلية التالية (RIGHT) - في الصف الأفقي"""
        if self.current_cell < 7:
            self.current_cell += 1
            self.current_char = 0
            self.update_display()

    def open_settings(self):
        """فتح شاشة الإعدادات لاختيار مسار حفظ الشفرات (الزر الأزرق الآن)"""
        try:
            # فتح FileBrowserScreen في وضع الإعدادات
            self.session.openWithCallback(
                self.on_settings_closed,
                FileBrowserScreen,
                mode="settings"
            )
        except Exception as e:
            print("Error opening settings: %s" % str(e))
            self.session.open(MessageBox, "Error opening settings", MessageBox.TYPE_ERROR, timeout=2)

    def on_settings_closed(self, result=None):
        """Callback عند إغلاق شاشة الإعدادات"""
        try:
            # تحديث أي معلومات قد تتأثر بالإعدادات
            print("Settings screen closed")
        except Exception as e:
            print("Error in settings callback: %s" % str(e))
        self.update_display()
        
    def viewBissKeys(self):
        """فتح شاشة عرض شفرات البيس"""
        try:
            self.session.open(BissKeysBrowserScreen)
        except Exception as e:
            print(f"Error opening BISS keys browser: {e}")
            self.session.open(
                MessageBox,
                "Error opening BISS keys browser",
                MessageBox.TYPE_ERROR,
                timeout=2
            )

    def confirm_reset(self, result):
        """تأكيد عملية إعادة التعيين"""
        if result:
            try:
                # إعادة تعيين الخلايا إلى القيم الافتراضية
                self.cells = ["00", "00", "00", "00", "00", "00", "00", "00"]
                self.current_cell = 0
                self.current_char = 0
                self.selected_letter_index = 0
                self.selected_hash = None
                self.hash_logic_name = ""
                
                # تحديث العرض
                self.update_display()
                self.update_hash_display()
                
                # عرض رسالة نجاح مع timeout 3 ثواني
                self.session.open(
                    MessageBox,
                    "All fields have been reset to default values.",
                    MessageBox.TYPE_INFO,
                    timeout=3  # ✓ Timeout محدد 3 ثواني
                )
            except Exception as e:
                print("Error resetting fields: %s" % str(e))
                self.session.open(
                    MessageBox,
                    "Error resetting fields. Please try again.",
                    MessageBox.TYPE_ERROR,
                    timeout=2  # ✅ Timeout محدد 2 ثانية للأخطاء
                )

    def open_about_screen(self):
        #"""فتح شاشة معلومات الإضافة عند الضغط على زر Info"""
        try:
            self.session.open(AboutScreen)
        except Exception as e:
            print("Error opening about screen: %s" % str(e))
            self.session.open(MessageBox, "Error opening about screen", MessageBox.TYPE_ERROR)

    def validate_and_save(self):
        #"""التحقق من صحة الشيفرة قبل الحفظ"""
        try:
            # أولاً، تحديث الهاش باستخدام الإعدادات الحالية
            self.update_hash_display()
            
            # التحقق من وجود هاش محدد
            if not self.selected_hash:
                self.session.open(MessageBox, "No hash available! Please check channel information.", MessageBox.TYPE_ERROR, timeout=3)
                return
            
            # التحقق من صحة الشيفرة وتصحيحها تلقائياً
            fixed_cells, valid, msg = validate_and_fix_biss_8cells(self.cells)
            
            if fixed_cells is None:
                self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR, timeout=3)
                return
            
            if valid:
                # إذا كانت الشيفرة صالحة، حفظ مباشرة
                self.doSave(fixed_cells)
            else:
                # إذا كانت تحتاج تصحيح، حفظ مع التصحيح
                self.doSave(fixed_cells)
                
        except Exception as e:
            print("Error in validate_and_save: %s" % str(e))
            self.session.open(MessageBox, "Validation error: %s" % str(e), MessageBox.TYPE_ERROR, timeout=3)

    def doSave(self, fixed_cells):
        """حفظ الشيفرة إلى ملف/ملفات SoftCam.Key مع مراعاة إعدادات Auto Restart"""
        try:
            # تحديث الخلايا المحلية بالقيم المصححة
            self.cells = fixed_cells
            
            # إنشاء الشيفرة الكاملة
            key16 = "".join(fixed_cells)
            channel_info = self.get_channel_info_for_backup()
    
            # إنشاء سطر المفتاح
            key_line = "F %s 00 %s ;  %s %s" % (self.selected_hash, key16, channel_info, datetime.now().strftime('%Y-%m-%d %H:%M'))
            
            # حفظ المفتاح في جميع المسارات
            save_success, save_message = save_key_to_all_paths(key_line)
            
            # ✅ التحقق من CAID الفعلي للقناة
            dvbapi_success = False
            dvbapi_message = ""
            
            if save_success and self.selected_hash:
                try:
                    # الحصول على معلومات القناة الحالية
                    service_info = self.get_detailed_service_info()
                    
                    if service_info:
                        sid = service_info.get('sid', 0)
                        pmtpid = service_info.get('pmtpid', 0)
                        
                        print(f"DEBUG - SID: {sid:04X}, PMTPID: {pmtpid:04X}")
                        
                        if sid > 0 and pmtpid > 0:
                            # ✅ الحصول على CAIDs الحقيقية للقناة
                            caids_list = []
                            caid_2600_found = False
                            
                            print("DEBUG - Checking actual CAID of current channel...")
                            
                            # الطريقة الأساسية: الحصول مباشرة من خدمة enigma
                            try:
                                from enigma import iServiceInformation
                                service = self.session.nav.getCurrentService()
                                
                                if service:
                                    info = service.info()
                                    if info:
                                        print(f"DEBUG - Service info object obtained")
                                        
                                        # محاولة 1: getInfoObject للحصول على قائمة CAIDs
                                        try:
                                            caids_obj = info.getInfoObject(iServiceInformation.sCAIDs)
                                            if caids_obj:
                                                print(f"DEBUG - Raw CAIDs object: {caids_obj}")
                                                if isinstance(caids_obj, list):
                                                    for caid_item in caids_obj:
                                                        try:
                                                            caid_int = int(caid_item)
                                                            caids_list.append(caid_int)
                                                            print(f"DEBUG - Found CAID: {caid_int} (0x{caid_int:04X})")
                                                        except ValueError:
                                                            print(f"DEBUG - Invalid CAID value: {caid_item}")
                                                else:
                                                    # قد يكون قيمة واحدة
                                                    try:
                                                        caid_int = int(caids_obj)
                                                        caids_list.append(caid_int)
                                                        print(f"DEBUG - Single CAID: {caid_int} (0x{caid_int:04X})")
                                                    except ValueError:
                                                        print(f"DEBUG - Invalid single CAID: {caids_obj}")
                                        except Exception as e:
                                            print(f"DEBUG - Error with getInfoObject: {e}")
                                        
                                        # محاولة 2: getInfo للحصول على CAID الأساسي
                                        if not caids_list:
                                            try:
                                                caid_val = info.getInfo(iServiceInformation.sCAID)
                                                if caid_val and caid_val > 0:
                                                    caids_list.append(caid_val)
                                                    print(f"DEBUG - CAID from sCAID: {caid_val} (0x{caid_val:04X})")
                                            except Exception as e:
                                                print(f"DEBUG - Error with sCAID: {e}")
                                        
                                        # محاولة 3: getInfo للحصول على CAIDs
                                        if not caids_list:
                                            try:
                                                caids_val = info.getInfo(iServiceInformation.sCAIDs)
                                                if caids_val:
                                                    print(f"DEBUG - sCAIDs value: {caids_val}")
                                                    if isinstance(caids_val, list):
                                                        for item in caids_val:
                                                            try:
                                                                caid_int = int(item)
                                                                caids_list.append(caid_int)
                                                            except:
                                                                pass
                                                    elif caids_val > 0:
                                                        caids_list.append(caids_val)
                                            except Exception as e:
                                                print(f"DEBUG - Error with sCAIDs: {e}")
                            except ImportError as e:
                                print(f"DEBUG - Cannot import enigma modules: {e}")
                            except Exception as e:
                                print(f"DEBUG - General error with enigma service: {e}")
                            
                            # ✅ طريقة احتياطية: استخدام ECM info
                            if not caids_list:
                                try:
                                    from Tools.GetEcmInfo import GetEcmInfo
                                    ecm_info = GetEcmInfo()
                                    if ecm_info:
                                        # محاولة الحصول على CAID من ECM
                                        caid_hex = ecm_info.getInfo("caid")
                                        if caid_hex:
                                            try:
                                                caid_int = int(caid_hex, 16) if caid_hex.startswith('0x') else int(caid_hex)
                                                caids_list.append(caid_int)
                                                print(f"DEBUG - CAID from ECM: {caid_int} (0x{caid_int:04X})")
                                            except ValueError:
                                                print(f"DEBUG - Invalid ECM CAID: {caid_hex}")
                                except Exception as e:
                                    print(f"DEBUG - Error with ECM info: {e}")
                            
                            # ✅ طريقة أخرى: قراءة من ملفات التردد الحالي
                            if not caids_list:
                                try:
                                    # محاولة قراءة من bouquet الحالي
                                    from Components.config import config
                                    import os
                                    
                                    current_ref = self.session.nav.getCurrentlyPlayingServiceReference()
                                    if current_ref:
                                        ref_str = current_ref.toString()
                                        print(f"DEBUG - Current service ref: {ref_str}")
                                        
                                        # استخراج CAID من مرجع الخدمة (الجزء السادس)
                                        parts = ref_str.split(':')
                                        if len(parts) > 5:
                                            caid_str = parts[5]
                                            if caid_str:
                                                try:
                                                    caid_int = int(caid_str, 16)
                                                    caids_list.append(caid_int)
                                                    print(f"DEBUG - CAID from service ref: {caid_int} (0x{caid_int:04X})")
                                                except ValueError:
                                                    print(f"DEBUG - Invalid CAID in service ref: {caid_str}")
                                except Exception as e:
                                    print(f"DEBUG - Error reading service ref: {e}")
                            
                            # ✅ معالجة نتائج CAID
                            print(f"DEBUG - Final CAIDs list: {caids_list}")
                            
                            # التحقق من وجود CAID 2600 (0xA28)
                            for caid in caids_list:
                                try:
                                    caid_int = int(caid)
                                    print(f"DEBUG - Checking CAID: {caid_int} (0x{caid_int:04X})")
                                    if caid_int == 0xA28:  # 2600 بالست عشري
                                        caid_2600_found = True
                                        print("✓ DEBUG - Found CAID 2600 (0xA28)")
                                        break
                                except (ValueError, TypeError) as e:
                                    print(f"DEBUG - Error processing CAID {caid}: {e}")
                                    continue
                            
                            # ✅ اتخاذ القرار بناءً على CAID الفعلي
                            if caid_2600_found:
                                print("DEBUG - Channel uses BISS (CAID 2600), skipping DVBAPI")
                                dvbapi_message = "\nℹ️ Channel uses BISS encryption (CAID 2600), no DVBAPI rule needed"
                            
                            elif caids_list:
                                # القناة تستخدم تشفيراً غير BISS، نضيف DVBAPI
                                try:
                                    # استخدام أول CAID (عادةً الأكثر أهمية)
                                    caid_to_use = int(caids_list[0])
                                    print(f"DEBUG - Non-BISS CAID found: {caid_to_use} (0x{caid_to_use:04X})")
                                    
                                    # إنشاء سطر DVBAPI باستخدام CAID الفعلي
                                    dvbapi_line = f"A: ::{sid:04X}:{pmtpid:04X} 2600:000000:1FFF ; %s %s" % (channel_info, datetime.now().strftime('%Y-%m-%d %H:%M'))
                                    
                                    print(f"DEBUG - DVBAPI Line: {dvbapi_line}")
                                    
                                    # مسارات ملفات DVBAPI
                                    dvbapi_paths = [
                                        "/etc/tuxbox/config/oscam.dvbapi",
                                        "/etc/tuxbox/config/ncam.dvbapi",
    
                                    ]
                                    
                                    # إضافة السطر إلى ملفات DVBAPI
                                    added_paths = []
                                    for path in dvbapi_paths:
                                        try:
                                            # التأكد من وجود المجلد
                                            dir_path = os.path.dirname(path)
                                            if dir_path and not os.path.exists(dir_path):
                                                os.makedirs(dir_path, exist_ok=True)
                                            
                                            # التحقق إذا كان الملف موجودًا
                                            file_exists = os.path.exists(path)
                                            
                                            # التحقق من التكرار
                                            duplicate_found = False
                                            if file_exists:
                                                with open(path, 'r', encoding='utf-8') as f:
                                                    content = f.read()
                                                    if dvbapi_line in content:
                                                        duplicate_found = True
                                                        print(f"DEBUG - Line already exists in {path}")
                                            
                                            if not duplicate_found:
                                                with open(path, 'a', encoding='utf-8') as f:
                                                    f.write(dvbapi_line + '\n')
                                                added_paths.append(path)
                                                print(f"✓ Added DVBAPI line to: {path}")
                                        except Exception as e:
                                            print(f"✗ Failed to add to {path}: {e}")
                                    
                                    if added_paths:
                                        dvbapi_success = True
                                        dvbapi_message = f"\n📝 DVBAPI rule added to {len(added_paths)} file(s):\n" + "\n".join([os.path.basename(p) for p in added_paths])
                                    else:
                                        dvbapi_message = "\n⚠️ DVBAPI rule not added (already exists or no writable files)"
                                except Exception as e:
                                    print(f"DEBUG - Error creating DVBAPI: {e}")
                                    dvbapi_message = f"\n⚠️ Error creating DVBAPI rule: {str(e)}"
                            
                            else:
                                # لم نتمكن من الحصول على CAID
                                print("DEBUG - Could not determine CAID")
                                dvbapi_message = "\n⚠️ Could not determine channel encryption type"
                                
                        else:
                            print(f"DEBUG - Missing SID or PMTPID")
                            dvbapi_message = "\n⚠️ Could not get channel parameters for DVBAPI rule"
                    else:
                        print("DEBUG - No service info available")
                        dvbapi_message = "\n⚠️ No channel information available"
                        
                except Exception as e:
                    print(f"Error in CAID detection: {e}")
                    import traceback
                    traceback.print_exc()
                    dvbapi_message = f"\n⚠️ Error detecting channel encryption: {str(e)[:50]}"
            
            # ✅ إعادة تشغيل المحاكي تلقائياً بعد الحفظ - بناءً على إعدادات المستخدم
            restart_success = False
            restart_message = ""
            
            if save_success:
                # التحقق من إعداد Auto Restart
                auto_restart_enabled = get_restart_emu()
                
                if auto_restart_enabled:
                    print("DEBUG: Auto Restart is ENABLED - calling restart_emu()")
                    restart_success = restart_emu()
                    
                    if restart_success:
                        restart_message = "\n🔄 Emulator restarted automatically (Auto Restart: Enabled)"
                    else:
                        restart_message = "\n⚠️ Emulator restart failed - please restart manually"
                else:
                    print("DEBUG: Auto Restart is DISABLED - skipping restart_emu()")
                    restart_message = "\n⏸️ Emulator restart skipped (Auto Restart: Disabled)"
            
            # ✅ بناء رسالة النتيجة
            if save_success:
                # الحصول على معلومات الإعدادات من ملف البلوجين
                hash_logic_text = get_hash_logic()
                auto_restart_status = "Enabled" if get_restart_emu() else "Disabled"
                use_custom_path_status = "Yes" if get_use_custom_path() else "No"
                
                message_parts = [
                    "✅ Key saved successfully!\n\n",
                    f"🔑 Hash: {self.selected_hash}\n",
                    f"🔐 Key: {key16}\n",
                    f"🎯 Hash Logic: {hash_logic_text}\n",
                    f"⚙️ Auto Restart: {auto_restart_status}\n",
                    f"📁 Custom Path: {use_custom_path_status}\n",
                    f"📁 {save_message}"
                ]
                
                if dvbapi_message:
                    message_parts.append(dvbapi_message)
                
                if restart_message:
                    message_parts.append(restart_message)
                
                message = "".join(message_parts)
            else:
                message = "❌ Save failed!\n\n%s" % save_message
            
            # عرض الرسالة
            self.session.open(
                MessageBox, 
                message, 
                MessageBox.TYPE_INFO if save_success else MessageBox.TYPE_ERROR, 
                timeout=5
            )
            
            # تفريغ الخانات بعد الحفظ الناجح
            if save_success:
                self.auto_reset_on_startup()
            
        except Exception as e:
            print("Error in doSave: %s" % str(e))
            import traceback
            traceback.print_exc()
            self.session.open(MessageBox, "Save failed:\n%s" % str(e), MessageBox.TYPE_ERROR, timeout=3)    
    
    def get_channel_info_for_backup(self):
        """الحصول على معلومات القناة للحفظ في النسخة الاحتياطية"""
        try:
            service_info = self.get_detailed_service_info()
            if service_info and service_info.get('channel_name'):
                return "%s, SID: %04X" % (service_info['channel_name'], service_info['sid'])
            return "Unknown Channel"
        except:
            return "Unknown Channel"
            
    def get_channel_info_for_backup(self):
        """الحصول على معلومات القناة للحفظ في النسخة الاحتياطية"""
        try:
            service_info = self.get_detailed_service_info()
            if service_info and service_info.get('channel_name'):
                return "%s, SID: %04X" % (service_info['channel_name'], service_info['sid'])
            return "Unknown Channel"
        except:
            return "Unknown Channel"


def main(session, **kwargs):
    # التأكد من وجود ملف الإعدادات في مجلد البلوجين
    print("DEBUG: Starting E2 BISS Key Editor...")
    ensure_settings_file()
    
    # عرض الإعدادات الحالية للتصحيح
    print("\n=== Plugin Settings ===")
    print(f"restart_emu: {get_restart_emu()}")
    print(f"UseCustomPath: {get_use_custom_path()}")
    print(f"HashLogic: {get_hash_logic()}")
    print(f"custom_save_path: {get_custom_path()}")
    print(f"Plugin settings file: {PLUGIN_SETTINGS_FILE}")
    print("=====================\n")
    
    # فتح شاشة إدخال الشيفرة مباشرة
    try:
        session.open(HorizontalHexInput)
    except Exception as e:
        handle_exception(e)
        # عرض رسالة خطأ للمستخدم
        session.open(
            MessageBox,
            f"Error opening BISS Key Editor:\n{str(e)[:100]}",
            MessageBox.TYPE_ERROR,
            timeout=5
        )

def Plugins(**kwargs): 
    return PluginDescriptor(
        name="E2 BISS Key Editor",
        description="Add & Validate Biss keys with Auto Restart & Backup",
        icon="plugin.png",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        fnc=main)
