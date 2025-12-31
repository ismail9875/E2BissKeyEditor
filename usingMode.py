# -*- coding: utf-8 -*-
# UsinMode.py - Plugin Usage Mode Screen

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
# Usage Mode Screen
# ========================================================================
class UsinMode(Screen):
    skin = """
        <screen name="UsinMode" position="center,center" flags="wfNoBorder" cornerRadius="25" size="1000,700" backgroundColor="#0D000000" title="How to Use E2 BISS Key Editor">
            <!-- Title -->
            <widget name="title" position="center,15" size="600,60" font="Regular;35" halign="center" valign="center" foregroundColor="#FFD700" backgroundColor="#3C110011" cornerRadius="15" transparent="1" />
            
            <!-- Time -->
            <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular;25" zPosition="5" noWrap="1" valign="center" halign="right" position="730,5" render="Label" size="260,70" source="global.CurrentTime" transparent="1">
                <convert type="ClockToText">Format: %-H:%M:%S</convert>
            </widget>
            
            <!-- Date -->
            <widget backgroundColor="#0D000000" foregroundColor="white" font="Regular;25" zPosition="5" noWrap="1" valign="center" halign="left" position="10,5" render="Label" size="510,70" source="global.CurrentTime" transparent="1">
                <convert type="ClockToText">Format:%d %b %Y</convert>
            </widget>
            
            <!-- Top status bar -->
            <eLabel position="30,80" size="940,3" zPosition="1" backgroundColor="#4169E1" />
            
            <!-- Scrollable instructions area -->
            <widget name="instruction_scroll" position="40,90" size="920,480" font="Regular;24" halign="left" valign="top" foregroundColor="#FFFFFF" backgroundColor="#0D000000" transparent="1" scrollbarMode="showOnDemand" />
            
            <!-- Bottom info bar -->
            <eLabel position="30,585" size="940,2" zPosition="1" backgroundColor="#4169E1" />
            
            <!-- Control buttons -->
            <!-- Red button -->
            <eLabel name="red_button" position="40,600" size="30,30" zPosition="2" cornerRadius="15" backgroundColor="red" />
            <widget name="key_red" position="75,600" size="130,35" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="#1A000000" cornerRadius="10" foregroundColor="red" transparent="1" />
           
            <!-- Green button -->
            <eLabel name="green_button" position="210,600" size="30,30" zPosition="2" cornerRadius="15" backgroundColor="green" />
            <widget name="key_green" position="245,600" size="130,35" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="#1A000000" cornerRadius="10" foregroundColor="green" transparent="1" />

            
            <!-- Yellow button -->
            <eLabel name="yellow_button" position="425,600" size="30,30" zPosition="2" cornerRadius="15" backgroundColor="yellow" />
            <widget name="key_yellow" position="460,600" size="180,35" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="#1A000000" cornerRadius="10" foregroundColor="yellow" transparent="1" />
            
            <!-- Blue button -->
            <eLabel name="blue_button" position="740,600" size="30,30" zPosition="2" cornerRadius="15" backgroundColor="blue" />
            <widget name="key_blue" position="775,600" size="130,35" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="#1A000000" cornerRadius="10" foregroundColor="blue" transparent="1" />
            
            
            <!-- Page indicator -->
            <widget name="page_indicator" position="center,655" size="200,25" font="Regular;20" halign="center" valign="center" foregroundColor="#AAAAAA" backgroundColor="#0D000000" transparent="1" />
        </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        # Initialize variables
        self.current_page = 0
        self.total_pages = 0
        self.instructions = []
        
        # Define elements
        self["title"] = Label("📖 How to Use the Plugin")
        self["instruction_scroll"] = ScrollLabel("")
        self["page_indicator"] = Label("")
        
        # Define buttons
        self["key_blue"] = Label("About")
        self["key_green"] = Label("▲ Scroll Up")
        self["key_yellow"] = Label("▼ Scroll Down")
        self["key_red"] = Label("Back")
        
        # Action map
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
        
        # Initialize instructions
        self.onLayoutFinish.append(self.initialize_instructions)
    
    def initialize_instructions(self):
        """Initialize and display instructions"""
        self.instructions = self.generate_instructions()
        self["instruction_scroll"].setText("\n\n".join(self.instructions))
        self.calculate_pages()
        self.update_page_indicator()
        
        # Setup scroll properties (LTR - Left to Right)
        if hasattr(self["instruction_scroll"], 'instance'):
            try:
                self["instruction_scroll"].instance.setScrollbarMode(2)  # showOnDemand
                self["instruction_scroll"].instance.setWrap(True)
                # Set LTR alignment
                self["instruction_scroll"].instance.setHAlign(RT_HALIGN_LEFT)
                # Set text flags for proper LTR display
                if hasattr(self["instruction_scroll"].instance, 'setTextFlags'):
                    self["instruction_scroll"].instance.setTextFlags(RT_WRAP | RT_HALIGN_LEFT)
            except:
                pass
    
    def generate_instructions(self):
        """Generate usage instructions divided into sections"""
        sections = []
        
        sections.append("""**MAIN FUNCTIONS**
======================================================
=================== E2 BISS Key Editor ===================
======================================================
        ★★★ MAIN INTERFACE ★★★
            • Stand on the encrypted channel then open the plugin
            • Enter the channel key and press green button to save
            • Browse stored keys by pressing yellow button from main interface
            • Blue button: Browse keys recorded by the plugin
            After selecting a key, press OK to print the key in input cells
            • Red button: Exit the plugin
            • Green button: Validate cells and save key after validation
            • Menu button: Access plugin settings menu
            • Info button: Plugin information

""")

        sections.append("""**MAIN FUNCTIONS**
======================================================
=================== E2 BISS Key Editor ===================
======================================================
        ★★★ KEY BROWSING INTERFACE ★★★
    ♦ From main interface press yellow button
        1 - Browse keys with up/down buttons
        2 - Navigate between pages with left/right or green/yellow buttons
        3 - Blue button to edit key
        4 - Yellow button to delete key
        5 - Green button to show complete key information
        6 - Red button to return to main screen

""")
        
        sections.append("""**MAIN FUNCTIONS**
======================================================
=================== E2 BISS Key Editor ===================
======================================================
        ★★★ KEY EDITING ★★★
    ♦ From key browsing interface press blue button
        1 - Enter new key using 0-9 buttons on remote
        Navigate between letters in plugin screen to type characters
            ××× BUTTON FUNCTIONS ×××
                - Red: Return to previous screen
                - Green: Save changes and validate field outputs
                - Yellow: Modify key comment/description
                - Blue: Validate field outputs

""")
        
        sections.append("""**MAIN FUNCTIONS**
======================================================
=================== E2 BISS Key Editor ===================
======================================================
        ★★★ PLUGIN SETTINGS ★★★
            1 - Hash Logic:
                SID+VIP = Recommended for fixed encryption channels like Algerian terrestrial
                    and feeds on satellites: EutelSat 21.5/21.6E & EutelSat 3.1E
                CRC32 ORIGINAL = Recommended for most satellites except those mentioned above
                    Unique channel identifier that doesn't conflict with other channels
                ****    This is the plugin default option ****
            2 - AutoRestart Emulator:
                Automatic emulator restart after saving key
            3 - Enable Custom Path:
                Enable/disable using custom path specified by user
                Default plugin path is:
                /etc/tuxbox/config/SoftCam.Key
            
        ================================================
                #### BUTTON FUNCTIONS ####
                 
            1 - Red button: Go back
            2 - Green button: Save changes
            3 - Yellow button: Update plugin
            4 - Blue button: Select custom path for key storage

""")
        
        sections.append("""**MAIN FUNCTIONS**
======================================================
=================== E2 BISS Key Editor ===================
======================================================
                #### CUSTOM PATH SELECTION SCREEN ###
        Main function: Select custom path for key storage
        SoftCam.Key file will be created if it doesn't exist
        
        ======================================================
                #### BUTTON FUNCTIONS ####
                
                1 - Red button: Go back
                2 - Green button: Set current path as key storage path
                3 - Yellow button: Go to parent folder
                4 - Blue button: Return to default storage path
                Default path is (/etc/tuxbox/config/)

""")
        
        sections.append("""**ADDITIONAL INFORMATION**
======================================================
=================== E2 BISS Key Editor ===================
======================================================
        ★★★ IMPORTANT NOTES ★★★
            1 - Plugin Version: 2.0
            2 - Compatible with: Enigma2 based receivers
            3 - Supported key formats: BISS



""")

        return sections
    
    def calculate_pages(self):
        """Calculate number of pages"""
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
        """Update page indicator"""
        if self.total_pages > 0:
            current_position = self.get_current_position()
            self["page_indicator"].setText(f"Page: {current_position}/{self.total_pages}")
        else:
            self["page_indicator"].setText("")
    
    def get_current_position(self):
        """Get current position"""
        try:
            pos = self["instruction_scroll"].getPos()
            if self.total_pages > 0:
                return min(self.total_pages, max(1, (pos * self.total_pages) // 100))
        except:
            pass
        return self.current_page + 1
    
    def scroll_up(self):
        """Scroll up"""
        try:
            self["instruction_scroll"].pageUp()
            self.update_page_indicator()
        except:
            pass
    
    def scroll_down(self):
        """Scroll down"""
        try:
            self["instruction_scroll"].pageDown()
            self.update_page_indicator()
        except:
            pass
    
    def page_up(self):
        """Page up"""
        self.scroll_up()
    
    def page_down(self):
        """Page down"""
        self.scroll_down()
    
    def page_left(self):
        """Go to previous section"""
        if len(self.instructions) > 0:
            self.current_page = (self.current_page - 1) % len(self.instructions)
            self["instruction_scroll"].setText(self.instructions[self.current_page])
            try:
                self["instruction_scroll"].goTop()
            except:
                pass
            self.update_page_indicator()
    
    def page_right(self):
        """Go to next section"""
        if len(self.instructions) > 0:
            self.current_page = (self.current_page + 1) % len(self.instructions)
            self["instruction_scroll"].setText(self.instructions[self.current_page])
            try:
                self["instruction_scroll"].goTop()
            except:
                pass
            self.update_page_indicator()
    
    def toggle_scroll_mode(self):
        """Toggle scroll mode"""
        # In Enigma2, ScrollLabel doesn't support setSelectionEnabled
        # You can add alternative functionality here if needed
        pass
    
    def show_about_info(self):
        """Show about information"""
        about_text = """E2 BISS Key Editor v2.0

A powerful plugin for managing biss keys
on Enigma2 based satellite receivers.
"""
        
        self.session.open(MessageBox, about_text, MessageBox.TYPE_INFO, timeout=30)
    
    def close(self):
        """Close screen"""
        Screen.close(self)
