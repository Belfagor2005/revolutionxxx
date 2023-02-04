#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*             03/02/2023               *
*       skin by MMark                  *
****************************************
Info http://t.me/tivustream
'''
from __future__ import print_function
from . import Utils
from . import html_conv
from .__init__ import _
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import ConfigDirectory, ConfigSubsection
from Components.config import ConfigYesNo, ConfigSelection
from Components.config import getConfigListEntry, ConfigText, configfile
from Components.config import config, ConfigEnableDisable
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryPixmapAlphaTest, MultiContentEntryText
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.Progress import Progress
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import MoviePlayer
from Screens.InfoBarGenerics import InfoBarNotifications
from Screens.InfoBarGenerics import InfoBarSubtitleSupport, InfoBarMenu
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarAudioSelection
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import fileExists, SCOPE_PLUGINS, resolveFilename
from Tools.Downloader import downloadWithProgress
from enigma import RT_HALIGN_LEFT
from enigma import RT_VALIGN_CENTER
from enigma import eListboxPythonMultiContent
from enigma import ePicLoad, loadPNG, gFont, gPixmapPtr
from enigma import eServiceReference
from enigma import eTimer
from enigma import iPlayableService
from os.path import splitext
from twisted.web.client import downloadPage
import base64
import os
import re
import six
import sys
import ssl
import json
import random

PY3 = False
PY3 = sys.version_info.major >= 3

try:
    from urllib.parse import urlparse
    # from urllib.request import Request
    from urllib.error import URLError
    PY3 = True
except ImportError:
    from urlparse import urlparse
    # from urllib2 import Request
    from urllib2 import URLError


if PY3:
    print('six.PY3: True ')

THISPLUG = '/usr/lib/enigma2/python/Plugins/Extensions/revolutionx'
# THISPLUG = os.path.dirname(sys.modules[__name__].__file__)
global skin_path, revol, pngs, pngl, pngx, file_json, nextmodule, search, pngori, pictmp, piconlive, piconinter

search = False
_session = None
_firstStarttvspro = True
streamlink = False
if Utils.isStreamlinkAvailable:
    streamlink = True


def trace_error():
    import traceback
    try:
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=open('/tmp/traceback.log', 'a'))
    except:
        pass


def logdata(name='', data=None):
    try:
        data = str(data)
        fp = open('/tmp/revolutionx.log', 'a')
        fp.write(str(name) + ': ' + data + "\n")
        fp.close()
    except:
        trace_error()
        pass


def getversioninfo():
    currversion = '1.3'
    version_file = os.path.join(THISPLUG, 'version')
    if os.path.exists(version_file):
        try:
            fp = open(version_file, 'r').readlines()
            for line in fp:
                if 'version' in line:
                    currversion = line.split('=')[1].strip()
        except:
            pass
    logdata("Plugin ", THISPLUG)
    logdata("Version ", currversion)
    return (currversion)


def paypal():
    conthelp = "If you like what I do you\n"
    conthelp += "can contribute with a coffee\n"
    conthelp += "scan the qr code and donate € 1.00"
    return conthelp


try:
    from twisted.internet import ssl
    from twisted.internet._sslverify import ClientTLSOptions
    sslverify = True
except:
    sslverify = False

if sslverify:
    class SNIFactory(ssl.ClientContextFactory):
        def __init__(self, hostname=None):
            self.hostname = hostname

        def getContext(self):
            ctx = self._contextFactory(self.method)
            if self.hostname:
                ClientTLSOptions(self.hostname, ctx)
            return ctx


if Utils.isFHD():
    skin_path = os.path.join(THISPLUG, 'res/skins/fhd/')
else:
    skin_path = os.path.join(THISPLUG, 'res/skins/hd/')
if Utils.DreamOS():
    skin_path = skin_path + 'dreamOs/'


class rvList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if Utils.isFHD():
            self.l.setItemHeight(50)
            textfont = int(30)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(30)
            textfont = int(24)
            self.l.setFont(0, gFont('Regular', textfont))


def rvListEntry(name, idx):
    res = [name]
    pngs = os.path.join(THISPLUG, 'res/pics/plugins.png')
    if Utils.isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(40, 40), png=loadPNG(pngs)))
        res.append(MultiContentEntryText(pos=(70, 0), size=(1000, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 3), size=(30, 30), png=loadPNG(pngs)))
        res.append(MultiContentEntryText(pos=(50, 0), size=(500, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def showlist(data, list):
    idx = 0
    plist = []
    for line in data:
        name = data[idx]
        plist.append(rvListEntry(name, idx))
        idx += 1
        list.setList(plist)


modechoices = [
        ("4097", _("IPTV(4097)")),
        ("1", _("Dvb(1)")),
    ]

if os.path.exists("/usr/bin/gstplayer"):
    modechoices.append(("5001", _("Gstreamer(5001)")))
if os.path.exists("/usr/bin/exteplayer3"):
    modechoices.append(("5002", _("Exteplayer3(5002)")))
if os.path.exists("/usr/sbin/streamlinksrv"):
    modechoices.append(("5002", _("Streamlink(5002)")))
if os.path.exists("/usr/bin/apt-get"):
    modechoices.append(("8193", _("DreamOS GStreamer(8193)")))

config.plugins.revolutionx = ConfigSubsection()
cfg = config.plugins.revolutionx
cfg.services = ConfigSelection(default='4097', choices=modechoices)
cfg.cachefold = ConfigDirectory(default='/media/hdd')
cfg.movie = ConfigDirectory("/media/hdd/movie")
try:
    from Components.UsageConfig import defaultMoviePath
    downloadpath = defaultMoviePath()
    cfg.movie = ConfigDirectory(default=downloadpath)
except:
    if os.path.exists("/usr/bin/apt-get"):
        cfg.movie = ConfigDirectory(default='/media/hdd/movie/')

cfg.code = ConfigText(default="1234")
pin = 2808
pin2 = str(cfg.code.value)

currversion = getversioninfo()
title_plug = 'Revolution XXX V.%s' % currversion
desc_plug = 'TivuStream Pro Revolution XXX'
ico_path = os.path.join(THISPLUG, 'logo.png')
res_plugin_path = os.path.join(THISPLUG, 'res/')
pngori = os.path.join(THISPLUG, 'res/pics/nasa.jpg')
piccons = os.path.join(THISPLUG, 'res/picons/')
piconlive = piccons + 'tv.png'
# piconmovie = piccons + 'cinema.png'
# piconseries = piccons + 'series.png'
# piconsearch = piccons + 'search.png'
no_cover = piccons + 'backg.png'
piconinter = piccons + 'inter.png'
pixmaps = piccons + 'backg.png'
nextpng = 'next.png'
prevpng = 'prev.png'
Path_Tmp = "/tmp"
pictmp = Path_Tmp + "/poster.jpg"
imgjpg = ("nasa.jpg", "nasa1.jpg", "nasa2.jpg")

revol = cfg.cachefold.value.strip()


global Path_Movies
Path_Movies = str(cfg.movie.value)


def cleanName(name):
    # name = name.strip()
    # filter out non-allowed characters
    non_allowed_characters = "/.\\:*?<>|\""
    name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
    name = name.replace(' ', '-').replace("'", '').replace('&', 'e')
    name = name.replace('(', '').replace(')', '')
    name = name.strip()
    name = ''.join(['_' if c in non_allowed_characters or ord(c) < 32 else c for c in name])
    return name


if not os.path.exists(revol):
    try:
        os.makedirs(revol)
    except OSError as e:
        print(('Error creating directory %s:\n%s') % (revol, str(e)))
logdata("path picons: ", str(revol))


def returnIMDB(text_clear):
    TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
    IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
    if TMDB:
        try:
            from Plugins.Extensions.TMBD.plugin import TMBD
            text = html_conv.html_unescape(text_clear)
            _session.open(TMBD.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", str(e))
        return True
    elif IMDb:
        try:
            from Plugins.Extensions.IMDb.plugin import main as imdb
            text = html_conv.html_unescape(text_clear)
            imdb(_session, text)
        except Exception as e:
            print("[XCF] imdb: ", str(e))
        return True
    else:
        text_clear = html_conv.html_unescape(text_clear)
        _session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)
        return True
    # return


PanelMain = [('XXX')]


class RevolmainX(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'revall.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        global nextmodule
        nextmodule = 'RevolmainX'
        self['list'] = rvList([])
        self.setup_title = ('HOME REVOLUTION XXX')
        self['pth'] = Label('')
        self['pth'].setText(_('Cache folder ') + revol)
        self['poster'] = Pixmap()
        self['desc'] = StaticText()
        # self['space'] = Label('')
        self['info'] = Label('')
        self['info'].setText('Select')
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Exit'))
        self['key_green'].hide()
        self.currentList = 'list'
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        self.idx = 0
        self.menulist = []
        self['title'] = Label(title_plug)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'EPGSelectActions',
                                     'ButtonSetupActions',
                                     'MenuActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'green': self.okRun,
                                                           'back': self.closerm,
                                                           'red': self.closerm,
                                                           # 'epg': self.showIMDB,
                                                           # 'info': self.showIMDB,
                                                           'up': self.up,
                                                           'down': self.down,
                                                           'left': self.left,
                                                           'right': self.right,
                                                           'menu': self.goConfig,
                                                           'cancel': self.closerm}, -1)
        self.onLayoutFinish.append(self.updateMenuList)
        self.onLayoutFinish.append(self.__layoutFinished)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        self['key_green'].show()
        self.load_poster()

    def closerm(self):
        # Utils.deletetmp()
        self.close()

    def updateMenuList(self):
        self.menu_list = []
        for x in self.menu_list:
            del self.menu_list[0]
        list = []
        self.idx = 0
        for x in PanelMain:
            list.append(rvListEntry(x, self.idx))
            self.menu_list.append(x)
            self.idx += 1
        self['list'].setList(list)
        self.name = 'XXX'
        self.load_poster()

    def okRun(self):
        self.keyNumberGlobalCB(self['list'].getSelectedIndex())

    def adultonly(self):
        self.session.openWithCallback(self.cancelConfirm, MessageBox, _('These streams may contain Adult content\n\nare you sure you want to continue??'))

    def cancelConfirm(self, result):
        if not result:
            return
        else:
            self.session.open(live_streamX, self.name, self.url, self.pic, nextmodule)

    def keyNumberGlobalCB(self, idx):
        global nextmodule
        sel = self.menu_list[idx]
        if sel == ('XXX'):
            if str(cfg.code.value) != str(pin):
                self.mbox = self.session.open(MessageBox, _('You are not allowed!'), MessageBox.TYPE_INFO, timeout=8)
                return
            else:
                self.name = 'XXX'
                self.url = 'https://tivustream.website/php_filter/kodi19/xxxJob.php?utKodi=TVSXXX'
                self.pic = pixmaps
                nextmodule = 'xxx'
                self.adultonly()
        else:
            self.mbox = self.session.open(MessageBox, _('Otherwise Use my Plugin Freearhey'), MessageBox.TYPE_INFO, timeout=4)

    def goConfig(self):
        self.session.open(myconfigX)

    def up(self):
        self[self.currentList].up()
        self.load_poster()

    def down(self):
        self[self.currentList].down()
        self.load_poster()

    def left(self):
        self[self.currentList].pageUp()
        self.load_poster()

    def right(self):
        self[self.currentList].pageDown()
        self.load_poster()

    def load_poster(self):
        try:
            sel = self['list'].getSelectedIndex()
            if sel is not None or sel != -1:
                pixmaps = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/picons/backg.png".format('revolutionx'))
                size = self['poster'].instance.size()
                if Utils.DreamOS():
                    self['poster'].instance.setPixmap(gPixmapPtr())
                else:
                    self['poster'].instance.setPixmap(None)
                self.scale = AVSwitch().getFramebufferScale()
                self.picload = ePicLoad()
                self.picload.setPara((size.width(),
                                      size.height(),
                                      self.scale[0],
                                      self.scale[1],
                                      False,
                                      1,
                                      '#FF000000'))
                ptr = self.picload.getData()
                if Utils.DreamOS():
                    if self.picload.startDecode(pixmaps, False) == 0:
                        ptr = self.picload.getData()
                else:
                    if self.picload.startDecode(pixmaps, 0, 0, False) == 0:
                        ptr = self.picload.getData()
                if ptr is not None:
                    self['poster'].instance.setPixmap(ptr)
                    self['poster'].show()
                return
        except Exception as e:
            print(e)


class myconfigX(Screen, ConfigListScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'myconfig.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = title_plug
        self.setTitle(title_plug)
        self.onChangedEntry = []
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Save'))
        self['key_yellow'] = Button(_('Choice'))
        self["key_blue"] = Button(_('Empty Cache'))
        self["paypal"] = Label()
        self['info'] = Label('')
        self['title'] = Label(title_plug)
        self['description'] = Label('')
        self["setupActions"] = ActionMap(['OkCancelActions',
                                          'DirectionActions',
                                          'ColorActions',
                                          'ButtonSetupActions',
                                          'VirtualKeyboardActions'], {'cancel': self.extnok,
                                                                      'red': self.extnok,
                                                                      'back': self.close,
                                                                      'left': self.keyLeft,
                                                                      'right': self.keyRight,
                                                                      'showVirtualKeyboard': self.KeyText,
                                                                      'yellow': self.Ok_edit,
                                                                      'ok': self.Ok_edit,
                                                                      'blue': self.cachedel,
                                                                      'green': self.msgok}, -1)
        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)
        if self.setInfo not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.setInfo)

    def layoutFinished(self):
        payp = paypal()
        self["paypal"].setText(payp)
        self.setTitle(self.setup_title)
        if not os.path.exists('/tmp/currentip'):
            os.system('wget -qO- http://ipecho.net/plain > /tmp/currentip')
        currentip1 = open('/tmp/currentip', 'r')
        currentip = currentip1.read()
        self['info'].setText(_('Settings Revolutionx \nYour current IP is %s') % currentip)

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None and len(callback):
            self['config'].getCurrent()[1].value = callback
            self['config'].invalidate(self['config'].getCurrent())

    def KeyText(self):
        sel = self['config'].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

    def cachedel(self):
        fold = os.path.join(str(cfg.cachefold.value), "revolutionx/pic")
        cmd = "rm " + fold + "/*"
        os.system(cmd)
        self.mbox = self.session.open(MessageBox, _('All cache fold are empty!'), MessageBox.TYPE_INFO, timeout=5)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_("Set the path Movie folder"), cfg.movie, _("Folder Movie Path (eg.: /media/hdd/movie), Press OK - Enigma restart required")))
        self.list.append(getConfigListEntry(_("Set the path to the Cache folder"), cfg.cachefold, _("Press Ok to select the folder containing the picons files")))
        self.list.append(getConfigListEntry(_('Services Player Reference type'), cfg.services, _("Configure Service Player Reference")))
        self.list.append(getConfigListEntry(_('Personal Password'), cfg.code, _("Set Password - ask by email to tivustream@gmail.com")))
        self['config'].list = self.list
        self["config"].l.setList(self.list)
        # self.setInfo()

    def setInfo(self):
        entry = str(self.getCurrentEntry())
        if entry == _('Set the path to the Cache folder'):
            self['description'].setText(_("Press Ok to select the folder containing the picons files"))
        if entry == _('Set the path Movie folder'):
            self['description'].setText(_("Folder Movie Path (eg.: /media/hdd/movie), Press OK - Enigma restart required"))
        if entry == _('Services Player Reference type'):
            self['description'].setText(_("Configure Service Player Reference"))
        if entry == _('Personal Password'):
            self['description'].setText(_("Set Password - ask by email to tivustream@gmail.com"))
        return

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.createSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.createSetup()

    def msgok(self):
        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()
            self.mbox = self.session.open(MessageBox, _('Settings saved correctly!'), MessageBox.TYPE_INFO, timeout=5)
            self.close()
        else:
            self.close()

    def restartenigma(self, result):
        if result:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close(True)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
        try:
            if isinstance(self['config'].getCurrent()[1], ConfigEnableDisable) or isinstance(self['config'].getCurrent()[1], ConfigYesNo) or isinstance(self['config'].getCurrent()[1], ConfigSelection):
                self.createSetup()
        except:
            pass

    def getCurrentEntry(self):
        return self['config'].getCurrent() and self['config'].getCurrent()[0] or ''

    def getCurrentValue(self):
        return self['config'].getCurrent() and str(self['config'].getCurrent()[1].getText()) or ''

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary

    def Ok_edit(self):
        ConfigListScreen.keyOK(self)
        sel = self['config'].getCurrent()[1]
        if sel and sel == cfg.cachefold:
            self.setting = 'revol'
            self.openDirectoryBrowser(cfg.cachefold.value)
        if sel and sel == cfg.movie:
            self.setting = 'moviefold'
            self.openDirectoryBrowser(cfg.movie.value)
        else:
            pass

    def openDirectoryBrowser(self, path):
        try:
            self.session.openWithCallback(
                self.openDirectoryBrowserCB,
                LocationBox,
                windowTitle=_('Choose Directory:'),
                text=_('Choose Directory'),
                currDir=str(path),
                bookmarks=config.movielist.videodirs,
                autoAdd=False,
                editDir=True,
                inhibitDirs=['/bin', '/boot', '/dev', '/home', '/lib', '/proc', '/run', '/sbin', '/sys', '/var'],
                minFree=15
            )
        except Exception as e:
            print('openDirectoryBrowser get failed: ', str(e))

    def openDirectoryBrowserCB(self, path):
        if path is not None:
            if self.setting == 'revol':
                cfg.cachefold.setValue(path)
            if self.setting == 'moviefold':
                cfg.movie.setValue(path)
        return

    def extnok(self, answer=None):
        from Screens.MessageBox import MessageBox
        if answer is None:
            if self["config"].isChanged():
                self.session.openWithCallback(self.extnok, MessageBox, _("Really close without saving settings?"))
            else:
                for x in self['config'].list:
                    x[1].save()
                self.mbox = self.session.open(MessageBox, _('Settings saved correctly!'), MessageBox.TYPE_INFO, timeout=5)
                cfg.save()
                configfile.save()
                self.close()
        elif answer:
            for x in self["config"].list:
                x[1].cancel()
            self.close()
        return


# Videos1


class live_streamX(Screen):
    def __init__(self, session, name, url, pic, nextmodule):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'revall.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('HOME REVOLUTION XXX')
        self.setTitle(title_plug)
        self.list = []
        self['list'] = self.list
        self['list'] = rvList([])
        self['info'] = Label(name)
        self['pth'] = Label('')
        self['pth'].setText(_('Cache folder ') + revol)
        self['desc'] = StaticText()
        self["poster"] = Pixmap()
        # self["poster"].hide()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self['key_red'] = Button(_('Back'))
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        self.name = name
        self.url = url
        self.pic = pic
        self.type = self.name
        self.downloading = False
        self.currentList = 'list'
        self.idx = 0
        self['title'] = Label(title_plug)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'EPGSelectActions',
                                     'MenuActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'red': self.cancel,
                                                           'up': self.up,
                                                           'down': self.down,
                                                           'left': self.left,
                                                           'right': self.right,
                                                           'epg': self.showIMDB,
                                                           'info': self.showIMDB,
                                                           'cancel': self.cancel}, -2)
        # self.readJsonFile(name, url, pic)
        self.readJsonTimer = eTimer()
        try:
            self.readJsonTimer_conn = self.readJsonTimer.timeout.connect(self.readJsonFile)
        except:
            self.readJsonTimer.callback.append(self.readJsonFile)
        self.readJsonTimer.start(200, True)
        # self.onFirstExecBegin.append(self.download)
        self.onLayoutFinish.append(self.__layoutFinished)

    def showIMDB(self):
        idx = self['list'].getSelectionIndex()
        text_clear = self.names[idx]
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def readJsonFile(self):
        global nextmodule
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        referer = 'https://tivustream.website'
        name = self.name
        url = self.url
        pic = self.pic
        info = ""
        content = Utils.ReadUrl2(url, referer)
        y = json.loads(content)
        # thumb = os.path.join(THISPLUG, 'res/pics/backg.jpg')
        # fanart = os.path.join(THISPLUG, 'res/pics/no_image.jpg')
        # genre = "adult"
        url = 'https://tivustream.website/php_filter/kodi19/xxxJob.php?utKodi=TVSXXX'
        i = 0
        while i < 100:
            # name = ""
            # url = ""
            # pic = ""
            '''
            "channels": [
                {
                    "name": "[COLOR gold]INFO ADDON[/COLOR]",
                    "thumbnail": "https://patbuweb.com/tivustream/logos/logoxxx.png",
                    "fanart": "https://interrogati.it/wp-content/uploads/2019/10/xxx.png",
                    "info": "No Info",
                    "items": [
                        {
                            "title": "[COLOR yellow][COLOR red]===[/COLOR] TIVUSTREAM [COLOR red]XxX[/COLOR] ADDON KODI V. 1.0.0. [COLOR red]===[/COLOR][/COLOR]",
                            "link": "http://patbuweb.com/iptv/e2liste/startend.avi",
                            "thumbnail": "https://patbuweb.com/tivustream/logos/logoxxx.png",
                            "fanart": "https://interrogati.it/wp-content/uploads/2019/10/xxx.png",
                            "info": "By @tivustream"
                        },
             '''
            try:
                print('In live_streamX y["channels"][i]["name"] =', y["channels"][i]["name"])
                if "title" in y["channels"][i]["items"][i]:

                    # name = (y["channels"][i]["items"][i]["name"])
                    name = (y["channels"][i]["name"])
                    # name = str(y["channels"][i]["title"])
                    name = re.sub('\[.*?\]', "", name)
                    name = cleanName(name)
                    name = str(i) + "_" + name

                # if "link" in y["channels"][i]["items"][i]:
                    # url = str(y["channels"][i]["items"][i]["link"])

                if "thumbnail" in y["channels"][i]["items"][i]:
                    # pic = str(y["channels"][i]["items"][i]["thumbnail"])
                    pic = (y["channels"][i]["thumbnail"])

                if "info" in y["channels"][i]["items"][i]:
                    # info = str(y["channels"][i]["items"][i]["info"])
                    info = str(y["channels"][i]["info"])
                    info = re.sub(r'\r\n', '', info)

                self.names.append(name)
                self.urls.append(url)
                self.pics.append(pic)
                self.infos.append(html_conv.html_unescape(info))
                i += 1
            except Exception as e:
                print(e)
                break
            nextmodule = "Videos1"
            if nextmodule == 'Player':
                nextmodule = 'Videos3'
            if nextmodule == 'Videos3':
                nextmodule = 'Videos1'
            print('=====================')
            print(nextmodule)
            print('=====================')
        showlist(self.names, self['list'])

    def okRun(self):
        i = len(self.names)
        if i < 0:
            return
        idx = self['list'].getSelectionIndex()
        if idx != '' or idx > -1:
            name = self.names[idx]
            url = self.urls[idx]
            pic = self.pics[idx]
            info = self.infos[idx]
            if nextmodule == 'Videos1':
                self.session.open(video1X, name, url, pic, info, nextmodule)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        self.load_infos()
        self.load_poster()

    def load_infos(self):
        try:
            i = len(self.names)
            if i > 0:
                idx = self['list'].getSelectionIndex()
                info = self.infos[idx]
                self['desc'].setText(info)
        except Exception as e:
            print(e)

    def selectionChanged(self):
        if self['list'].getCurrent():
            idx = self['list'].getIndex()

    def cancel(self):
        global nextmodule
        if nextmodule == 'Videos1':
            nextmodule = 'xxx'
        if nextmodule == 'Videos3':
            nextmodule = 'Videos1'
        if nextmodule == 'Player':
            nextmodule = 'Videos3'
        print('cancel movie nextmodule ', nextmodule)
        self.close()

    def up(self):
        idx = self['list'].getSelectionIndex()
        if idx and (idx != '' or idx > -1):
            self[self.currentList].up()
            self.load_infos()
            self.load_poster()
        else:
            return

    def down(self):
        self[self.currentList].down()
        self.load_infos()
        self.load_poster()

    def left(self):
        self[self.currentList].pageUp()
        self.load_infos()
        self.load_poster()

    def right(self):
        self[self.currentList].pageDown()
        self.load_infos()
        self.load_poster()

    def load_poster(self):
        try:
            i = len(self.names)
            if i > 0:
                idx = self['list'].getSelectionIndex()
                name = self.names[idx]
                pixmaps = self.pics[idx]
                if 'next' in name.lower():
                    pixmaps = str(piccons) + nextpng
                    if os.path.exists(pixmaps):
                        self.downloadPic(None, pixmaps)
                        return
                if 'prev' in name.lower():
                    pixmaps = str(piccons) + prevpng
                    if os.path.exists(pixmaps):
                        self.downloadPic(None, pixmaps)
                        return
                if pixmaps != "" or pixmaps != "n/A" or pixmaps is not None or pixmaps != "null":
                    try:
                        if PY3:
                            pixmaps = six.ensure_binary(self.pics[idx])
                        # print("debug: pixmaps:",pixmaps)
                        # print("debug: pixmaps:",type(pixmaps))
                        if pixmaps.startswith(b"https") and sslverify:
                            parsed_uri = urlparse(pixmaps)
                            domain = parsed_uri.hostname
                            sniFactory = SNIFactory(domain)
                            downloadPage(pixmaps, pictmp, sniFactory, timeout=5).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                        else:
                            downloadPage(pixmaps, pictmp).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)

    def downloadPic(self, data, pictmp):
        if os.path.exists(pictmp):
            try:
                self.poster_resize(pictmp)
            except Exception as ex:
                print("* error ** %s" % ex)
                pass

    def downloadError(self, png):
        try:
            if fileExists(png):
                self.poster_resize(no_cover)
        except Exception as e:
            self.poster_resize(no_cover)
            print(e)

    def poster_resize(self, png):
        self["poster"].hide()
        size = self['poster'].instance.size()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        # if self.picload:
        self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
        if Utils.DreamOS():
            self.picload.startDecode(png, False)
        else:
            self.picload.startDecode(png, 0, 0, False)
        ptr = self.picload.getData()
        if ptr is not None:
            self['poster'].instance.setPixmap(ptr)
            self['poster'].show()
        return


class video1X(Screen):
    def __init__(self, session, name, url, pic, info, nextmodule):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'revall.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('HOME REVOLUTION XXX')
        self.list = []
        self['list'] = self.list
        self['list'] = rvList([])
        self['info'] = Label(name)
        self['pth'] = Label('')
        self['pth'].setText(_('Cache folder ') + revol)
        self['desc'] = StaticText()
        self["poster"] = Pixmap()
        # self["poster"].hide()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self['key_red'] = Button(_('Back'))
        # self.idx = 0
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        self.name = name
        self.url = url
        self.pic = pic
        self.info = info
        self.downloading = False
        self.currentList = 'list'
        self['title'] = Label(title_plug)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'EPGSelectActions',
                                     'MenuActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'red': self.cancel,
                                                           'up': self.up,
                                                           'down': self.down,
                                                           'left': self.left,
                                                           'right': self.right,
                                                           'epg': self.showIMDB,
                                                           'info': self.showIMDB,
                                                           'cancel': self.cancel}, -2)
        self.readJsonTimer = eTimer()
        try:
            self.readJsonTimer_conn = self.readJsonTimer.timeout.connect(self.readJsonFile)
        except:
            self.readJsonTimer.callback.append(self.readJsonFile)
        self.readJsonTimer.start(2500, True)
        self.onLayoutFinish.append(self.__layoutFinished)

    def showIMDB(self):
        idx = self['list'].getSelectionIndex()
        text_clear = self.names[idx]
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        self.load_infos()
        # self.load_poster()

    def load_infos(self):
        try:
            i = len(self.names)
            if i > 0:
                idx = self['list'].getSelectionIndex()
                info = self.infos[idx]
                self['desc'].setText(info)
        except Exception as e:
            print(e)

    def selectionChanged(self):
        if self['list'].getCurrent():
            currentindex = self['list'].getIndex()
            print(currentindex)

    def readJsonFile(self):
        global nextmodule
        name = self.name
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        referer = 'https://tivustream.website'
        url = self.url
        pic = self.pic
        content = Utils.ReadUrl2(url, referer)
        y = json.loads(content)
        folder_path = "/tmp/tivustream/"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open("/tmp/tivustream/channels", "w") as f:
            json.dump(y, f)
        with open('/tmp/tivustream/channels') as json_file:
            y = json.load(json_file)

        x = name.split("_")
        n = int(x[0])
        try:
            print('In video1X y["channels"] =', y["channels"])
        except Exception as e:
            print(e)
        # is_enabled = True
        # title = "NO TIT"
        # genre = "adult"
        # info = ""
        # regExp = ""
        # resolverPar = "no_par"
        # link = ""
        # extLink = False
        # extLink2 = False
        # is_folder = False
        # is_magnet = False
        # is_myresolve = False
        # is_regex = False
        # is_m3u = False
        try:
            for item in y["channels"][n]["items"]:
                '''
                {
                    "name": "[COLOR lime]LIVE[/COLOR]",
                    "thumbnail": "https://i.ebayimg.com/images/g/gKYAAOSwFYZamqYy/s-l500.jpg",
                    "fanart": "https://interrogati.it/wp-content/uploads/2019/10/xxx.png",
                    "info": "No Info",
                    "items": [
                        {
                            "title": "[COLOR yellow] [COLOR red]---Live---[/COLOR][/COLOR]",
                            "link": "http://patbuweb.com/iptv/e2liste/startend.avi",
                            "thumbnail": "https://i.ebayimg.com/images/g/gKYAAOSwFYZamqYy/s-l500.jpg",
                            "fanart": "https://interrogati.it/wp-content/uploads/2019/10/xxx.png",
                            "info": "By @tivustream"
                        },
                '''

                # print('item = ', item)
                name = item["title"]
                name = re.sub('\[.*?\]', "", name)
                name = cleanName(name)
                url = item["link"]
                url = url.replace("\\", "")
                pic = item["thumbnail"]
                info = item["info"]
                '''
                if "title" in y["channels"][n]["items"][n]:
                    name = str(y["channels"][n]["items"][n]["title"])
                    name = re.sub('\[.*?\]', "", name)
                    name = cleanName(name)

                if "link" in y["channels"][n]["items"][n]:
                    url = (y["channels"][n]["items"][n]["link"])
                elif "yatse" in y["channels"][n]["items"][n]:
                    url = (y["channels"][n]["items"][n]["yatse"])

                if "thumbnail" in y["channels"][n]["items"][n]:
                    pic = (y["channels"][n]["items"][n]["thumbnail"])

                if "info" in y["channels"][n]["items"][n]:
                    info = str(y["channels"][n]["items"][n]["info"])
                    info = re.sub(r'\r\n', '', info)
                '''
                self.names.append(name)
                self.urls.append(url)
                self.pics.append(pic)
                self.infos.append(html_conv.html_unescape(info))

                # name = item["title"]
                # name = REGEX.sub('', name.strip())
                # # print("In live_streamX title =", str(name))
                # url = item["link"]
                # url = url.replace("\\", "")
                # # print("In live_streamX link =", str(url))
                # pic = item["thumbnail"]
                # info = item["info"]
                # # print("In live_streamX info =", str(info))
                # self.names.append(Utils.checkStr(name))
                # self.urls.append(url)
                # self.pics.append(Utils.checkStr(pic))
                # self.infos.append(Utils.checkStr(info))
            nextmodule = "Videos3"
            showlist(self.names, self['list'])
        except Exception as e:
            print(e)

    def okRun(self):
        i = len(self.names)
        if i < 0:
            return
        idx = self['list'].getSelectionIndex()
        print('item = ', idx)
        name = self.names[idx]
        url = self.urls[idx]
        pic = self.pics[idx]
        info = self.infos[idx]
        print('item tot= ', name, url, pic, info)
        self.session.open(video3X, name, url, pic, info, nextmodule)

    def cancel(self):
        global nextmodule
        if nextmodule == 'Videos3':
            nextmodule = 'Videos1'
        print('cancel movie nextmodule ', nextmodule)
        self.close(None)

    def up(self):
        self[self.currentList].up()
        self.load_infos()
        self.load_poster()

    def down(self):
        self[self.currentList].down()
        self.load_infos()
        self.load_poster()

    def left(self):
        self[self.currentList].pageUp()
        self.load_infos()
        self.load_poster()

    def right(self):
        self[self.currentList].pageDown()
        self.load_infos()
        self.load_poster()

    def load_poster(self):
        try:    
            i = len(self.names)
            if i > 0:
                idx = self['list'].getSelectionIndex()
                name = self.names[idx]
                pixmaps = self.pics[idx]
                if 'next' in name.lower():
                    pixmaps = str(piccons) + nextpng
                    if os.path.exists(pixmaps):
                        self.downloadPic(None, pixmaps)
                        return
                if 'prev' in name.lower():
                    pixmaps = str(piccons) + prevpng
                    if os.path.exists(pixmaps):
                        self.downloadPic(None, pixmaps)
                        return
                if pixmaps != "" or pixmaps != "n/A" or pixmaps is not None or pixmaps != "null":
                        if PY3:
                            pixmaps = six.ensure_binary(self.pics[idx])
                        # print("debug: pixmaps:",pixmaps)
                        # print("debug: pixmaps:",type(pixmaps))
                        if pixmaps.startswith(b"https") and sslverify:
                            parsed_uri = urlparse(pixmaps)
                            domain = parsed_uri.hostname
                            sniFactory = SNIFactory(domain)
                            downloadPage(pixmaps, pictmp, sniFactory, timeout=5).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                        else:
                            downloadPage(pixmaps, pictmp).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
        except Exception as e:
            print(e)

    def downloadPic(self, data, pictmp):
        if os.path.exists(pictmp):
            try:
                self.poster_resize(pictmp)
            except Exception as ex:
                print("* error ** %s" % ex)
                pass

    def downloadError(self, png):
        try:
            if fileExists(png):
                self.poster_resize(no_cover)
        except Exception as e:
            self.poster_resize(no_cover)
            print(e)

    def poster_resize(self, png):
        self["poster"].hide()
        size = self['poster'].instance.size()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        # if self.picload:
        self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
        if Utils.DreamOS():
            self.picload.startDecode(png, False)
        else:
            self.picload.startDecode(png, 0, 0, False)
        ptr = self.picload.getData()
        if ptr is not None:
            self['poster'].instance.setPixmap(ptr)
            self['poster'].show()
        return


class video3X(Screen):
    def __init__(self, session, name, url, pic, info, nextmodule):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'revall.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('HOME REVOLUTION XXX')
        self.list = []
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        self['list'] = self.list
        self['list'] = rvList([])
        self['info'] = Label(name)
        self['pth'] = Label('')
        self['pth'].setText(_('Cache folder ') + revol)
        self["poster"] = Pixmap()
        self['desc'] = StaticText()
        # self['space'] = Label('')
        # self["poster"].hide()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self['key_red'] = Button(_('Back'))
        # self.idx = 0
        self.name = name
        self.url = url
        self.pic = pic
        self.info = info
        self.downloading = False
        self.currentList = 'list'
        self['title'] = Label(title_plug)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'EPGSelectActions',
                                     'MenuActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'red': self.cancel,
                                                           'up': self.up,
                                                           'down': self.down,
                                                           'left': self.left,
                                                           'right': self.right,
                                                           'epg': self.showIMDB,
                                                           'info': self.showIMDB,
                                                           'cancel': self.cancel}, -2)
        # self.readJsonFile(name, url, pic, info)
        self.readJsonTimer = eTimer()
        try:
            self.readJsonTimer_conn = self.readJsonTimer.timeout.connect(self.readJsonFile)
        except:
            self.readJsonTimer.callback.append(self.readJsonFile)
        self.readJsonTimer.start(500, True)

        self.onLayoutFinish.append(self.__layoutFinished)

    def showIMDB(self):
        idx = self['list'].getSelectionIndex()
        text_clear = self.names[idx]
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        self.load_infos()
        self.load_poster()

    def load_infos(self):
        try:
            i = len(self.names)
            if i > 0:
                idx = self['list'].getSelectionIndex()
                info = self.infos[idx]
                self['desc'].setText(info)
        except Exception as e:
            print(e)

    def readJsonFile(self):
        try:
            self.names = []
            self.urls = []
            self.pics = []
            self.infos = []
            self.names.append(self.name)
            self.urls.append(self.url)
            self.pics.append(self.pic)
            self.infos.append(self.info)
            showlist(self.names, self['list'])
        except Exception as e:
            print(e)

    def okRun(self):
        idx = self['list'].getSelectionIndex()
        if idx != '' or idx > -1:
            name = self.names[idx]
            url = self.urls[idx]
            # pic = self.pics[idx]
            info = self.infos[idx]
            nextmodule = "Player"
            print('Videos3 nextmodule - is: ', nextmodule)
            self.session.open(Playstream1X, name, url, info)
        return

    def cancel(self):
        global nextmodule
        if nextmodule == 'Player':
            nextmodule = 'Videos3'
        print('cancel movie nextmodule ', nextmodule)
        self.close(None)

    def up(self):
        self[self.currentList].up()
        self.load_infos()
        self.load_poster()

    def down(self):
        self[self.currentList].down()
        self.load_infos()
        self.load_poster()

    def left(self):
        self[self.currentList].pageUp()
        self.load_infos()
        self.load_poster()

    def right(self):
        self[self.currentList].pageDown()
        self.load_infos()
        self.load_poster()

    def load_poster(self):
        try:    
            i = len(self.names)
            if i > 0:
                idx = self['list'].getSelectionIndex()
                name = self.names[idx]
                pixmaps = self.pics[idx]
                if 'next' in name.lower():
                    pixmaps = str(piccons) + nextpng
                    if os.path.exists(pixmaps):
                        self.downloadPic(None, pixmaps)
                        return
                if 'prev' in name.lower():
                    pixmaps = str(piccons) + prevpng
                    if os.path.exists(pixmaps):
                        self.downloadPic(None, pixmaps)
                        return
                if pixmaps != "" or pixmaps != "n/A" or pixmaps is not None or pixmaps != "null":
                        if PY3:
                            pixmaps = six.ensure_binary(self.pics[idx])
                        # print("debug: pixmaps:",pixmaps)
                        # print("debug: pixmaps:",type(pixmaps))
                        if pixmaps.startswith(b"https") and sslverify:
                            parsed_uri = urlparse(pixmaps)
                            domain = parsed_uri.hostname
                            sniFactory = SNIFactory(domain)
                            downloadPage(pixmaps, pictmp, sniFactory, timeout=5).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                        else:
                            downloadPage(pixmaps, pictmp).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
        except Exception as e:
            print(e)

    def downloadPic(self, data, pictmp):
        if os.path.exists(pictmp):
            try:
                self.poster_resize(pictmp)
            except Exception as ex:
                print("* error ** %s" % ex)
                pass

    def downloadError(self, png):
        try:
            if fileExists(png):
                self.poster_resize(no_cover)
        except Exception as e:
            self.poster_resize(no_cover)
            print(e)

    def poster_resize(self, png):
        self["poster"].hide()
        size = self['poster'].instance.size()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        # if self.picload:
        self.picload.setPara([size.width(), size.height(), self.scale[0], self.scale[1], 0, 1, '#00000000'])
        if Utils.DreamOS():
            self.picload.startDecode(png, False)
        else:
            self.picload.startDecode(png, 0, 0, False)
        ptr = self.picload.getData()
        if ptr is not None:
            self['poster'].instance.setPixmap(ptr)
            self['poster'].show()
        return


class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {
            "toggleShow": self.OkPressed,
            "hide": self.hide
        }, 0)

        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
            iPlayableService.evStart: self.serviceStarted
        })
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(5000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def OkPressed(self):
        self.toggleShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return
        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()

    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:
                self.doShow()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            # self.hideTimer.stop()
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def lockShow(self):
        try:
            self.__locked += 1
        except:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()

    def debug(obj, text=""):
        print(text + " %s\n" % obj)


class Playstream1X(Screen):
    def __init__(self, session, name, url, desc):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        skin = os.path.join(skin_path, 'Playstream1.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()

        self.setup_title = ('Select Player Stream')
        self.list = []
        self['list'] = rvList([])
        self['info'] = Label()
        self['info'].setText(name)
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Select'))
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self.downloading = False
        self['actions'] = ActionMap(['MoviePlayerActions',
                                     'MovieSelectionActions',
                                     'MediaPlayerActions',
                                     'EPGSelectActions',
                                     'MediaPlayerSeekActions',
                                     'DirectionActions',
                                     'ButtonSetupActions',
                                     'OkCancelActions',
                                     'InfobarShowHideActions',
                                     'InfobarActions',
                                     'InfobarSeekActions'], {'red': self.cancel,
                                                             'green': self.okClicked,
                                                             'back': self.cancel,
                                                             'cancel': self.cancel,
                                                             'leavePlayer': self.cancel,
                                                             # 'yellow': self.taskManager,
                                                             'rec': self.runRec,
                                                             'instantRecord': self.runRec,
                                                             'ShortRecord': self.runRec,
                                                             'ok': self.okClicked}, -2)
        self.name1 = cleanName(name)
        self.url = url
        self.desc = desc
        print('In Playstream1X self.url =', url)
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)
        return

    def runRec(self):
        self.namem3u = self.name1
        self.urlm3u = self.url
        if self.downloading is True:
            self.session.open(MessageBox, _('You are already downloading!!!'), MessageBox.TYPE_INFO, timeout=5)
            return
        else:
            if '.mp4' or '.mkv' or '.flv' or '.avi' in self.urlm3u:
                self.session.openWithCallback(self.download_m3u, MessageBox, _("DOWNLOAD VIDEO?\n%s" % self.namem3u), type=MessageBox.TYPE_YESNO, timeout=10, default=False)
            else:
                self.downloading = False
                self.session.open(MessageBox, _('Only VOD Movie allowed or not .ext Filtered!!!'), MessageBox.TYPE_INFO, timeout=5)

    def download_m3u(self, result):
        if result:
            if 'm3u8' not in self.urlm3u:
                path = urlparse(self.urlm3u).path
                ext = splitext(path)[1]
                if ext != '.mp4' or ext != '.mkv' or ext != '.avi' or ext != '.flv':  # or ext != 'm3u8':
                    ext = '.mp4'
                fileTitle = re.sub(r'[\<\>\:\"\/\\\|\?\*\[\]]', '_', self.namem3u)
                fileTitle = re.sub(r' ', '_', fileTitle)
                fileTitle = re.sub(r'_+', '_', fileTitle)
                fileTitle = fileTitle.replace("(", "_").replace(")", "_").replace("#", "").replace("+", "_").replace("\'", "_").replace("'", "_").replace("!", "_").replace("&", "_")
                fileTitle = fileTitle.replace(" ", "_").replace(":", "").replace("[", "").replace("]", "").replace("!", "_").replace("&", "_")
                fileTitle = fileTitle.lower() + ext
                self.in_tmp = os.path.join(Path_Movies, fileTitle)
                self.downloading = True
                try:
                    self.download = downloadWithProgress(self.urlm3u, self.in_tmp)
                    self.download.addProgress(self.downloadProgress)
                    self.download.start().addCallback(self.check).addErrback(self.showError)
                except URLError as e:
                    self.session.openWithCallback(self.ImageDownloadCB, MessageBox, _("Download Failed !!") + "\n%s" % e, type=MessageBox.TYPE_ERROR)
                    self.downloading = False
                else:
                    self.downloading = False
                    self.session.open(MessageBox, _('Download Failed!!!'), MessageBox.TYPE_INFO, timeout=5)

        else:
            self.downloading = False

    def downloadProgress(self, recvbytes, totalbytes):
        self["progress"].show()
        self['progress'].value = int(100 * recvbytes / float(totalbytes))
        self['progresstext'].text = '%d of %d kBytes (%.2f%%)' % (recvbytes / 1024, totalbytes / 1024, 100 * recvbytes / float(totalbytes))
        if recvbytes == totalbytes:
            self.downloading = False

    def check(self, fplug):
        checkfile = self.in_tmp
        if os.path.exists(checkfile):
            # self.downloading = False
            self['progresstext'].text = ''
            self.progclear = 0
            self['progress'].setValue(self.progclear)
            self["progress"].hide()

    def showError(self, error):
        self.downloading = False
        self.session.open(MessageBox, _('Download Failed!!!'), MessageBox.TYPE_INFO, timeout=5)

    def openTest(self):
        url = self.url
        self.names = []
        self.urls = []
        self.names.append('Play Now')
        self.urls.append(url)
        self.names.append('Download Now')
        self.urls.append(url)
        self.names.append('Play HLS')
        self.urls.append(url)
        self.names.append('Play TS')
        self.urls.append(url)
        self.names.append('Streamlink')
        self.urls.append(url)
        showlist(self.names, self['list'])

    def okClicked(self):
        idx = self['list'].getSelectionIndex()
        if idx is not None or idx != -1:
            self.name = self.names[idx]
            self.url = self.urls[idx]
            if "youtube" in str(self.url):
                desc = self.desc
                try:
                    from Plugins.Extensions.revolution.youtube_dl import YoutubeDL
                    '''
                    ydl_opts = {'format': 'best'}
                    ydl_opts = {'format': 'bestaudio/best'}
                    '''
                    ydl_opts = {'format': 'best'}
                    ydl = YoutubeDL(ydl_opts)
                    ydl.add_default_info_extractors()
                    result = ydl.extract_info(self.url, download=False)
                    self.url = result["url"]
                except:
                    pass
                self.session.open(Playstream2X, self.name, self.url, desc)
            if idx == 0:
                print('In playVideo url D=', self.url)
                self.play()
            elif idx == 1:
                print('In playVideo url D=', self.url)
                self.runRec()
            elif idx == 2:
                try:
                    os.remove('/tmp/hls.avi')
                except:
                    pass
                header = ''
                cmd = 'python "/usr/lib/enigma2/python/Plugins/Extensions/revolution/resolver/hlsclient.py" "' + self.url + '" "1" "' + header + '" + &'
                print('In playVideo cmd =', cmd)
                os.system(cmd)
                os.system('sleep 3')
                self.url = '/tmp/hls.avi'
                self.play()
            elif idx == 3:
                url = self.url
                try:
                    os.remove('/tmp/hls.avi')
                except:
                    pass
                cmd = 'python "/usr/lib/enigma2/python/Plugins/Extensions/revolution/resolver/tsclient.py" "' + url + '" "1" + &'
                print('hls cmd = ', cmd)
                os.system(cmd)
                os.system('sleep 3')
                self.url = '/tmp/hls.avi'
                self.play()
            else:
                if idx == 4:
                    print('In playVideo url D=', self.url)
                    self.play2()
            return

    def playfile(self, serverint):
        self.serverList[serverint].play(self.session, self.url, self.name)

    def play(self):
        desc = self.desc
        url = self.url
        name = self.name1
        self.session.open(Playstream2X, name, url, desc)
        self.close()

    def play2(self):
        if Utils.isStreamlinkAvailable():
            desc = self.desc
            name = self.name1
            url = self.url
            url = url.replace(':', '%3a')
            ref = '5002:0:1:0:0:0:0:0:0:0:' + 'http%3a//127.0.0.1%3a8088/' + str(url)
            sref = eServiceReference(ref)
            print('SREF: ', sref)
            sref.setName(name)
            self.session.open(Playstream2X, name, sref, desc)
            self.close()
        else:
            self.session.open(MessageBox, _('Install Streamlink first'), MessageBox.TYPE_INFO, timeout=5)

    def cancel(self):
        try:
            self.session.nav.stopService()
            self.session.nav.playService(self.srefInit)
            self.close()
        except:
            pass


class Playstream2X(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarAudioSelection, TvInfoBarShowHide, InfoBarSubtitleSupport):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 4000

    def __init__(self, session, name, url, desc):
        global streaml
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = 'MoviePlayer'
        streaml = False
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self, steal_current_service=True)
        TvInfoBarShowHide.__init__(self)
        InfoBarAudioSelection.__init__(self)
        InfoBarSubtitleSupport.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(['WizardActions', 'MoviePlayerActions', 'MovieSelectionActions', 'MediaPlayerActions', 'EPGSelectActions', 'MediaPlayerSeekActions', 'ColorActions',
                                     'ButtonSetupActions', 'InfobarShowHideActions', 'InfobarActions', 'InfobarSeekActions'], {
            'leavePlayer': self.cancel,
            'epg': self.showIMDB,
            'info': self.showIMDB,
            # 'info': self.cicleStreamType,
            'tv': self.cicleStreamType,
            'stop': self.leavePlayer,
            'cancel': self.cancel,
            'back': self.cancel
        }, -1)
        self.allowPiP = False
        self.service = None
        InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')
        self.desc = desc
        self.url = url
        self.name = name
        self.state = self.STATE_PLAYING
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        if '8088' in str(self.url):
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            self.onFirstExecBegin.append(self.cicleStreamType)
        return

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {
            0: '4:3 Letterbox',
            1: '4:3 PanScan',
            2: '16:9',
            3: '16:9 always',
            4: '16:10 Letterbox',
            5: '16:10 PanScan',
            6: '16:9 Letterbox'
        }[aspectnum]

    def setAspect(self, aspect):
        map = {
            0: '4_3_letterbox',
            1: '4_3_panscan',
            2: '16_9',
            3: '16_9_always',
            4: '16_10_letterbox',
            5: '16_10_panscan',
            6: '16_9_letterbox'
        }
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        temp += 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def showIMDB(self):
        text_clear = self.name
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def slinkPlay(self):
        ref = str(self.url)
        ref = ref.replace(':', '%3a').replace(' ', '%20')
        print('final reference 1:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openPlay(self, servicetype, url):
        url = url.replace(':', '%3a').replace(' ', '%20')
        ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:' + str(url)
        if streaml is True:
            ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + str(url)
        print('final reference 2:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streaml
        from itertools import cycle, islice
        self.servicetype = str(cfg.services.value)
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        if str(splitext(url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"
        currentindex = 0
        streamtypelist = ["4097"]
        """
        # if "youtube" in str(self.url):
            # self.mbox = self.session.open(MessageBox, _('For Stream Youtube coming soon!'), MessageBox.TYPE_INFO, timeout=5)
            # return
        # if Utils.isStreamlinkAvailable():
            # streamtypelist.append("5002")  # ref = '5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + url
            # streaml = True
        # elif os.path.exists("/usr/bin/gstplayer"):
            # streamtypelist.append("5001")
        # if os.path.exists("/usr/bin/exteplayer3"):
            # streamtypelist.append("5002")
            """
        if os.path.exists("/usr/bin/apt-get"):
            streamtypelist.append("8193")
        for index, item in enumerate(streamtypelist, start=0):
            if str(item) == str(self.servicetype):
                currentindex = index
                break
        nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        self.servicetype = str(next(nextStreamType))
        print('servicetype2: ', self.servicetype)
        self.openPlay(self.servicetype, url)

    # def keyNumberGlobal(self, number):
        # self['text'].number(number)

    # def keyLeft(self):
        # self['text'].left()

    # def keyRight(self):
        # self['text'].right()

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        SREF = self.srefInit
        if os.path.exists('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(SREF)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        self.close()

    def leavePlayer(self):
        self.close()


class plgnstrt(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        skin = os.path.join(skin_path, 'Plgnstrt.xml')
        with open(skin, 'r') as f:
            self.skin = f.read()
        self["poster"] = Pixmap()
        self["poster"].hide()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self['list'] = StaticText()
        self['actions'] = ActionMap(['OkCancelActions',
                                     'DirectionActions',
                                     'ColorActions'], {'ok': self.clsgo,
                                                       'cancel': self.clsgo,
                                                       'back': self.clsgo,
                                                       'red': self.clsgo,
                                                       'green': self.clsgo}, -1)
        self.onFirstExecBegin.append(self.loadDefaultImage)
        self.onLayoutFinish.append(self.checkDwnld)

    def poster_resize(self, pngori):
        pixmaps = pngori
        if Utils.DreamOS():
            self['poster'].instance.setPixmap(gPixmapPtr())
        else:
            self['poster'].instance.setPixmap(None)
        self.scale = AVSwitch().getFramebufferScale()
        self.picload = ePicLoad()
        size = self['poster'].instance.size()
        self.picload.setPara((size.width(),
                             size.height(),
                             self.scale[0],
                             self.scale[1],
                             False,
                             1,
                             '#FF000000'))
        ptr = self.picload.getData()
        if Utils.DreamOS():
            if self.picload.startDecode(pixmaps, False) == 0:
                ptr = self.picload.getData()
        else:
            if self.picload.startDecode(pixmaps, 0, 0, False) == 0:
                ptr = self.picload.getData()
        if ptr is not None:
            self['poster'].instance.setPixmap(ptr)
            self['poster'].show()
        return

    def image_downloaded(self):
        pngori = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/nasa.jpg".format('revolutionx'))
        if os.path.exists(pngori):
            try:
                self.poster_resize(pngori)
            except Exception as ex:
                print(str(ex))

    def loadDefaultImage(self, failure=None):
        import random
        print("*** failure *** %s" % failure)
        global pngori
        fldpng = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/".format('revolutionx'))
        npj = random.choice(imgjpg)
        pngori = fldpng + npj
        self.poster_resize(pngori)

    def checkDwnld(self):
        self.icount = 0
        self['list'].setText(_('\n\n\nCheck Connection wait please...'))
        self.timer = eTimer()
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self.OpenCheck)
        else:
            self.timer.callback.append(self.OpenCheck)
        self.timer.start(200, 1)

    def getinfo(self):
        continfo = _("========       WELCOME     ==========\n")
        continfo += _("=======     SUPPORT ON:   ==========\n")
        continfo += _("+WWW.TIVUSTREAM.COM - WWW.CORVOBOYS.COM+\n")
        continfo += _("http://t.me/tivustream\n\n")
        continfo += _("========================================\n")
        continfo += _("NOTA BENE:\n")
        continfo += _("Le liste create ad HOC contengono indirizzi liberamente e gratuitamente\n")
        continfo += _("trovati in rete e non protetti da sottoscrizione o abbonamento.\n")
        continfo += _("Il server di riferimento strutturale ai progetti rilasciati\n")
        continfo += _("non e' fonte di alcun stream/flusso.\n")
        continfo += _("Assolutamente VIETATO utilizzare queste liste senza autorizzazione.\n")
        continfo += _("========================================\n")
        continfo += _("DISCLAIMER: \n")
        continfo += _("The lists created at HOC contain addresses freely and freely found on\n")
        continfo += _("the net and not protected by subscription or subscription.\n")
        continfo += _("The structural reference server for projects released\n")
        continfo += _("is not a source of any stream/flow.\n")
        continfo += _("Absolutely PROHIBITED to use this lists without authorization\n")
        continfo += _("========================================\n")
        return continfo

    def OpenCheck(self):
        try:
            self['list'].setText(self.getinfo())
        except:
            self['list'].setText(_('\n\n' + 'Error downloading News!'))

    def error(self, error):
        self['list'].setText(_('\n\n' + 'Server Off !') + '\n' + _('check SERVER in config'))

    def clsgo(self):
        self.session.openWithCallback(self.close, RevolmainX)


class AutoStartTimertvsx:

    def __init__(self, session):
        self.session = session
        global _firstStarttvsx
        print("*** running AutoStartTimertvsx ***")
        if _firstStarttvsx:
            self.runUpdate()

    def runUpdate(self):
        print("*** running update ***")
        try:
            from . import Update
            Update.upd_done()
            _firstStarttvsx = False
        except Exception as e:
            print('error tvsprox', str(e))


def autostart(reason, session=None, **kwargs):
    print("*** running autostart ***")
    global autoStartTimertvsx
    global _firstStarttvsx
    if reason == 0:
        if session is not None:
            _firstStarttvsx = True
            autoStartTimertvsx = AutoStartTimertvsx(session)
    return


def main(session, **kwargs):
    try:
        session.open(RevolmainX)
    except:
        import traceback
        traceback.print_exc()
        pass


def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(desc_plug, main, title_plug, 44)]
    else:
        return []


def mainmenu(session, **kwargs):
    main(session, **kwargs)


def Plugins(**kwargs):
    ico_path = 'logo.png'
    if not os.path.exists('/var/lib/dpkg/status'):
        ico_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/logo.png".format('revolutionx'))
    result = [PluginDescriptor(name=desc_plug, description=title_plug, where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart),
              PluginDescriptor(name=desc_plug, description=title_plug, where=PluginDescriptor.WHERE_PLUGINMENU, icon=ico_path, fnc=main)]
    return result
