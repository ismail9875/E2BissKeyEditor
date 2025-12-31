# -*- coding: utf-8 -*-
# UsinMode.py - شاشة عرض طريقة استخدام البلوجين

from __future__ import absolute_import
import os
import sys
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from enigma import eLabel, gFont, RT_HALIGN_LEFT, RT_HALIGN_CENTER, RT_HALIGN_RIGHT, RT_VALIGN_TOP, RT_VALIGN_CENTER, RT_WRAP
from Screens.MessageBox import MessageBox
from enigma import getDesktop
from skin import parseColor

# ========================================================================
# شاشة طريقة الاستخدام
# ========================================================================
class UsinMode(Screen):
    skin = """
        <screen name="UsinMode" position="center,center" flags="wfNoBorder" cornerRadius="25" size="1000,700" backgroundColor="#0D000000" title="How to Use E2 BISS Key Editor">
            <!-- العنوان -->
            <widget name="title" position="center,15" size="600,60" font="Regular;35" halign="center" valign="center" foregroundColor="#FFD700" backgroundColor="#3C110011" cornerRadius="15" transparent="1" />
            
            <!-- الوقت -->
            <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular;25" zPosition="5" noWrap="1" valign="center" halign="right" position="730,5" render="Label" size="260,70" source="global.CurrentTime" transparent="1">
                <convert type="ClockToText">Format: %-H:%M:%S</convert>
            </widget>
            
            <!-- التاريخ -->
            <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular;25" zPosition="5" noWrap="1" valign="center" halign="left" position="10,5" render="Label" size="510,70" source="global.CurrentTime" transparent="1">
                <convert type="ClockToText">Format:%d %b %Y</convert>
            </widget>
            
            <!-- شريط الحالة العلوي -->
            <eLabel position="30,80" size="940,3" zPosition="1" backgroundColor="#4169E1" />
            
            <!-- منطقة التعليمات القابلة للتمرير -->
            <widget name="instruction_scroll" position="40,90" size="920,480" font="Regular;24" halign="left" valign="top" foregroundColor="#FFFFFF" backgroundColor="#0D000000" transparent="1" scrollbarMode="showOnDemand" />
            
            <!-- شريط المعلومات السفلي -->
            <eLabel position="30,585" size="940,2" zPosition="1" backgroundColor="#4169E1" />
            
            <!-- أزرار التحكم -->
            <!-- الزر الأزرق -->
            <eLabel name="blue_button" position="40,600" size="30,30" zPosition="2" cornerRadius="15" backgroundColor="blue" />
            <widget name="key_blue" position="75,600" size="130,35" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="#1A000000" cornerRadius="10" foregroundColor="blue" transparent="1" />
            
            <!-- الزر الأخضر -->
            <eLabel name="green_button" position="210,600" size="30,30" zPosition="2" cornerRadius="15" backgroundColor="green" />
            <widget name="key_green" position="245,600" size="130,35" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="#1A000000" cornerRadius="10" foregroundColor="green" transparent="1" />
            
            <!-- الزر الأصفر -->
            <eLabel name="yellow_button" position="400,600" size="30,30" zPosition="2" cornerRadius="15" backgroundColor="yellow" />
            <widget name="key_yellow" position="445,600" size="130,35" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="#1A000000" cornerRadius="10" foregroundColor="yellow" transparent="1" />
            
            <!-- الزر الأحمر -->
            <eLabel name="red_button" position="600,600" size="30,30" zPosition="2" cornerRadius="15" backgroundColor="red" />
            <widget name="key_red" position="630,600" size="130,35" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="#1A000000" cornerRadius="10" foregroundColor="red" transparent="1" />
            
            <!-- مؤشر الصفحة -->
            <widget name="page_indicator" position="center,655" size="200,25" font="Regular;20" halign="center" valign="center" foregroundColor="#AAAAAA" backgroundColor="#0D000000" transparent="1" />
        </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        # تهيئة المتغيرات
        self.current_page = 0
        self.total_pages = 0
        self.instructions = []
        
        # تعريف العناصر
        self["title"] = Label("📖 How to Use the Plugin")
        self["instruction_scroll"] = ScrollLabel("")
        self["page_indicator"] = Label("")
        
        # تعريف الأزرار
        self["key_blue"] = Label("About")
        self["key_green"] = Label("▲ Scroll Up")
        self["key_yellow"] = Label("▼ Scroll Down")
        self["key_red"] = Label("Back")
        
        # خريطة الإجراءات
        self["actions"] = ActionMap(["ColorActions", "OkCancelActions", "NavigationActions"],
            {
                "red": self.close,
                "cancel": self.close,
                "ok": self.toggle_scroll_mode,
                "blue": self.show_about_info,
                "green": self.scroll_up,
                "yellow": self.scroll_down,
                "up": self.scroll_up,
                "down": self.scroll_down,
                "left": self.page_left,
                "right": self.page_right,
                "pageUp": self.page_up,
                "pageDown": self.page_down,
            }, -1)
        
        # تهيئة التعليمات
        self.onLayoutFinish.append(self.initialize_instructions)
    
    def initialize_instructions(self):
        """تهيئة التعليمات وعرضها"""
        self.instructions = self.generate_instructions()
        self["instruction_scroll"].setText("\n\n".join(self.instructions))
        self.calculate_pages()
        self.update_page_indicator()
        
        # إعداد خصائص التمرير
        if hasattr(self["instruction_scroll"], 'instance'):
            try:
                self["instruction_scroll"].instance.setScrollbarMode(2)  # showOnDemand
                self["instruction_scroll"].instance.setWrap(True)
            except:
                pass
    
    def generate_instructions(self):
        """إنشاء تعليمات الاستخدام مقسمة إلى أقسام"""
        sections = []
        

        sections.append("""**MAIN FUNCTIONS**
======================================================
=================== E2 Biss Key Editor ===================
======================================================
1. **Add New Keys**: Add BISS keys for new channels
2. **Edit Existing**: Modify existing BISS keys
3. **Validate Keys**: Check key format and validity
4. **Delete Keys**: Remove unwanted or incorrect keys
5. **Backup/Restore**: Create backups of your key database
6. **Auto-restart**: Automatically restart emulator after changes""")
        
        # القسم 3: إضافة المفاتيح
        sections.append(""" **ADDING NEW KEYS - STEP BY STEP**
======================================================
=================== E2 Biss Key Editor ===================
====================================================== 
*** Hash Logic ***
    • SID+VPID :
        - a method based on the channel data ServiceID & VideoPid.
        - direct method to build a biss key for emulators.
        - Recommended to use for channels of : 21.5/21.6 sat & EutelSat 3.1
    • CRC32 ORIGINAL :
        - More advanced methode & more effecience  for major satellites
        - 

""")
        
        # القسم 4: صيغ المفاتيح
        sections.append("""**KEY FORMATS SUPPORTED**
======================================================
=================== E2 Biss Key Editor ===================
======================================================
**Standard BISS Key:**
   • 16 hexadecimal characters
   • Example: 1122334455667788

**BISS-CA Auto-fix:**
   • Automatic correction of BISS-CA format
   • Converts to standard format
   • Preserves compatibility

**Validation Rules:**
   • Exactly 16 characters
   • Only 0-9, A-F allowed
   • No spaces or special characters
   • Auto-uppercase conversion
   """)
        # القسم 6: الميزات التلقائية
        sections.append("""**AUTOMATIC FEATURES**
======================================================
=================== E2 Biss Key Editor ===================
======================================================
    • Auto-save: Automatic saving after validation
    • Auto-restart: Restarts emulator after changes
    • Auto-backup: Creates backup before modifications
    • Auto-error-correction: Fixes common key format errors
    • Auto-SID-detection: Detects SID from current channel
    • Auto-logging: Detailed logs for troubleshooting""")
        

        
        # القسم 8: أفضل الممارسات
        sections.append(""" **BEST PRACTICES & TIPS**
======================================================
=================== E2 Biss Key Editor ===================
======================================================
    1. **Always Backup:** Create backup before making changes
    2. **Verify SID:** Double-check Service Reference before adding
    3. **Test Immediately:** Test each key after adding
    4. **Keep Updated:** Regularly update plugin version
    5. **Check Logs:** Review logs for error information
    6. **Use Color Buttons:** Quick navigation with color keys
    7. **Keyboard Shortcuts:**
       • OK: Toggle scroll mode
       • ▲/▼: Scroll up/down
       • ◀/▶: Navigate sections
       • Red: Back/Exit
       • Blue: About info""")
        

        
        # القسم 10: الخيارات المتقدمة
        sections.append(""" **ADVANCED OPTIONS**
======================================================
=================== E2 Biss Key Editor ===================
======================================================
    **System Integration:**
        • Custom SoftCam.Key paths
        • External script execution
        • Enable/Disable Emulator AutoRestart
""")
        
        return sections
    
    def calculate_pages(self):
        """حساب عدد الصفحات"""
        try:
            content_height = self["instruction_scroll"].instance.contentHeight()
            viewport_height = self["instruction_scroll"].instance.size().height()
            if viewport_height > 0:
                self.total_pages = max(1, (content_height + viewport_height - 1) // viewport_height)
            else:
                self.total_pages = len(self.instructions)
        except:
            self.total_pages = len(self.instructions)
    
    def update_page_indicator(self):
        """تحديث مؤشر الصفحة"""
        if self.total_pages > 0:
            current_position = self.get_current_position()
            self["page_indicator"].setText(f"Page: {current_position}/{self.total_pages}")
        else:
            self["page_indicator"].setText("")
    
    def get_current_position(self):
        """الحصول على الموضع الحالي"""
        try:
            pos = self["instruction_scroll"].getPos()
            if self.total_pages > 0:
                return min(self.total_pages, max(1, (pos * self.total_pages) // 100))
        except:
            pass
        return self.current_page + 1
    
    def scroll_up(self):
        """التمرير لأعلى"""
        try:
            self["instruction_scroll"].pageUp()
            self.update_page_indicator()
        except:
            pass
    
    def scroll_down(self):
        """التمرير لأسفل"""
        try:
            self["instruction_scroll"].pageDown()
            self.update_page_indicator()
        except:
            pass
    
    def page_up(self):
        """صفحة لأعلى"""
        self.scroll_up()
    
    def page_down(self):
        """صفحة لأسفل"""
        self.scroll_down()
    
    def page_left(self):
        """الانتقال للقسم السابق"""
        if len(self.instructions) > 0:
            self.current_page = (self.current_page - 1) % len(self.instructions)
            self["instruction_scroll"].setText(self.instructions[self.current_page])
            try:
                self["instruction_scroll"].goTop()
            except:
                pass
            self.update_page_indicator()
    
    def page_right(self):
        """الانتقال للقسم التالي"""
        if len(self.instructions) > 0:
            self.current_page = (self.current_page + 1) % len(self.instructions)
            self["instruction_scroll"].setText(self.instructions[self.current_page])
            try:
                self["instruction_scroll"].goTop()
            except:
                pass
            self.update_page_indicator()
    
    def toggle_scroll_mode(self):
        """تبديل وضع التمرير"""
        # في Enigma2، ScrollLabel لا يدعم setSelectionEnabled
        # يمكنك إضافة وظيفة بديلة هنا إذا لزم الأمر
        pass
    
    def show_about_info(self):
        """عرض معلومات عن البلوجين"""
        about_text =""
  
    def close(self):
        """إغلاق الشاشة"""
        Screen.close(self)
