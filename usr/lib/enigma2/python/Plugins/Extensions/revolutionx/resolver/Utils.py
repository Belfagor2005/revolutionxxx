#!/usr/bin/python
# -*- coding: utf-8 -*-
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.ActionMap import NumberActionMap
from Components.Button import Button
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.FileList import FileList
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.Pixmap import MovingPixmap
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Task import Task, Job, job_manager as JobManager, Condition
from Components.config import config
from Components.config import ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBar import MoviePlayer
from Screens.InfoBar import InfoBar
from Screens.InfoBarGenerics import *
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.TaskView import JobView
from ServiceReference import ServiceReference
from Tools.Directories import resolveFilename, pathExists, fileExists, SCOPE_SKIN_IMAGE, SCOPE_MEDIA
from Tools.LoadPixmap import LoadPixmap
from enigma import eServiceCenter
from enigma import eServiceReference
from enigma import eTimer, quitMainloop, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, eListbox, gFont, ePicLoad
from enigma import getDesktop
from enigma import loadPNG
from skin import parseColor
from socket import gaierror, error
from threading import Thread
from twisted.internet import reactor
from twisted.web import client
from twisted.web.client import getPage, downloadPage
import os
import re
import socket
import sys
import six
from six.moves.urllib.request import urlopen
from six.moves.urllib.request import Request
from six.moves.urllib.error import HTTPError, URLError
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import quote
from six.moves.urllib.parse import urlencode
from six.moves.urllib.parse import unquote
from six.moves.urllib.parse import quote_plus
from six.moves.urllib.parse import unquote_plus
from six.moves.urllib.parse import parse_qs
from six.moves.urllib.request import urlretrieve  
from sys import version_info
PY3 = sys.version_info.major >= 3

try:
    from http.client import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
    import http.client
    import urllib.request, urllib.parse, urllib.error
except:
    from httplib import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
    import httplib
    import urllib
    import urlparse

HTTPConnection.debuglevel = 1
DESKHEIGHT = getDesktop(0).size().height()

THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/tvspro"
try:
       from Plugins.Extensions.SubsSupport import SubsSupport, initSubsSettings
except:
       pass

std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
}
##############################################################
#                                                            #
#   Mainly Coded by pcd, July 2013                 #
#                                                            #
##############################################################

SREF = " "

class PlayvidFHD():
    skin = """
            <screen name="playscreen" position="center,center" size="1920,1080" title="tvspro" flags="wfNoBorder" backgroundColor="transparent">
            <eLabel position="93,33" zPosition="1" size="969,939" backgroundColor="#000000" />
            <eLabel position="90,30" zPosition="-1" size="975,945" backgroundColor="#ffffff" />
            <eLabel position="1278,528" zPosition="-1" size="519,444" backgroundColor="#000000" />
            <eLabel position="1275,525" zPosition="-2" size="525,450" backgroundColor="#ffffff" />
            <widget name="list" position="150,150" zPosition="4" size="870,444" itemHeight="40" backgroundColor="#000000" foregroundColor="#b3b3b9" foregroundColorSelected="#ffffff" backgroundColorSelected="#000000" scrollbarMode="showOnDemand" />
            <widget name="info" position="120,660" zPosition="4" size="930,300" font="Regular;37" foregroundColor="#ffffff" backgroundColor="#40000000" transparent="1" halign="left" valign="center" />
            <ePixmap position="150,975" zPosition="1" size="75,75" pixmap="~/images/Exit2.png" />
            </screen>"""

class PlayvidHD():
    skin = """
        <screen name="Playvid" position="center,center" size="1280,720" title="tvspro" flags="wfNoBorder" backgroundColor="transparent">
        <eLabel position="62,22" zPosition="1" size="646,626" backgroundColor="#000000" />
        <eLabel position="60,20" zPosition="-1" size="650,630" backgroundColor="#ffffff" />
        <eLabel position="852,352" zPosition="-1" size="346,296" backgroundColor="#000000" />
        <eLabel position="850,350" zPosition="-2" size="350,300" backgroundColor="#ffffff" />
        <widget name="list" position="100,100" zPosition="4" size="580,296" itemHeight="40" backgroundColor="#000000" foregroundColor="#b3b3b9" foregroundColorSelected="#ffffff" backgroundColorSelected="#000000" scrollbarMode="showOnDemand" />
        <widget name="info" position="80,440" zPosition="4" size="620,200" font="Regular;25" foregroundColor="#ffffff" backgroundColor="#40000000" transparent="1" halign="left" valign="center" />
        </screen>"""

class Playvid(Screen):
    def __init__(self, session, name, url, desc):
        global SREF
        Screen.__init__(self, session)
        if DESKHEIGHT > 1000:
           self.skin = PlayvidFHD.skin
        else:
           self.skin = PlayvidHD.skin
        self.name = name
        self.url = url
        self["list"] = List([])
        self["list"] = RSList([])
        self['info'] = Label()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Download'))
        self['key_yellow'] = Button(_('Play'))
        self['key_blue'] = Button(_('Stop Download'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'red': self.close,
         'green': self.okClicked,
         'yellow': self.play,
         'blue': self.stopDL,
         'cancel': self.cancel,
         'ok': self.okClicked}, -2)
        self.icount = 0
        self.bLast = 0
        self.useragent = "QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)"
        self.svfile = " "
        self.list=[]
########################
        """
        i=0
        while i<7:
               self.list.append(i)
               i=i+1
        self.list[0] =(_("Play"))

        self.list[1] =(_("Play hls"))
        self.list[2] =(_("Download"))
        self.list[3] =(_("Stop download"))
        self.list[4] =(_("Add to favorites"))
        self.list[5] =(_("Add to bouquets"))
        self.list[6] =(_("Current Downloads"))
        """
########################
        self.name = name
        self.url = url
        print("Here in Playvid self.url =", self.url)
        print("<<<Endurl")
#        self.url = self.url.replace("|", "\|")
        n1 = self.url.find("|", 0)
        if n1 > -1:
                self.url = self.url[:n1]
        print("Here in Playvid self.url B=", self.url)
        #self['info'].setText(txt)

        ####################
##        self.updateTimer = eTimer()
##        self.updateTimer.callback.append(self.updateStatus)
##        self.updateTimer.start(2000)
##        self.updateStatus()
        ####################
        self.updateTimer = eTimer()
        try:
               self.updateTimer_conn = self.updateTimer.timeout.connect(self.updateStatus)
        except AttributeError:
               self.updateTimer.callback.append(self.updateStatus)
#       self.updateTimer.callback.append(self.updateStatus)
##	self.updateTimer.start(2000)
##	self.updateStatus()
        ####################
        self['info'].setText(" ")
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        SREF = self.srefOld
        self.onLayoutFinish.append(self.start)

    def start2(self):
        desc = " "
        self.session.open(Playvid2, self.name, self.url, desc)
        self.close()

    def start3(self):
        from stream import GreekStreamTVList
        self.session.open(GreekStreamTVList, streamFile = "/tmp/stream.xml")
        self.close()

    def start4(self):
        from Playlist import Playlist
        self.session.open(Playlist, self.url)
        self.close()

    def start5(self):
         self.pop = 1
         n1 = self.url.find("video_id", 0)
         n2 = self.url.find("=", n1)
         vid = self.url[(n2+1):]
         cmd = "python '/usr/lib/enigma2/python/Plugins/Extensions/KodiDirect/plugins/plugin.video.youtube/default.py' '6' '?plugin://plugin.video.youtube/play/?video_id=" + vid + "' &"
         self.p = os.popen(cmd)

    def start(self):
        infotxt=" "
        self['info'].setText(infotxt)
        showlist(self.list, self['list'])

    def openTest(self):
        pass

    def play(self):
        url = self.url
        name = self.name
        self.session.open(Playvid3, name, url, desc = " ")

    def getlocal_filename(self):
           fold = config.plugins.kodiplug.cachefold.value+"/"
           name = self.name.replace("/media/hdd/xbmc/vid/", "")
           name = name.replace(" ", "-")
           pattern = '[a-zA-Z0-9\-]'
           input = name
           output = ''.join(re.findall(pattern, input))
           self.name = output
           if self.url.endswith("mp4"):
              svfile = fold + self.name+".mp4"
           elif self.url.endswith("flv"):
              svfile = fold + self.name+".flv"
           elif self.url.endswith("avi"):
              svfile = fold + self.name+".avi"
           elif self.url.endswith("ts"):
              svfile = fold + self.name+".ts"
           else:
              svfile = fold + self.name+".mpg"
           filetitle=os.path.split(svfile)[1]
           return svfile,filetitle


    def okClicked(self):

          idx=self["list"].getSelectionIndex()
          print("idx",idx)
          if idx==0:
                self.start2()
          elif idx==1:
                self.play()

    def playfile(self, serverint):
          self.serverList[serverint].play(self.session, self.url, self.name)


    def showError(self, error):
               print("DownloadPage error = ", error)


    def updateStatus(self):
     if self.pop == 1:
            try:
               ptxt = self.p.read()
               if "data B" in ptxt:
                      n1 = ptxt.find("data B", 0)
                      n2 = ptxt.find("&url", n1)
                      n3 = ptxt.find("\n", n2)
                      url = ptxt[(n2+5):n3]
                      url = url.replace("AxNxD", "&")
                      self.url = url.replace("ExQ", "=")
                      name = "Video"
                      desc = " "
                      self.session.open(Playvid, self.name, self.url, desc)
                      self.close()
                      self.updateTimer.stop()
#               else:
#                      self.openTest()
#                      return
            except:
               self.openTest()
#               return
     else:
        if not os.path.exists(self.svfile):
            print("No self.svfile =", self.svfile)
            self.openTest()
            return

        if self.icount == 0:
            self.openTest()
            return

        b1 = os.path.getsize(self.svfile)
        b = b1 / 1000
        if b == self.bLast:
            infotxt = _('Download Complete....') + str(b)
            self['info'].setText(infotxt)
            return
        self.bLast = b
        infotxt = _('Downloading....') + str(b) + ' kb'
        self['info'].setText(infotxt)

    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job

        if currentjob is not None:
            self.session.open(JobViewNew, currentjob)

    def cancel(self):
           if os.path.exists("/tmp/hls.avi"):
                   os.remove("/tmp/hls.avi")
           Screen.close(self, False)

    def stopDL(self):
                cmd = "rm -f " + self.svfile
                os.system(cmd)
                self.session.nav.playService(self.srefOld)
                cmd1 = "killall -9 rtmpdump"
                cmd2 = "killall -9 wget"
                os.system(cmd1)
                os.system(cmd2)
                self['info'].setText("Current download task stopped")
                self.close()

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)

class Playvid2FHD():
    skin = """
       	<screen name="Playvid" position="0,825" size="1920,225" title="InfoBar" backgroundColor="transparent" flags="wfNoBorder">
		<!-- Background -->
		<ePixmap position="0,3" zPosition="-1" size="1920,225" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/infobar2L.png"/>

       		<ePixmap position="600,34" size="30,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/yellow.png" alphatest="blend" />
                <widget name="key_yellow" position="630,22" size="300,45" valign="center" halign="left" zPosition="4"  foregroundColor="#ffffff" font="Regular;24" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />

		<!-- Date -->
		<widget source="global.CurrentTime" render="Label" position="105,25" size="187,33" font="Regular;28"  backgroundColor="black" foregroundColor="white" transparent="1" >
			<convert type="ClockToText">Format:%d.%m.%Y</convert>
		</widget>
		<!-- Time -->
		<ePixmap position="1650,31" zPosition="2" size="33,33" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/clock.png" alphatest="on" />
		<widget source="global.CurrentTime" render="Label" position="1695,25" size="300,39" zPosition="2" font="Regular;28"  foregroundColor="grey" backgroundColor="black" transparent="1">
			<convert type="ClockToText">Format %H:%M:%S</convert>
		</widget>
		<!-- Servicename -->
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/icon_event.png" position="309,85" size="30,19" alphatest="on" />
		<!-- Elapsed time -->
		<widget source="session.CurrentService" render="Label" position="360,75" size="150,39" font="Regular;33"  foregroundColor="grey"  backgroundColor="black" transparent="1" >
			<convert type="ServicePosition">Position,ShowHours</convert>
		</widget>
		<widget source="session.CurrentService" render="Label" position="525,75" size="1110,37" zPosition="2" font="Regular;30" halign="center" noWrap="1" foregroundColor="white" transparent="1" backgroundColor="background">
			<convert type="ServiceName">Name</convert>
		</widget>
		<!-- movie length -->
		<!-- Remaining time -->
		<widget source="session.CurrentService" render="Label" position="1635,72" size="180,39" font="Regular;33" halign="right"  foregroundColor="red" backgroundColor="black" transparent="1" >
			<convert type="ServicePosition">Remaining,Negate,ShowHours</convert>
		</widget>
		<widget source="session.CurrentService" render="PositionGauge" position="315,114" size="1335,21" zPosition="2" pointer="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/pointerdvd.png:890,0" transparent="1" >
			<convert type="ServicePosition">Gauge</convert>
		</widget>
		<!-- Audio icon (is there multichannel audio?) -->
		<ePixmap position="309,150" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_dolby_off.png" alphatest="blend" />
		<widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_dolby_on.png" position="309,150" size="150,30" zPosition="2" alphatest="blend">
			<convert type="ServiceInfo">IsMultichannel</convert>
			<convert type="ConditionalShowHide"/>
		</widget>
		<!-- Videoformat icon (16:9?) -->
		<ePixmap position="435,150" size="150,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_format_off.png" alphatest="blend" />
		<widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_format_on.png" position="435,150" zPosition="4" size="150,27" alphatest="blend" >
			<convert type="ServiceInfo">IsWidescreen</convert>
			<convert type="ConditionalShowHide" />
		</widget>
		<!-- HDTV icon -->
		<ePixmap position="525,147" size="150,36" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_hd_off.png" alphatest="blend" />
		<widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_hd_on.png" position="525,147" size="75,36" zPosition="4" alphatest="blend">
			<convert type="ServiceInfo">VideoWidth</convert>
			<convert type="ValueRange">721,1980</convert>
			<convert type="ConditionalShowHide" />
		</widget>
		<!-- VideoFormat -->
		<eLabel text="Res" font="Regular;30" position="600,142" size="75,30"  foregroundColor="grey" backgroundColor="black" transparent="1"/>
		<widget source="session.CurrentService" render="Label" font="Regular;30" position="660,142" size="82,30" halign="right"  foregroundColor="white" backgroundColor="black" transparent="1">
			<convert type="ServiceInfo">VideoWidth</convert>
		</widget>
		<eLabel text="x" font="Regular;24" position="757,145" size="22,33" halign="center"  backgroundColor="black" transparent="1"/>
		<widget source="session.CurrentService" render="Label" font="Regular;30" position="795,142" size="82,33"   foregroundColor="white" backgroundColor="black" transparent="1">
			<convert type="ServiceInfo">VideoHeight</convert>
		</widget>
		<widget source="session.CurrentService" render="Label" position="1740,142" size="180,39" font="Regular;33"  foregroundColor="yellow" backgroundColor="black" transparent="1" >
			<convert type="ServicePosition">Length</convert>
		</widget>
	</screen>"""



class PlayvidB():
    skin = """
       	<screen name="Playvid" position="0,550" size="1280,150" title="InfoBar" backgroundColor="transparent" flags="wfNoBorder">
		<!-- Background -->
		<ePixmap position="0,2" zPosition="-1" size="1280,150" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/infobar2.png"/>

       		<ePixmap position="400,23" size="20,20" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/yellow.png" alphatest="blend" />
                <widget name="key_yellow" position="420,15" size="200,30" valign="center" halign="left" zPosition="4"  foregroundColor="#ffffff" font="Regular;16" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />

		<!-- Date -->
		<widget source="global.CurrentTime" render="Label" position="70,17" size="125,22" font="Regular;19"  backgroundColor="black" foregroundColor="white" transparent="1" >
			<convert type="ClockToText">Format:%d.%m.%Y</convert>
		</widget>
		<!-- Time -->
		<ePixmap position="1100,21" zPosition="2" size="22,22" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/clock.png" alphatest="on" />
		<widget source="global.CurrentTime" render="Label" position="1130,17" size="200,26" zPosition="2" font="Regular;19"  foregroundColor="#062748" backgroundColor="black" transparent="1">
			<convert type="ClockToText">Format %H:%M:%S</convert>
		</widget>
		<!-- Servicename -->
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/icon_event.png" position="206,57" size="20,13" alphatest="on" />
		<!-- Elapsed time -->
		<widget source="session.CurrentService" render="Label" position="240,50" size="100,26" font="Regular;22"  foregroundColor="#062748"  backgroundColor="black" transparent="1" >
			<convert type="ServicePosition">Position,ShowHours</convert>
		</widget>
		<widget source="session.CurrentService" render="Label" position="350,50" size="740,25" zPosition="2" font="Regular;20" halign="center" noWrap="1" foregroundColor="white" transparent="1" backgroundColor="background">
			<convert type="ServiceName">Name</convert>
		</widget>
		<!-- movie length -->
		<!-- Remaining time -->
		<widget source="session.CurrentService" render="Label" position="1090,48" size="120,26" font="Regular;22" halign="right"  foregroundColor="red" backgroundColor="black" transparent="1" >
			<convert type="ServicePosition">Remaining,Negate,ShowHours</convert>
		</widget>
		<widget source="session.CurrentService" render="PositionGauge" position="210,76" size="890,14" zPosition="2" pointer="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/pointerdvd.png:890,0" transparent="1" >
			<convert type="ServicePosition">Gauge</convert>
		</widget>
		<!-- Audio icon (is there multichannel audio?) -->
		<ePixmap position="206,100" size="100,20" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_dolby_off.png" alphatest="blend" />
		<widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_dolby_on.png" position="206,100" size="100,20" zPosition="2" alphatest="blend">
			<convert type="ServiceInfo">IsMultichannel</convert>
			<convert type="ConditionalShowHide"/>
		</widget>
		<!-- Videoformat icon (16:9?) -->
		<ePixmap position="290,100" size="100,20" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_format_off.png" alphatest="blend" />
		<widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_format_on.png" position="290,100" zPosition="4" size="100,18" alphatest="blend" >
			<convert type="ServiceInfo">IsWidescreen</convert>
			<convert type="ConditionalShowHide" />
		</widget>
		<!-- HDTV icon -->
		<ePixmap position="350,98" size="100,24" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_hd_off.png" alphatest="blend" />
		<widget source="session.CurrentService" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/icon/ico_hd_on.png" position="350,98" size="50,24" zPosition="4" alphatest="blend">
			<convert type="ServiceInfo">VideoWidth</convert>
			<convert type="ValueRange">721,1980</convert>
			<convert type="ConditionalShowHide" />
		</widget>
		<!-- VideoFormat -->
		<eLabel text="Res" font="Regular;20" position="400,95" size="50,20"  foregroundColor="#062748" backgroundColor="black" transparent="1"/>
		<widget source="session.CurrentService" render="Label" font="Regular;20" position="440,95" size="55,20" halign="right"  foregroundColor="white" backgroundColor="black" transparent="1">
			<convert type="ServiceInfo">VideoWidth</convert>
		</widget>
		<eLabel text="x" font="Regular;16" position="505,97" size="15,22" halign="center"  backgroundColor="black" transparent="1"/>
		<widget source="session.CurrentService" render="Label" font="Regular;20" position="530,95" size="55,22"   foregroundColor="white" backgroundColor="black" transparent="1">
			<convert type="ServiceInfo">VideoHeight</convert>
		</widget>
		<widget source="session.CurrentService" render="Label" position="1160,95" size="120,26" font="Regular;22"  foregroundColor="yellow" backgroundColor="black" transparent="1" >
			<convert type="ServicePosition">Length</convert>
		</widget>
	</screen>"""

class Playvid3(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):
    STATE_PLAYING = 1
    STATE_PAUSED = 2

    def __init__(self, session, name, url, desc):

        Screen.__init__(self, session)
        if DESKHEIGHT > 1000:
              self.skin = Playvid2FHD.skin
        else:
        #                      self.skin = Playvid2HD.skin
              self.skin = PlayvidB.skin
        title = "Play"
        self.sref=None
        self["title"] = Button(title)
        self["list"] = MenuList([])
        self["info"] = Label()
        self['key_yellow'] = Button(_('Subtitles'))
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self)
        InfoBarShowHide.__init__(self)
        self.statusScreen = self.session.instantiateDialog(StatusScreen)
        ##aspect ratio stuff
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0

        self.new_aspect = self.init_aspect
        ##end aspect ratio

        self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarSeekActions", "InfobarActions"],
            {
             "leavePlayer": self.cancel,
             "back":    self.cancel,
             "info":self.showinfo,
             "playpauseService":    self.playpauseService,
             "yellow":  self.subtitles,
             'down': self.av,##for aspect ratio
            }, -1)

        self.allowPiP = False
        #   initSubsSettings()
        #   SubsSupport.__init__(self, embeddedSupport=True, searchSupport=True)
        #   self.subs = True
        InfoBarSeek.__init__(self, actionmap = "MediaPlayerSeekActions")
        self.icount = 0
        self.name = name
        self.url = url
        print("Here in Playvid2 self.url = ", self.url)
        self.desc = desc
        self.pcip = "None"
        self.state = self.STATE_PLAYING
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)
    ##aspect ratio stuff
    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: _('4:3 Letterbox'),
         1: _('4:3 PanScan'),
         2: _('16:9'),
         3: _('16:9 always'),
         4: _('16:10 Letterbox'),
         5: _('16:10 PanScan'),
         6: _('16:9 Letterbox')}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
         1: '4_3_panscan',
         2: '16_9',
         3: '16_9_always',
         4: '16_10_letterbox',
         5: '16_10_panscan',
         6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        print(self.getAspectString(temp))
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)
        print(self.getAspectString(temp))
        self.statusScreen.setStatus(self.getAspectString(temp))



    def showinfo(self):
            debug=True
            try:

                 servicename,serviceurl=getserviceinfo(self.sref)
                 if servicename is not None:
                         sTitle=servicename
                 else:
                        sTitle=''

                 if serviceurl is not None:
                     sServiceref=serviceurl
                 else:
                   sServiceref=''

                 currPlay = self.session.nav.getCurrentService()

                 sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
                 sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
                 sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)

#return str(sTitle)
#message='remote keys help:\nmenu: subtitle player\nnumbers 1-6 seek back and forward\nleft and right:next and previous channel when playlist supported\ninfo:help\nup and cancel keys:exit to playlist'
                 message='stitle:'+str(sTitle)+"\n"+'sServiceref:'+str(sServiceref)+"\n"+'sTagCodec:'+str(sTagCodec)+"\n"+ 'sTagVideoCodec:'+str(sTagVideoCodec)+"\n"+'sTagAudioCodec :'+str(sTagAudioCodec)
                 # from XBMCAddonsinfo import XBMCAddonsinfoScreen
                 # self.session.open(XBMCAddonsinfoScreen,None,'XBMCAddonsPlayer',message)
                    # from XBMCAddonsinfo import XBMCAddonsinfoScreen
                    # self.session.open(XBMCAddonsinfoScreen, None, 'XBMCAddonsPlayer', message)
                 self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
            except:
                  pass

    def playpauseService(self):
        print("playpauseService")
        if self.state == self.STATE_PLAYING:
                self.pause()
                self.state = self.STATE_PAUSED
        elif self.state == self.STATE_PAUSED:
                self.unpause()
                self.state = self.STATE_PLAYING

    def pause(self):
                self.session.nav.pause(True)

    def unpause(self):
                self.session.nav.pause(False)

    def openTest(self):
                if "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url :

                      from tube_resolver.plugin import getvideo
                      self.url,error = getvideo(self.url)
                      if error is not None or self.url is None:
                         print("failed to get valid youtube stream link")
                         return

                elif "pcip" in self.url:
                       n1 = self.url.find("pcip")
                       urlA = self.url
                       self.url = self.url[:n1]
                       self.pcip = urlA[(n1+4):]

                url = self.url
                name = self.name
                print("Here in Playvid name A =", name)
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace("›", "-")
                name = name.replace(",", "-")
                print("Here in Playvid name B2 =", name)

                if url is not None:
                    url = str(url)
                    print("url final= ", url)
                    ref = eServiceReference(0x1001, 0, url)
                    ref.setName(name)
                    self.sref=ref
                    self.session.nav.stopService()
                    self.session.nav.playService(ref)
                else:
                       return

    def subtitles(self):
        try:
           self.subsMenu()
        except:
           pass
    def subtitlesX(self):
        if not os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/DD_Subt/plugin.pyo"):
                self.session.open(MessageBox, _("Subtitle Player plugin is not installed\nPlease install it."), MessageBox.TYPE_ERROR, timeout = 10)
        else:
                found = 0
                pluginlist = []
                pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
                for plugin in pluginlist:
                        if "Subtitle player" in str(plugin.name):
                                found = 1
                                break
                if found == 0:
                        self.session.open(MessageBox, _("Subtitle Player plugin Missing"), MessageBox.TYPE_ERROR, timeout = 5)
                else:
                    try:
                        plugin(session=self.session)
                    except:
                        self.session.open(MessageBox, _("Subtitle Player not working"), MessageBox.TYPE_ERROR, timeout = 5)

    def cancel(self):
                if os.path.exists("/tmp/hls.avi"):
                        os.remove("/tmp/hls.avi")
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
#                try:
                if self.pcip != "None":
                        url2 = "http://" + self.pcip + ":8080/requests/status.xml?command=pl_stop"
                        print("In Playvid2 url2 =", url2)
                        resp = urlopen(url2)
#                except:
#                     pass
                ##aspect ratio
                if not self.new_aspect == self.init_aspect:
                    try:
                        self.setAspect(self.init_aspect)
                    except:
                        pass
                #aspect ratio
                self.close()

    def keyLeft(self):
        self["text"].left()

    def keyRight(self):
        self["text"].right()

    def keyNumberGlobal(self, number):
        self["text"].number(number)

#class Playvid2X(Screen, InfoBarMenu, InfoBarBase, SubsSupport, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):
class Playvid2X(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):

    STATE_PLAYING = 1
    STATE_PAUSED = 2

    def __init__(self, session, name, url, desc):

                Screen.__init__(self, session)
                self.skinName = "Playvid"
                title = "Play"
                self.sref=None
                self["title"] = Button(title)
                self["list"] = MenuList([])
                self["info"] = Label()
                self['key_yellow'] = Button(_('Subtitles'))
                InfoBarMenu.__init__(self)
                InfoBarNotifications.__init__(self)
                InfoBarBase.__init__(self)
                InfoBarShowHide.__init__(self)
                self.statusScreen = self.session.instantiateDialog(StatusScreen)
                ##aspect ratio stuff
                try:
                    self.init_aspect = int(self.getAspect())
                except:
                    self.init_aspect = 0

                self.new_aspect = self.init_aspect
                ##end aspect ratio

                self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarSeekActions", "InfobarActions"],
                {
                        "leavePlayer":                  self.cancel,
                        "back":                         self.cancel,
                        "info":self.showinfo,
                        "playpauseService":             self.playpauseService,
                        "yellow":                          self.subtitles,
                        'down': self.av,##for aspect ratio
                }, -1)

                self.allowPiP = False
                initSubsSettings()
                SubsSupport.__init__(self, embeddedSupport=True, searchSupport=True)
                self.subs = True
                InfoBarSeek.__init__(self, actionmap = "MediaPlayerSeekActions")
                self.icount = 0
                self.name = name
                self.url = url
                print("Here in Playvid2 self.url = ", self.url)
                self.desc = desc
                self.pcip = "None"
                self.state = self.STATE_PLAYING
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.openTest)
    ##aspect ratio stuff
    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: _('4:3 Letterbox'),
         1: _('4:3 PanScan'),
         2: _('16:9'),
         3: _('16:9 always'),
         4: _('16:10 Letterbox'),
         5: _('16:10 PanScan'),
         6: _('16:9 Letterbox')}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
         1: '4_3_panscan',
         2: '16_9',
         3: '16_9_always',
         4: '16_10_letterbox',
         5: '16_10_panscan',
         6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        print(self.getAspectString(temp))
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)
        print(self.getAspectString(temp))
        self.statusScreen.setStatus(self.getAspectString(temp))



    def showinfo(self):
            debug=True
            try:

                 servicename,serviceurl=getserviceinfo(self.sref)
                 if servicename is not None:
                         sTitle=servicename
                 else:
                        sTitle=''

                 if serviceurl is not None:
                     sServiceref=serviceurl
                 else:
                   sServiceref=''

                 currPlay = self.session.nav.getCurrentService()

                 sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
                 sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
                 sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)

#return str(sTitle)
#message='remote keys help:\nmenu: subtitle player\nnumbers 1-6 seek back and forward\nleft and right:next and previous channel when playlist supported\ninfo:help\nup and cancel keys:exit to playlist'
                 message='stitle:'+str(sTitle)+"\n"+'sServiceref:'+str(sServiceref)+"\n"+'sTagCodec:'+str(sTagCodec)+"\n"+ 'sTagVideoCodec:'+str(sTagVideoCodec)+"\n"+'sTagAudioCodec :'+str(sTagAudioCodec)
                 # from XBMCAddonsinfo import XBMCAddonsinfoScreen
                 # self.session.open(XBMCAddonsinfoScreen,None,'XBMCAddonsPlayer',message)
                 self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

            except:
                  pass

    def playpauseService(self):
        print("playpauseService")
        if self.state == self.STATE_PLAYING:
            self.pause()
            self.state = self.STATE_PAUSED
        elif self.state == self.STATE_PAUSED:
            self.unpause()
            self.state = self.STATE_PLAYING

    def pause(self):
                self.session.nav.pause(True)

    def unpause(self):
                self.session.nav.pause(False)

    def openTest(self):
                if "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url :

                      from tube_resolver.plugin import getvideo
                      self.url,error = getvideo(self.url)
                      if error is not None or self.url is None:
                         print("failed to get valid youtube stream link")
                         return

                elif "pcip" in self.url:
                       n1 = self.url.find("pcip")
                       urlA = self.url
                       self.url = self.url[:n1]
                       self.pcip = urlA[(n1+4):]

                url = self.url
                name = self.name
                print("Here in Playvid name A =", name)
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace("›", "-")
                name = name.replace(",", "-")
                print("Here in Playvid name B2 =", name)

                if url is not None:
                    url = str(url)
                    print("url final= ", url)
                    ref = eServiceReference(0x1001, 0, url)
                    ref.setName(name)
                    self.sref=ref
                    self.session.nav.stopService()
                    self.session.nav.playService(ref)
                else:
                       return

    def subtitles(self):
        try:
           self.subsMenu()
        except:
           self['programm'].setText('Unable to start subtitles player')

    def subtitlesX(self):
        if not os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/DD_Subt/plugin.pyo"):
                self.session.open(MessageBox, _("Subtitle Player plugin is not installed\nPlease install it."), MessageBox.TYPE_ERROR, timeout = 10)
        else:
                found = 0
                pluginlist = []
                pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
                for plugin in pluginlist:
                        if "Subtitle player" in str(plugin.name):
                                found = 1
                                break
                if found == 0:
                        self.session.open(MessageBox, _("Subtitle Player plugin Missing"), MessageBox.TYPE_ERROR, timeout = 5)
                else:
                    try:
                        plugin(session=self.session)
                    except:
                        self.session.open(MessageBox, _("Subtitle Player not working"), MessageBox.TYPE_ERROR, timeout = 5)

    def cancel(self):
                if os.path.exists("/tmp/hls.avi"):
                        os.remove("/tmp/hls.avi")
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
#                try:
                if self.pcip != "None":
                        url2 = "http://" + self.pcip + ":8080/requests/status.xml?command=pl_stop"
                        print("In Playvid2 url2 =", url2)
                        resp = urlopen(url2)
#                except:
#                     pass
                ##aspect ratio
                if not self.new_aspect == self.init_aspect:
                    try:
                        self.setAspect(self.init_aspect)
                    except:
                        pass
                #aspect ratio
                self.close()

    def keyLeft(self):
        self["text"].left()

    def keyRight(self):
        self["text"].right()

    def keyNumberGlobal(self, number):
        self["text"].number(number)

class downloadJob(Job):
        def __init__(self, toolbox, cmdline, filename, filetitle):
                Job.__init__(self, _("Saving Video"))
                self.toolbox = toolbox
                self.retrycount = 0
                downloadTask(self, cmdline, filename, filetitle)

        def retry(self):
                assert self.status == self.FAILED
                self.retrycount += 1
                self.restart()

class downloadTask(Task):
        ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(5)
        def __init__(self, job, cmdline, filename, filetitle):
                Task.__init__(self, job, filetitle)
                self.setCmdline(cmdline)
                self.filename = filename
                self.toolbox = job.toolbox
                self.error = None
                self.lasterrormsg = None

        def processOutput(self, data):
                try:
                        if data.endswith('%)'):
                                startpos = data.rfind("sec (")+5
                                if startpos and startpos != -1:
                                        self.progress = int(float(data[startpos:-4]))
                        elif data.find('%') != -1:
                                tmpvalue = data[:data.find("%")]
                                tmpvalue = tmpvalue[tmpvalue.rfind(" "):].strip()
                                tmpvalue = tmpvalue[tmpvalue.rfind("(")+1:].strip()
                                self.progress = int(float(tmpvalue))
                        else:
                                Task.processOutput(self, data)
                except Exception as errormsg:
                        Task.processOutput(self, data)

        def processOutputLine(self, line):
                        self.error = self.ERROR_SERVER

        def afterRun(self):
                pass

#################
class RSList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 22))
        self.l.setFont(2, gFont('Regular', 24))
        self.l.setFont(3, gFont('Regular', 26))
        self.l.setFont(4, gFont('Regular', 28))
        self.l.setFont(5, gFont('Regular', 30))
        self.l.setFont(6, gFont('Regular', 32))
        self.l.setFont(7, gFont('Regular', 34))
        self.l.setFont(8, gFont('Regular', 36))
        self.l.setFont(9, gFont('Regular', 40))
        if DESKHEIGHT > 1000:
            self.l.setItemHeight(50)
        else:
            self.l.setItemHeight(40)

def RSListEntry(download):
    res = [download]
    # white = 16777215
    # yellow = 16776960
    # green = 3828297
    # col = 16777215
    # backcol = 0
    # blue = 4282611429
    white = 0xffffff
    grey = 0xb3b3b9
    green = 0x389416
    black = 0x000000
    yellow = 0xe5b243
    blue = 0x002d39
    red = 0xf07655
    col = int("0xffffff", 16)
    colsel = int("0xf07655", 16)
    backcol = int("0x000000", 16)
    backsel = int("0x000000", 16)

    png = '/usr/lib/enigma2/python/Plugins/Extensions/tvspro/res/pics/setting2.png'
    if DESKHEIGHT > 1000:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=7, text=download, color=col, color_sel = colsel, backcolor = backcol, backcolor_sel = backcol))
        # res.append(MultiContentEntryText(pos=(60, 0), size=(1200, 50), font=7, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 6), size=(34, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=2, text=download, color=col, color_sel = colsel, backcolor = backcol, backcolor_sel = backcol))
        # res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=2, text=download, color = 0xa6d1fe, flags=RT_HALIGN_LEFT))# | RT_VALIGN_CENTER
    return res

def showlist(data, list):
        icount = 0
        plist = []
        for line in data:
            name = data[icount]
            plist.append(RSListEntry(name))
            icount = icount+1
        list.setList(plist)


#################

def getserviceinfo(sref):## this def returns the current playing service name and stream_url from give sref
    try:
        p=ServiceReference(sref)
        servicename=str(p.getServiceName())
        serviceurl=str(p.getPath())
        return servicename,serviceurl
    except:
        return None, None

def addstreamboq(bouquetname=None):
           boqfile="/etc/enigma2/bouquets.tv"
           if not os.path.exists(boqfile):
              pass
           else:
              fp=open(boqfile,"r")
              lines=fp.readlines()
              fp.close()
              add=True
              for line in lines:

                 if "userbouquet."+bouquetname+".tv" in line :

                    add=False
                    break
           if add==True:
              fp=open(boqfile,"a")
              fp.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.%s.tv" ORDER BY bouquet\n'% bouquetname)
              fp.close()
              add=True

def stream2bouquet(url=None,name=None,bouquetname=None):
          error='none'
          bouquetname='TVSPROAddons'
          fileName ="/etc/enigma2/userbouquet.%s.tv" % bouquetname
          out = '#SERVICE 4097:0:0:0:0:0:0:0:0:0:%s:%s\r\n' % (quote(url), quote(name))
          try:
              addstreamboq(bouquetname)
              if not os.path.exists(fileName):
                 fp = open(fileName, 'w')
                 fp.write("#NAME %s\n"%bouquetname)
                 fp.close()
                 fp = open(fileName, 'a')
                 fp.write(out)
              else:
                 fp=open(fileName,'r')
                 lines=fp.readlines()
                 fp.close()
                 for line in lines:
                     if out in line:
                        error=(_('Stream already added to bouquet'))
                        return error
                 fp = open(fileName, 'a')
                 fp.write(out)
              fp.write("")
              fp.close()
          except:
             error=(_('Adding to bouquet failed'))
          return error

##added for need of aspect ratio
class StatusScreen(Screen):

    def __init__(self, session):
        desktop = getDesktop(0)
        size = desktop.size()
        self.sc_width = size.width()
        self.sc_height = size.height()
        statusPositionX = 50
        statusPositionY = 100
        self.delayTimer = eTimer()
        try:
               self.delayTimer_conn = self.delayTimer.timeout.connect(self.hideStatus)
        except AttributeError:
               self.delayTimer.callback.append(self.hideStatus)

        self.delayTimerDelay = 1500
        self.shown = True
        self.skin = '\n            <screen name="StatusScreen" position="%s,%s" size="%s,90" zPosition="0" backgroundColor="transparent" flags="wfNoBorder">\n                    <widget name="status" position="0,0" size="%s,70" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="yellow" shadowColor="#40101010" shadowOffset="3,3" />\n            </screen>' % (str(statusPositionX),
         str(statusPositionY),
         str(self.sc_width),
         str(self.sc_width))
        Screen.__init__(self, session)
        self.stand_alone = True
        print('initializing status display')
        self['status'] = Label('')
        self.onClose.append(self.__onClose)

    def setStatus(self, text, color = 'yellow'):
        self['status'].setText(text)
        self['status'].instance.setForegroundColor(parseColor(color))
        self.show()
        self.delayTimer.start(self.delayTimerDelay, True)

    def hideStatus(self):
        self.hide()
        self['status'].setText('')

    def __onClose(self):
        self.delayTimer.stop()
        del self.delayTimer

