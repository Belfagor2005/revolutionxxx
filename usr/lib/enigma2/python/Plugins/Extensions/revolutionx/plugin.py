#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Info http://t.me/tivustream
****************************************
*        coded by Lululla              *
*                                      *
*             18/11/2021               *
****************************************
'''
from __future__ import print_function
from . import _
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
# from Components.HTMLComponent import *
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MovingPixmap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.List import List
from Components.Sources.Progress import Progress
from Components.Sources.Source import Source
from Components.Sources.StaticText import StaticText
from Components.config import *
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport, InfoBarNotifications
from Screens.InfoBarGenerics import InfoBarServiceNotifications, InfoBarMoviePlayerSummarySupport, InfoBarMenu
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Tools.Directories import pathExists, resolveFilename, fileExists, copyfile
from Tools.Downloader import downloadWithProgress
from Tools.LoadPixmap import LoadPixmap
from enigma import *
from enigma import RT_HALIGN_CENTER, RT_VALIGN_CENTER
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT
from enigma import eListbox, eTimer
from enigma import eListboxPythonMultiContent, eConsoleAppContainer
from enigma import eSize, iServiceInformation, eServiceReference
from enigma import getDesktop, loadPNG, gFont
from twisted.web.client import downloadPage, getPage
from xml.dom import Node, minidom
import base64
import os
import re
import sys
import ssl
import glob
import json
import hashlib
import random
import six
from os.path import splitext
try:
    from Plugins.Extensions.revolutionx.Utils import *
except:
    from . import Utils
if six.PY3:
    print('six.PY3: True ')
plugin_path = os.path.dirname(sys.modules[__name__].__file__)
global skin_path, revol, pngs, pngl, pngx, file_json, nextmodule, search, pngori, pictmp
from six.moves.urllib.request import urlopen
from six.moves.urllib.request import Request
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import quote
from six.moves.urllib.parse import quote_plus
from six.moves.urllib.parse import urlencode
from six.moves.urllib.error import HTTPError
from six.moves.urllib.error import URLError
from six.moves.urllib.request import urlretrieve

search = False
_session = None

def trace_error():
    import traceback
    try:
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=open('/tmp/traceback.log', 'a'))
    except:
        pass

def logdata(name = '', data = None):
    try:
        data=str(data)
        fp = open('/tmp/revolutionx.log', 'a')
        fp.write(str(name) + ': ' + data + "\n")
        fp.close()
    except:
        trace_error()
        pass

def getversioninfo():
    currversion = '1.2'
    version_file = plugin_path + '/version'
    if os.path.exists(version_file):
        try:
            fp = open(version_file, 'r').readlines()
            for line in fp:
                if 'version' in line:
                    currversion = line.split('=')[1].strip()
        except:
            pass
    logdata("Version ", currversion)
    return (currversion)

try:
    from OpenSSL import SSL
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

def make_request(url):
    link = []
    try:
        import requests
        if six.PY3:
            url = url.encode()
        link = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'}).text
        return link
    except ImportError:
        print("Here in client2 getUrl url =", url)
        if six.PY3:
            url = url.encode()
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urlopen(req, None, 3)
        link=response.read().decode('utf-8') #03/09/2021
        response.close()
        print("Here in client2 link =", link)
        return link
    except:
        return ''
    return

modechoices = [
                ("4097", _("IPTV(4097)")),
                ("1", _("Dvb(1)")),
                ("8193", _("eServiceUri(8193)")),
                ]

if os.path.exists("/usr/bin/gstplayer"):
    modechoices.append(("5001", _("Gstreamer(5001)")))
if os.path.exists("/usr/bin/exteplayer3"):
    modechoices.append(("5002", _("Exteplayer3(5002)")))
if os.path.exists("/usr/sbin/streamlinksrv"):
    modechoices.append(("5002", _("Streamlink(5002)")))

config.plugins.revolutionx = ConfigSubsection()
config.plugins.revolutionx.cachefold = ConfigDirectory(default='/media/hdd/revolutionx/')
config.plugins.revolutionx.services = ConfigSelection(default='4097', choices = modechoices)
config.plugins.revolutionx.code = ConfigText(default = "1234")
pin = 2808
pin2 = str(config.plugins.revolutionx.code.value)
currversion = getversioninfo()
title_plug = '..:: TivuStream Pro Revolution XXX V. %s ::..' % currversion
desc_plug = 'TivuStream Pro Revolution XXX'
ico_path = plugin_path + '/logo.png'
no_cover = plugin_path + '/no_coverArt.png'
res_plugin_path = plugin_path + '/res/'
ico1_path = res_plugin_path + 'pics/plugin.png'
ico3_path = res_plugin_path + 'pics/setting.png'
res_picon_plugin_path = res_plugin_path + 'picons/'
piconlive = res_picon_plugin_path + 'tv.png'
piconmovie = res_picon_plugin_path + 'cinema.png'
piconseries = res_picon_plugin_path + 'series.png'
# piconsearch = res_picon_plugin_path + 'search.png'
piconsearch = "https://tivustream.website/php_filter/kodi19/img/search.png"
piconinter = res_picon_plugin_path + 'inter.png'
pixmaps = res_picon_plugin_path + 'backg.png'
revol = config.plugins.revolutionx.cachefold.value.strip()
imgjpg = ("nasa1.jpg", "nasa2.jpg", "nasa.jpg", "fulltop.jpg")
pngori = plugin_path + '/res/pics/fulltop.jpg'
Path_Tmp = "/tmp"
pictmp = Path_Tmp + "/poster.jpg"
if revol.endswith('/'):
    revol = revol[:-1]
if not os.path.exists(revol):
    try:
        os.makedirs(revol)
    except OSError as e:
        print(('Error creating directory %s:\n%s') % (revol, str(e)))
logdata("path picons: ", str(revol))

if isFHD():
    skin_path = res_plugin_path + 'skins/fhd/'
else:
    skin_path = res_plugin_path + 'skins/hd/'
if os.path.exists('/var/lib/dpkg/status'):
    skin_path = skin_path + 'dreamOs/'

REGEX = re.compile(
		r'([\(\[]).*?([\)\]])|'
		r'(: odc.\d+)|'
		r'(\d+: odc.\d+)|'
		r'(\d+ odc.\d+)|(:)|'
		r'( -(.*?).*)|(,)|'
		r'!|'
		r'/.*|'
		r'\|\s[0-9]+\+|'
		r'[0-9]+\+|'
		r'\s\d{4}\Z|'
		r'([\(\[\|].*?[\)\]\|])|'
		r'(\"|\"\.|\"\,|\.)\s.+|'
		r'\"|:|'
		r'Премьера\.\s|'
		r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
		r'(х|Х|м|М|т|Т|д|Д)/с\s|'
		r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
		r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
		r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
		r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
		r'\d{1,3}(-я|-й|\sс-н).+|', re.DOTALL)

class rvList(MenuList):
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
        if isFHD():
            self.l.setItemHeight(50)
        else:
            self.l.setItemHeight(40)

def rvListEntry(name, idx):
    pngs = ico1_path
    res = [name]
    if fileExists(pngs):
        if isFHD():
            res.append(MultiContentEntryPixmapAlphaTest(pos =(10, 12), size =(34, 25), png =loadPNG(pngs)))
            res.append(MultiContentEntryText(pos=(60, 0), size =(1900, 50), font =7, text=name, color = 0xa6d1fe, flags =RT_HALIGN_LEFT | RT_VALIGN_CENTER))
        else:
            res.append(MultiContentEntryPixmapAlphaTest(pos =(10, 6), size=(34, 25), png =loadPNG(pngs)))
            res.append(MultiContentEntryText(pos=(60, 0), size =(1000, 50), font =2, text =name, color = 0xa6d1fe, flags =RT_HALIGN_LEFT))
        return res

def rvoneListEntry(name):
    pngx = ico1_path
    res = [name]
    if isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=7, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 6), size=(34, 25), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=2, text=name, color = 0xa6d1fe, flags=RT_HALIGN_LEFT))
    return res

def showlist(data, list):
    icount = 0
    plist = []
    for line in data:
        name = data[icount]
        plist.append(rvoneListEntry(name))
        icount = icount+1
        list.setList(plist)

PanelMain = [
 ('XXXX')]

class Revolmain(Screen):
    def __init__(self, session):
        self.session = session
        global _session
        _session = session        
        skin = skin_path + 'revall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        Screen.__init__(self, session)
        # self.setTitle(title_plug)
        global nextmodule
        nextmodule = 'revolmain'
        self['text'] = rvList([])
        self.setup_title = ('HOME REVOLUTION XXX')
        self['pth'] = Label('')
        self['pth'].setText(_('Cache folder ') + revol)
        self['poster'] = Pixmap()
        self['desc'] = StaticText()
        self['space'] = Label('')
        self['info'] = Label('')
        self['info'].setText(_('Load selected filter list, please wait ...'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Exit'))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self['progresstext'].text = ''
        self.currentList = 'text'
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        idx = 0
        self.menulist = []
        self['title'] = Label(title_plug)
        self['actions'] = NumberActionMap(['SetupActions', 'DirectionActions', "EPGSelectActions", 'ColorActions', "MenuActions"], {'ok': self.okRun,
         'green': self.okRun,
         'back': self.closerm,
         'red': self.closerm,
         # 'yellow': self.remove,
         # 'blue': self.msgtqm,
         'epg': self.showIMDB,
         'info': self.showIMDB,
         'up': self.up,
         'down': self.down,
         'left': self.left,
         'right': self.right,
         'menu': self.goConfig,
         'cancel': self.closerm}, -1)
        self.onLayoutFinish.append(self.updateMenuList)
        self.onLayoutFinish.append(self.__layoutFinished)

    def showIMDB(self):
        itype = idx
        name = self.names[itype]
        text_clear = name
        if is_tmdb:
            try:
                from Plugins.Extensions.tmdb import tmdb
                text = charRemove(text_clear)
                _session.open(tmdb.tmdbScreen, text, 0)
            except Exception as e:
                print("[XCF] Tmdb: ", e)
        elif is_imdb:
            try:
                from Plugins.Extensions.IMDb.plugin import main as imdb
                text = charRemove(text_clear)
                imdb(_session, text)
            except Exception as e:
                print("[XCF] imdb: ", e) 

        else:
            inf = idx
            if inf and inf != '':
                text_clear = self.infos[inf]
            else:
                text_clear = name
            self.session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        self['info'].setText('Select')
        self.load_poster()

    def closerm(self):
        self.close()

    def updateMenuList(self):
        self.menu_list = []
        for x in self.menu_list:
            del self.menu_list[0]
        list = []
        idx = 0
        for x in PanelMain:
            list.append(rvListEntry(x, idx))
            self.menu_list.append(x)
            idx += 1
        self['text'].setList(list)
        self.load_poster()

    def okRun(self):
        self.keyNumberGlobalCB(self['text'].getSelectedIndex())

    def keyNumberGlobalCB(self, idx):
        global nextmodule
        sel = self.menu_list[idx]
        if sel == ('XXXX'):
            if str(config.plugins.revolutionx.code.value) != str(pin):
                self.mbox = self.session.open(MessageBox, _('You are not allowed!'), MessageBox.TYPE_INFO, timeout=8)
                return
            else:
                self.name = 'XXXX'
                self.url = 'https://tivustream.website/php_filter/kodi19/xxxJob.php?utKodi=TVSXXX'
                self.pic = piconlive
                nextmodule = 'xxxx'
                self.adultonly()
        else:
            self.mbox = self.session.open(MessageBox, _('Otherwise Use my Plugin Freearhey'), MessageBox.TYPE_INFO, timeout=4)

    def adultonly(self):
        self.session.openWithCallback(self.cancelConfirm, MessageBox, _('These streams may contain Adult content\n\nare you sure you want to continue??'))

    def cancelConfirm(self, result):
        if not result:
            return
        else:
            self.session.open(live_stream, self.name, self.url, self.pic, nextmodule)

    def goConfig(self):
        self.session.open(myconfig)

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
        sel = self['text'].getSelectedIndex()
        if sel != None or sel != -1:
            if sel == 0:
                pixmaps = piconlive
            else:
                pixmaps = piconinter
            size = self['poster'].instance.size()
            if os.path.exists('/var/lib/dpkg/status'):
                self['poster'].instance.setPixmap(gPixmapPtr())
            else:
                self['poster'].instance.setPixmap(None)
            sc = AVSwitch().getFramebufferScale()
            self.picload = ePicLoad()
            self.picload.setPara((size.width(),
             size.height(),
             sc[0],
             sc[1],
             False,
             1,
             '#FF000000'))
            ptr = self.picload.getData()
            if os.path.exists('/var/lib/dpkg/status'):
                if self.picload.startDecode(pixmaps, False) == 0:
                    ptr = self.picload.getData()
            else:
                if self.picload.startDecode(pixmaps, 0, 0, False) == 0:
                    ptr = self.picload.getData()
            if ptr != None:
                self['poster'].instance.setPixmap(ptr)
                self['poster'].show()
            else:
                print('no cover.. error')
            return

#Videos1
class live_stream(Screen):
    def __init__(self, session, name, url, pic, nextmodule):
        self.session = session
        global _session
        _session = session        
        skin = skin_path + 'revall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('HOME REVOLUTION XXX LIST')
        Screen.__init__(self, session)
        self.setTitle(title_plug)
        self.list = []
        self['text'] = self.list
        self['text'] = rvList([])
        self['info'] = Label(_('Load selected filter list, please wait ...'))
        self['pth'] = Label('')
        self['pth'].setText(_('Cache folder ') + revol)
        self['desc'] = StaticText()
        self['space'] = Label('')
        self["poster"] = Pixmap()
        #self["poster"].hide()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self['key_green'] = Button(_('Download'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        self.name = name
        self.url = url
        self.pic = pic
        self.type = self.name
        self.downloading = False
        self.currentList = 'text'
        idx = 0
        self['title'] = Label(title_plug)
        self['actions'] = ActionMap(['SetupActions', "EPGSelectActions", 'DirectionActions', 'ColorActions'], {'ok': self.okRun,
         # 'green': self.start_download,
         # 'yellow': self.readJsonFile,
         'red': self.cancel,
         'up': self.up,
         'down': self.down,
         'left': self.left,
         'right': self.right,
         "epg": self.showIMDB,
         "info": self.showIMDB,
         'cancel': self.cancel}, -2)
        self.readJsonFile(name, url, pic)
        self.timer = eTimer()
        self.timer.start(2000, 1)
        # self.onFirstExecBegin.append(self.download)
        self.onLayoutFinish.append(self.__layoutFinished)

    def showIMDB(self):
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        text_clear = name
        if is_tmdb:
            try:
                from Plugins.Extensions.tmdb import tmdb
                text = charRemove(text_clear)
                _session.open(tmdb.tmdbScreen, text, 0)
            except Exception as e:
                print("[XCF] Tmdb: ", e)
        elif is_imdb:
            try:
                from Plugins.Extensions.IMDb.plugin import main as imdb
                text = charRemove(text_clear)
                imdb(_session, text)
            except Exception as e:
                print("[XCF] imdb: ", e) 
        else:
            inf = idx
            if inf and inf != '':
                text_clear = self.infos[inf]
            else:
                text_clear = name
            self.session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)

    def readJsonFile(self, name, url, pic):
        global nextmodule
        strJson = make_request(url)
        # content = six.ensure_str(content)
        print('live_stream content B =', strJson)
        y = json.loads(strJson)
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        name = str(name)
        thumb = "https://www.andreisfina.it/wp-content/uploads/2018/12/no_image.jpg"
        fanart = "https://www.andreisfina.it/wp-content/uploads/2018/12/no_image.jpg"
        genre = "adult"
        info = ""
        url = 'https://tivustream.website/php_filter/kodi19/xxxJob.php?utKodi=TVSXXX'
        i = 0
        while i < 100:
            try:
                print('In live_stream y["channels"][i]["name"] =', y["channels"][i]["name"])
                name = (y["channels"][i]["name"])
                name = REGEX.sub('', name.strip())
                # print("In live_stream name =", name)
                name = str(i) + "_" + name
                pic = (y["channels"][i]["thumbnail"])
                # print("In live_stream pic =", pic)
                info = (y["channels"][i]["info"])
                # print("In live_stream info =", info)
                self.names.append(checkStr(name))
                self.urls.append(checkStr(url))
                self.pics.append(checkStr(pic))
                self.infos.append(checkStr(info))
                i = i+1
            except:
                break
            nextmodule = "Videos1"
            if nextmodule == 'Player':
                nextmodule = 'Videos3'
            if nextmodule == 'Videos3':
                nextmodule = 'Videos1'
            print('=====================')
            print(nextmodule)
            print('=====================')
        showlist(self.names, self['text'])

    def okRun(self):
        idx = self["text"].getSelectionIndex()
        if idx != None or idx != -1:
            name = self.names[idx]
            url = self.urls[idx]
            pic = self.pics[idx]
            info = self.infos[idx]
            if nextmodule == 'Videos1':
                self.session.open(video1, name, url, pic, info, nextmodule)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        self['info'].setText('Select')
        self.load_infos()
        self.load_poster()

    def load_infos(self):
        idx = self["text"].getSelectionIndex()
        print('idx: ', idx)
        if idx != None or idx != -1:
            info = self.infos[idx]
            name = self.names[idx]
            self['desc'].setText(str(info))
            self['space'].setText(str(name))

    def selectionChanged(self):
        if self["text"].getCurrent():
            currentindex = self["text"].getIndex()
            print(currentindex)

    def cancel(self):
        global nextmodule
        if nextmodule == 'Videos1':
            nextmodule = 'xxxx'

        if nextmodule == 'Videos3':
            nextmodule = 'Videos1'

        if nextmodule == 'Player':
            nextmodule = 'Videos3'

        print('cancel movie nextmodule ', nextmodule)
        self.close(None)

    def up(self):
        idx = self["text"].getSelectionIndex()
        print('idx: ', idx)
        if idx != None or idx != -1:
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
        idx = self["text"].getSelectionIndex()
        print('idx: ', idx)
        if idx != None or idx != -1:
            pixmaps = self.pics[idx]
            # pixmaps = six.ensure_binary(self.pics[idx])
            if pixmaps != "" or pixmaps != "n/A" or pixmaps != None or pixmaps != "null" :
                if pixmaps.find('http') == -1:
                    self.poster_resize(no_cover)
                    return
                else:
                    try:
                        if six.PY3:
                            pixmaps = six.ensure_binary(self.pics[idx])
                        # print("debug: pixmaps:",pixmaps)
                        # print("debug: pixmaps:",type(pixmaps))
                        if pixmaps.startswith(b"https") and sslverify:
                            parsed_uri = urlparse(pixmaps)
                            domain = parsed_uri.hostname
                            sniFactory = SNIFactory(domain)
                            # if six.PY3:
                                # pixmaps = pixmaps.encode()
                            downloadPage(pixmaps, pictmp, sniFactory, timeout=5).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                        else:
                            downloadPage(pixmaps, pictmp).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                    except Exception as ex:
                        print(ex)
                        print("Error: can't find file or read data")
                return

    def downloadPic(self, data, pictmp):
        if os.path.exists(pictmp):
            try:
                self.poster_resize(pictmp)
            except Exception as ex:
                print("* error ** %s" % ex)
                pass
            except:
                pass

    def downloadError(self, png):
        try:
            if fileExists(png):
                self.poster_resize(no_cover)
        except Exception as ex:
            self.poster_resize(no_cover)
            print(ex)
            print('exe downloadError')

    def poster_resize(self, png):
        self["poster"].hide()
        if os.path.exists(png):
            size = self['poster'].instance.size()
            self.picload = ePicLoad()
            sc = AVSwitch().getFramebufferScale()
            self.picload.setPara([size.width(), size.height(), sc[0], sc[1], False, 1, '#00000000'])
            if os.path.exists('/var/lib/dpkg/status'):
                self.picload.startDecode(png, False)
            else:
                self.picload.startDecode(png, 0, 0, False)
            ptr = self.picload.getData()
            if ptr != None:
                self['poster'].instance.setPixmap(ptr)
                self['poster'].show()
            else:
                print('no cover.. error')
            return

class video1(Screen):
    def __init__(self, session, name, url, pic, info, nextmodule):
        self.session = session
        global _session
        _session = session        
        skin = skin_path + 'revall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('HOME REVOLUTION XXX LIST')
        Screen.__init__(self, session)
        self.setTitle(title_plug)
        self.list = []
        self['text'] = self.list
        self['text'] = rvList([])
        self['info'] = Label(_('Load selected filter list, please wait ...'))
        self['pth'] = Label('')
        self['pth'].setText(_('Cache folder ') + revol)
        self['desc'] = StaticText()
        self['space'] = Label('')
        self["poster"] = Pixmap()
        #self["poster"].hide()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self['key_green'] = Button(_('Download'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        # idx = 0
        self.name = name
        self.url = url
        self.pic = pic
        self.info = info
        # print('self.name: ', self.name)
        # print('self.url: ', self.url)
        # print('self.pic: ', self.pic)
        # print('self.info: ', self.info)
        self.downloading = False
        self.currentList = 'text'
        self['title'] = Label(name)
        self['actions'] = ActionMap(['SetupActions', "EPGSelectActions", 'DirectionActions', 'ColorActions'], {'ok': self.okRun,
         # 'green': self.start_download,
         # 'yellow': self.readJsonFile,
         'red': self.cancel,
         'up': self.up,
         'down': self.down,
         'left': self.left,
         'right': self.right,
         'epg': self.showIMDB,
         'info': self.showIMDB,
         'cancel': self.cancel}, -2)
        self.timer = eTimer()
        self.timer.start(1000, 1)
        self.readJsonFile(name, url, pic)
        self.onLayoutFinish.append(self.__layoutFinished)

    def showIMDB(self):
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        text_clear = name
        if is_tmdb:
            try:
                from Plugins.Extensions.tmdb import tmdb
                text = charRemove(text_clear)
                _session.open(tmdb.tmdbScreen, text, 0)
            except Exception as e:
                print("[XCF] Tmdb: ", e)
        elif is_imdb:
            try:
                from Plugins.Extensions.IMDb.plugin import main as imdb
                text = charRemove(text_clear)
                imdb(_session, text)
            except Exception as e:
                print("[XCF] imdb: ", e)       
        else:
            inf = idx
            if inf and inf != '':
                text_clear = self.infos[inf]
            else:
                text_clear = name
            self.session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        self['info'].setText('Select')
        self.load_poster()
        self.load_infos()

    def load_infos(self):
        idx = self["text"].getSelectionIndex()
        print('idx: ', idx)
        if idx != None or idx != -1:
            info = self.infos[idx]
            name = self.names[idx]
            self['desc'].setText(str(info))
            self['space'].setText(str(name))

    def selectionChanged(self):
        if self["text"].getCurrent():
            currentindex = self["text"].getIndex()
            print(currentindex)

    def readJsonFile(self, name, url, pic):
        global nextmodule#, y
        self.name = name
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        content = make_request(self.url)
        # content = six.ensure_str(content)
        # print("content video1 =", content)
        y = json.loads(content)
        folder_path = "/tmp/tivustream/"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open("/tmp/tivustream/channels", "w") as f:
            json.dump(y, f)
        with open('/tmp/tivustream/channels') as json_file:
            y = json.load(json_file)
        x = self.name.split("_")
        n = int(x[0])
        try:
            print('In video1 y["channels"] =', y["channels"])
            # print('In video1 n y["channels"][0] =', y["channels"][n]["items"])
            # print('In video1 y["channels"][0]["name"]=', y["channels"][0]["name"])
            # print('In video1 y["channels"][self.idx]["items"]["title"]=', y["channels"][self.idx]["items"]["title"])
        except Exception as e:
            print(e)
        is_enabled = True
        title = "NO TIT"
        thumb = "https://www.andreisfina.it/wp-content/uploads/2018/12/no_image.jpg"
        fanart = "https://www.andreisfina.it/wp-content/uploads/2018/12/no_image.jpg"
        genre = "adult"
        info = ""
        regExp = ""
        resolverPar = "no_par"
        link = ""
        extLink = False
        extLink2 = False
        is_folder = False
        is_magnet = False
        is_myresolve = False
        is_regex = False
        is_m3u = False
        try:
            for item in y["channels"][n]["items"]:
                name = item["title"]
                name = REGEX.sub('', name.strip())
                # print("In live_stream title =", str(name))
                url = item["link"]
                url = url.replace("\\", "")
                # print("In live_stream link =", str(url))
                pic = item["thumbnail"]
                info = item["info"]
                # print("In live_stream info =", str(info))
                self.names.append(checkStr(name))
                self.urls.append(checkStr(url))
                self.pics.append(checkStr(pic))
                self.infos.append(checkStr(info))
            nextmodule = "Videos3"
            showlist(self.names, self['text'])
        except:
           return

    def okRun(self):
        idx = self["text"].getSelectionIndex()
        print('video1 idx: ', idx)
        if idx != None or idx != -1:
            name = self.names[idx]
            url = self.urls[idx]
            pic = self.pics[idx]
            info = self.infos[idx]
            self.session.open(video3, name, url, pic, info, nextmodule)

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
        idx = self["text"].getSelectionIndex()
        print('idx: ', idx)
        if idx != None or idx != -1:
            pixmaps = self.pics[idx]
            if pixmaps != "" or pixmaps != "n/A" or pixmaps != None or pixmaps != "null" :
                if pixmaps.find('http') == -1:
                    self.poster_resize(no_cover)
                    return
                else:
                    try:
                        if six.PY3:
                            pixmaps = six.ensure_binary(self.pics[idx])
                        # print("debug: pixmaps:",pixmaps)
                        # print("debug: pixmaps:",type(pixmaps))
                        if pixmaps.startswith(b"https") and sslverify:
                            parsed_uri = urlparse(pixmaps)
                            domain = parsed_uri.hostname
                            sniFactory = SNIFactory(domain)
                            # if six.PY3:
                                # pixmaps = pixmaps.encode()
                            downloadPage(pixmaps, pictmp, sniFactory, timeout=5).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                        else:
                            downloadPage(pixmaps, pictmp).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                    except Exception as ex:
                        print(ex)
                        print("Error: can't find file or read data")
                return

    def downloadPic(self, data, pictmp):
        if os.path.exists(pictmp):
            try:
                self.poster_resize(pictmp)
            except Exception as ex:
                print("* error ** %s" % ex)
                pass
            except:
                pass

    def downloadError(self, png):
        try:
            if fileExists(png):
                self.poster_resize(no_cover)
        except Exception as ex:
            self.poster_resize(no_cover)
            print(ex)
            print('exe downloadError')

    def poster_resize(self, png):
        self["poster"].hide()
        if os.path.exists(png):
            size = self['poster'].instance.size()
            self.picload = ePicLoad()
            sc = AVSwitch().getFramebufferScale()
            self.picload.setPara([size.width(), size.height(), sc[0], sc[1], False, 1, '#00000000'])
            if os.path.exists('/var/lib/dpkg/status'):
                self.picload.startDecode(png, False)
            else:
                self.picload.startDecode(png, 0, 0, False)
            ptr = self.picload.getData()
            if ptr != None:
                self['poster'].instance.setPixmap(ptr)
                self['poster'].show()
            else:
                print('no cover.. error')
            return

class video3(Screen):
    def __init__(self, session, name, url, pic, info, nextmodule):
        self.session = session
        global _session
        _session = session        
        skin = skin_path + 'revall.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('HOME REVOLUTION XXX LIST')
        Screen.__init__(self, session)
        self.setTitle(title_plug)
        self.list = []
        self['text'] = self.list
        self['text'] = rvList([])
        self['info'] = Label(_('Load selected filter list, please wait ...'))
        self['pth'] = Label('')
        self['pth'].setText(_('Cache folder ') + revol)
        self['desc'] = StaticText()
        self['space'] = Label('')
        self["poster"] = Pixmap()
        #self["poster"].hide()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self['progress'] = ProgressBar()
        self['progresstext'] = StaticText()
        self["progress"].hide()
        self['key_green'] = Button(_('Download'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self['key_green'].hide()
        # idx = 0
        self.name = name
        self.url = url
        self.pic = pic
        self.info = info
        print('self.name: ', self.name)
        print('self.url: ', self.url)
        print('self.pic: ', self.pic)
        print('self.info: ', self.info)
        self.downloading = False
        self.currentList = 'text'
        self['title'] = Label(name)
        self['actions'] = ActionMap(['SetupActions', "EPGSelectActions", 'DirectionActions', 'ColorActions'], {'ok': self.okRun,
         # 'green': self.start_download,
         # 'yellow': self.readJsonFile,
         'red': self.cancel,
         'up': self.up,
         'down': self.down,
         'left': self.left,
         'right': self.right,
         'epg': self.showIMDB,
         'info': self.showIMDB,
         'cancel': self.cancel}, -2)
        self.readJsonFile(name, url, pic, info)
        self.timer = eTimer()
        self.timer.start(1000, 1)
        self.onLayoutFinish.append(self.__layoutFinished)

    def showIMDB(self):
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        text_clear = name
        if is_tmdb:
            try:
                from Plugins.Extensions.tmdb import tmdb
                text = charRemove(text_clear)
                _session.open(tmdb.tmdbScreen, text, 0)
            except Exception as e:
                print("[XCF] Tmdb: ", e)
        elif is_imdb:
            try:
                from Plugins.Extensions.IMDb.plugin import main as imdb
                text = charRemove(text_clear)
                imdb(_session, text)
            except Exception as e:
                print("[XCF] imdb: ", e)        
        else:
            inf = idx
            if inf and inf != '':
                text_clear = self.infos[inf]
            else:
                text_clear = name
            self.session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)

    def __layoutFinished(self):
        self.setTitle(self.setup_title)
        self['info'].setText('Select')
        self.load_infos()
        self.load_poster()

    def load_infos(self):
        idx = self["text"].getSelectionIndex()
        print('idx: ', idx)
        if idx != None or idx != -1:
            info = self.infos[idx]
            name = self.names[idx]
        else:
            info = ''
            name = ''
        self['desc'].setText(str(info))
        self['space'].setText(str(name))

    def selectionChanged(self):
        if self["text"].getCurrent():
            currentindex = self["text"].getIndex()
            print(currentindex)

    def readJsonFile(self, name, url, pic, info):
        self.names = []
        self.urls = []
        self.pics = []
        self.infos = []
        self.names.append(name)
        self.urls.append(url)
        self.pics.append(pic)
        self.infos.append(info)
        showlist(self.names, self['text'])

    def okRun(self):
        idx = self["text"].getSelectionIndex()
        print('idx: ', idx)
        if idx != None or idx != -1:
            name = self.names[idx]
            url = self.urls[idx]
            pic = self.pics[idx]
            info = self.infos[idx]
            nextmodule = "Player"
            # print('name: ', name)
            # print('url: ', url)
            # print('png: ', pic)
            # print('info: ', info)
            print('Videos3 nextmodule - is: ', nextmodule)
            self.session.open(Playstream1, name, url, info)
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
        idx = self["text"].getSelectionIndex()
        print('idx: ', idx)
        if idx != None or idx != -1:
            pixmaps = self.pics[idx]
            if pixmaps != "" or pixmaps != "n/A" or pixmaps != None or pixmaps != "null" :
                if pixmaps.find('http') == -1:
                    self.poster_resize(no_cover)
                    return
                else:
                    try:
                        if six.PY3:
                            pixmaps = six.ensure_binary(self.pics[idx])
                        # print("debug: pixmaps:",pixmaps)
                        # print("debug: pixmaps:",type(pixmaps))
                        if pixmaps.startswith(b"https") and sslverify:
                            parsed_uri = urlparse(pixmaps)
                            domain = parsed_uri.hostname
                            sniFactory = SNIFactory(domain)
                            # if six.PY3:
                                # pixmaps = pixmaps.encode()
                            downloadPage(pixmaps, pictmp, sniFactory, timeout=5).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                        else:
                            downloadPage(pixmaps, pictmp).addCallback(self.downloadPic, pictmp).addErrback(self.downloadError)
                    except Exception as ex:
                        print(ex)
                        print("Error: can't find file or read data")
                return

    def downloadPic(self, data, pictmp):
        if os.path.exists(pictmp):
            try:
                self.poster_resize(pictmp)
            except Exception as ex:
                print("* error ** %s" % ex)
                pass
            except:
                pass

    def downloadError(self, png):
        try:
            if fileExists(png):
                self.poster_resize(no_cover)
        except Exception as ex:
            self.poster_resize(no_cover)
            print(ex)
            print('exe downloadError')

    def poster_resize(self, png):
        self["poster"].hide()
        if os.path.exists(png):
            size = self['poster'].instance.size()
            self.picload = ePicLoad()
            sc = AVSwitch().getFramebufferScale()
            self.picload.setPara([size.width(), size.height(), sc[0], sc[1], False, 1, '#00000000'])
            if os.path.exists('/var/lib/dpkg/status'):
                self.picload.startDecode(png, False)
            else:
                self.picload.startDecode(png, 0, 0, False)
            ptr = self.picload.getData()
            if ptr != None:
                self['poster'].instance.setPixmap(ptr)
                self['poster'].show()
            else:
                print('no cover.. error')
            return

class myconfig(Screen, ConfigListScreen):
    def __init__(self, session):
        skin = skin_path + 'myconfig.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.setup_title = _("Config")
        self.onChangedEntry = []
        self.session = session
        global _session
        _session = session        
        self.setTitle(title_plug)
        self['description'] = Label('')
        info = ''
        self['info'] = Label(_('Config Revolution XXX'))
        self['key_yellow'] = Button(_('Choice'))
        self['key_green'] = Button(_('Save'))
        self['key_red'] = Button(_('Back'))
        self["key_blue"] = Button(_('Empty Cache'))
        # self['key_blue'].hide()
        self['title'] = Label('Config')
        self["setupActions"] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions', 'VirtualKeyboardActions', 'ActiveCodeActions'], {'cancel': self.extnok,
         'red': self.extnok,
         'back': self.close,
         'left': self.keyLeft,
         'right': self.keyRight,
         "showVirtualKeyboard": self.KeyText,
         'yellow': self.Ok_edit,
         'ok': self.Ok_edit,
         'blue': self.cachedel,
         'green': self.msgok}, -1)
        self.list = []
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)
        if self.setInfo not in self['config'].onSelectionChanged:
            self['config'].onSelectionChanged.append(self.setInfo)

    def setInfo(self):
        entry = str(self.getCurrentEntry())
        if entry == _('Set the path to the Cache folder'):
            self['description'].setText(_("Press Ok to select the folder containing the picons files"))
            return
        if entry == _('Services Player Reference type'):
            self['description'].setText(_("Configure Service Player Reference"))
        if entry == _('Personal Password'):
            self['description'].setText(_("Set Password - ask by email to tivustream@gmail.com"))
        return

    def layoutFinished(self):
        self.setTitle(self.setup_title)
        if not os.path.exists('/tmp/currentip'):
            os.system('wget -qO- http://ipecho.net/plain > /tmp/currentip')
        currentip1 = open('/tmp/currentip', 'r')
        currentip = currentip1.read()
        self['info'].setText(_('Config Panel Addon\nYour current IP is %s') % currentip)

    def createSetup(self):
        self.editListEntry = None
        self.list = []
        self.list.append(getConfigListEntry(_("Set the path to the Cache folder"), config.plugins.revolutionx.cachefold, _("Press Ok to select the folder containing the picons files")))
        self.list.append(getConfigListEntry(_('Services Player Reference type'), config.plugins.revolutionx.services, _("Configure Service Player Reference")))
        self.list.append(getConfigListEntry(_('Personal Password'), config.plugins.revolutionx.code, _("Set Password - ask by email to tivustream@gmail.com")))

        self["config"].list = self.list
        self["config"].setList(self.list)
        # self.setInfo()

    def cachedel(self):
        fold = config.plugins.tvspro.cachefold.value + "/pic"
        cmd = "rm " + fold + "/*"
        os.system(cmd)
        self.mbox = self.session.open(MessageBox, _('All cache fold empty!'), MessageBox.TYPE_INFO, timeout=5)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        print("current selection:", self["config"].l.getCurrentSelection())
        self.createSetup()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        print("current selection:", self["config"].l.getCurrentSelection())
        self.createSetup()

    def msgok(self):
        if self['config'].isChanged():
            for x in self['config'].list:
                x[1].save()
            self.mbox = self.session.open(MessageBox, _('Settings saved correctly!'), MessageBox.TYPE_INFO, timeout=5)
            self.close()
        else:
         self.close()

    def Ok_edit(self):
        ConfigListScreen.keyOK(self)
        sel = self['config'].getCurrent()[1]
        if sel and sel == config.plugins.revolutionx.cachefold:
            self.setting = 'revol'
            mmkpth = config.plugins.revolutionx.cachefold.value
            self.openDirectoryBrowser(mmkpth)
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
             minFree=15)
        except Exception as e:
            print(('openDirectoryBrowser get failed: ', str(e)))

    def openDirectoryBrowserCB(self, path):
        if path != None:
            if self.setting == 'revol':
                config.plugins.revolutionx.cachefold.setValue(path)
        return

    def KeyText(self):
        sel = self['config'].getCurrent()
        if sel:
            self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)

    def VirtualKeyBoardCallback(self, callback = None):
        if callback != None and len(callback):
            self['config'].getCurrent()[1].value = callback
            self['config'].invalidate(self['config'].getCurrent())
        return

    def restartenigma(self, result):
        if result:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close(True)

    def changedEntry(self):
        sel = self['config'].getCurrent()
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

    def extnok(self):
        if self['config'].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _('Really close without saving the settings?'))
        else:
            self.close()

    def cancelConfirm(self, result):
        if not result:
            return
        for x in self['config'].list:
            x[1].cancel()
        self.close()

class Playstream1(Screen):
    def __init__(self, session, name, url, info):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session        
        skin = skin_path + 'Playstream1.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('Select Player Stream')
        self.list = []
        self['list'] = rvList([])
        self['info'] = Label()
        self['info'].setText('Select Player')
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Select'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'red': self.cancel,
         'green': self.okClicked,
         'back': self.cancel,
         'cancel': self.cancel,
         'ok': self.okClicked}, -2)
        self.name1 = name
        self.url = url
        self.info = info
        # if PY3:
            # self.url = url.encode('utf8')
        print('In Playstream1 self.url =', url)
        global srefInit
        self.initialservice = self.session.nav.getCurrentlyPlayingServiceReference()
        srefInit = self.initialservice
        self.onLayoutFinish.append(self.openTest)
        return

    def openTest(self):
        url = self.url
        self.names = []
        self.urls = []
        self.names.append('Play Now')
        self.urls.append(str(url))
        self.names.append('Play HLS')
        self.urls.append(str(url))
        self.names.append('Play TS')
        self.urls.append(str(url))
        # self.names.append('Preview')
        # self.urls.append(str(url))
        showlist(self.names, self['list'])

    def okClicked(self):
        idx = self['list'].getSelectionIndex()
        if idx != None or idx != -1:
            self.name = self.names[idx]
            self.url = self.urls[idx]
            if "youtube" in str(self.url):
                # self.mbox = self.session.open(MessageBox, _('For Stream Youtube coming soon!'), MessageBox.TYPE_INFO, timeout=5)
                # return
                info = self.info
                try:
                    from Plugins.Extensions.revolutionx.youtube_dl import YoutubeDL
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
                self.session.open(Playstream2, self.name, self.url, info)

            if idx == 0:
                self.name = self.names[idx]
                self.url = self.urls[idx]
                print('In playVideo url D=', self.url)
                self.play()
            elif idx == 1:
                print('In playVideo url B=', self.url)
                self.name = self.names[idx]
                self.url = self.urls[idx]
                try:
                    os.remove('/tmp/hls.avi')
                except:
                    pass
                header = ''
                cmd = 'python "/usr/lib/enigma2/python/Plugins/Extensions/Exodus/resolver/hlsclient.py" "' + self.url + '" "1" "' + header + '" + &'
                print('In playVideo cmd =', cmd)
                os.system(cmd)
                os.system('sleep 3')
                self.url = '/tmp/hls.avi'
                self.play()
            elif idx == 2:
                print('In playVideo url A=', self.url)
                url = self.url
                try:
                    os.remove('/tmp/hls.avi')
                except:
                    pass
                cmd = 'python "/usr/lib/enigma2/python/Plugins/Extensions/revolutionx/resolver/tsclient.py" "' + url + '" "1" + &'
                print('hls cmd = ', cmd)
                os.system(cmd)
                os.system('sleep 3')
                self.url = '/tmp/hls.avi'
                self.name = self.names[idx]
                self.play()

            elif idx == 3:
                self.name = self.names[idx]
                self.url = self.urls[idx]
                print('In playVideo url D=', self.url)
                self.play2()
            else:
                self.name = self.names[idx]
                self.url = self.urls[idx]
                print('In playVideo url D=', self.url)
                self.play()
            return
        return

    def playfile(self, serverint):
        self.serverList[serverint].play(self.session, self.url, self.name)

    def play(self):
        info = self.info
        url = self.url
        name = self.name1
        self.session.open(Playstream2, name, url, info)
        self.close()

    def play2(self):
        info = self.info
        name = self.name1
        if os.path.exists("/usr/sbin/streamlinksrv"):
            url = self.url
            url = url.replace(':', '%3a')
            print('In revolutionx url =', url)
            ref = '5002:0:1:0:0:0:0:0:0:0:' + 'http%3a//127.0.0.1%3a8088/' + str(url)
            # ref = '4097:0:1:0:0:0:0:0:0:0:' + url
            sref = eServiceReference(ref)
            print('SREF: ', sref)
            sref.setName(self.name1)
            self.session.open(Playstream2, name, sref, info)
            self.close()

    def cancel(self):
        try:
            password_mgr = HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.hostaddr, '', 'Admin')
            handler = HTTPBasicAuthHandler(password_mgr)
            opener = build_opener(handler)
            f = opener.open(self.hostaddr + '/requests/status.xml?command=pl_stop')
            f = opener.open(self.hostaddr + '/requests/status.xml?command=pl_empty')
        except:
            pass
        self.session.nav.stopService()
        self.session.nav.playService(srefInit)
        self.close()

class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {"toggleShow": self.OkPressed,
         "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
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

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

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

    def debug(obj, text = ""):
        print(text + " %s\n" % obj)

class Playstream2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarAudioSelection, TvInfoBarShowHide):#,InfoBarSubtitleSupport
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000

    def __init__(self, session, name, url, info):
        global SREF, streaml
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session        
        self.skinName = 'MoviePlayer'
        title = name
        streaml = False
        # self['list'] = MenuList([])
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self, steal_current_service=True)
        TvInfoBarShowHide.__init__(self)
        InfoBarAudioSelection.__init__(self)
        # InfoBarSubtitleSupport.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(['WizardActions',
         'MoviePlayerActions',
         'MovieSelectionActions',
         'MediaPlayerActions',
         'EPGSelectActions',
         'MediaPlayerSeekActions',
         'SetupActions',
         'ColorActions',
         'InfobarShowHideActions',
         'InfobarActions',
         'InfobarSeekActions'], {'leavePlayer': self.cancel,
         'epg': self.showIMDB,
         'info': self.showinfo,
         # 'info': self.cicleStreamType,
         'tv': self.cicleStreamType,
         'stop': self.leavePlayer,
         'cancel': self.cancel,
         'back': self.cancel}, -1)
        self.allowPiP = False
        self.service = None
        service = None
        InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')
        url = checkStr(url)
        self.icount = 0
        self.info = info
        self.pcip = 'None'
        self.url = url
        self.name = name
        self.state = self.STATE_PLAYING
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        SREF = self.srefOld
        if '8088' in str(self.url):
            self.onLayoutFinish.append(self.slinkPlay)
        else:
            self.onLayoutFinish.append(self.cicleStreamType)
        self.onClose.append(self.cancel)
		# self.onClose.append(self.__onClose)
        return

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
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def showinfo(self):
        debug = True
        sTitle = ''
        sServiceref = ''
        try:
            servicename, serviceurl = getserviceinfo(sref)
            if servicename != None:
                sTitle = servicename
            else:
                sTitle = ''
            if serviceurl != None:
                sServiceref = serviceurl
            else:
                sServiceref = ''
            currPlay = self.session.nav.getCurrentService()
            sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
            sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
            sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)
            message = 'stitle:' + str(sTitle) + '\n' + 'sServiceref:' + str(sServiceref) + '\n' + 'sTagCodec:' + str(sTagCodec) + '\n' + 'sTagVideoCodec:' + str(sTagVideoCodec) + '\n' + 'sTagAudioCodec:' + str(sTagAudioCodec)
            self.mbox = self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        except:
            pass

        return

    def showIMDB(self):
        text_clear = self.name
        if is_tmdb:
            try:
                from Plugins.Extensions.tmdb import tmdb
                text = charRemove(text_clear)
                _session.open(tmdb.tmdbScreen, text, 0)
            except Exception as e:
                print("[XCF] Tmdb: ", e)
        elif is_imdb:
            try:
                from Plugins.Extensions.IMDb.plugin import main as imdb
                text = charRemove(text_clear)
                imdb(_session, text)
            except Exception as e:
                print("[XCF] imdb: ", e)     
        else:
            inf = self.info
            if inf and inf != '':
                text_clear = inf
            else:
                text_clear = name
            self.session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)

    def slinkPlay(self, url):
        ref = str(url)
        ref = ref.replace(':', '%3a').replace(' ','%20')
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openPlay(self, servicetype, url):
        url = url.replace(':', '%3a').replace(' ','%20')
        ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:' + str(url)
        if streaml == True:
            ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + str(url)
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streml
        streaml = False
        from itertools import cycle, islice
        self.servicetype = str(config.plugins.revolutionx.services.value) +':0:1:0:0:0:0:0:0:0:'#  '4097'
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        currentindex = 0
        streamtypelist = ["4097"]
        # if "youtube" in str(self.url):
            # self.mbox = self.session.open(MessageBox, _('For Stream Youtube coming soon!'), MessageBox.TYPE_INFO, timeout=5)
            # return
        if os.path.exists("/usr/sbin/streamlinksrv"):
            streamtypelist.append("5002") #ref = '5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + url
            streaml = True
        if os.path.exists("/usr/bin/gstplayer"):
            streamtypelist.append("5001")
        if os.path.exists("/usr/bin/exteplayer3"):
            streamtypelist.append("5002")
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

    def cancel(self):
        if os.path.exists('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(SREF)
        if self.pcip != 'None':
            url2 = 'http://' + self.pcip + ':8080/requests/status.xml?command=pl_stop'
            resp = urlopen(url2)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        streaml = False
        self.close()

    def leavePlayer(self):
        self.close()

class plgnstrt(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + '/Plgnstrt.xml'
        f = open(skin, 'r')
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self["poster"] = Pixmap()
        self["poster"].hide()
        self.picload = ePicLoad()
        self.scale = AVSwitch().getFramebufferScale()
        self['text'] = StaticText()
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions', 'ColorActions', 'SetupActions'], {'ok': self.clsgo,
         'cancel': self.clsgo,
         'back': self.clsgo,
         'red': self.clsgo,
         'green': self.clsgo}, -1)
        # self.onShown.append(self.checkDwnld)
        self.onFirstExecBegin.append(self.loadDefaultImage)
        self.onLayoutFinish.append(self.checkDwnld)

    def poster_resize(self, pngori):
        pixmaps = pngori
        if os.path.exists('/var/lib/dpkg/status'):
            self['poster'].instance.setPixmap(gPixmapPtr())
        else:
            self['poster'].instance.setPixmap(None)
        sc = AVSwitch().getFramebufferScale()
        self.picload = ePicLoad()
        size = self['poster'].instance.size()
        self.picload.setPara((size.width(),
         size.height(),
         sc[0],
         sc[1],
         False,
         1,
         '#FF000000'))
        ptr = self.picload.getData()
        if os.path.exists('/var/lib/dpkg/status'):
            if self.picload.startDecode(pixmaps, False) == 0:
                ptr = self.picload.getData()
        else:
            if self.picload.startDecode(pixmaps, 0, 0, False) == 0:
                ptr = self.picload.getData()
        if ptr != None:
            self['poster'].instance.setPixmap(ptr)
            self['poster'].show()
        else:
            print('no cover.. error')
        return

    def image_downloaded(self):
        pngori = res_plugin_path + 'pics/fulltop.jpg'
        if os.path.exists(pngori):
            print('image pngori: ', pngori)
            try:
                self.poster_resize(pngori)
            except Exception as ex:
                print(ex)
                pass
            except:
                pass

    def loadDefaultImage(self, failure=None):
        print("*** failure *** %s" % failure)
        global pngori
        fldpng = '/usr/lib/enigma2/python/Plugins/Extensions/revolutionx/res/pics/'
        npj = random.choice(imgjpg)
        pngori = fldpng + npj
        self.poster_resize(pngori)

    def checkDwnld(self):
        self.icount = 0
        self['text'].setText(_('\n\n\nCheck Connection wait please...'))
        self.timer = eTimer()
        self.timer.start(2000, 1)
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.OpenCheck)
        else:
            self.timer.callback.append(self.OpenCheck)

    def getinfo(self):
        continfo = _("==========       WELCOME     ============\n")
        continfo += _("=========     SUPPORT ON:   ============\n")
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
            self['text'].setText(self.getinfo())
        except:
            self['text'].setText(_('\n\n' + 'Error downloading News!'))

    def error(self, error):
        self['text'].setText(_('\n\n' + 'Server Off !') + '\n' + _('check SERVER in config'))


    def clsgo(self):
        self.session.openWithCallback(self.close, Revolmain)

def checks():
    chekin= False
    if checkInternet():
            chekin = True
    return

def main(session, **kwargs):
    if checks:
        try:
            from Plugins.Extensions.revolutionx.resolver.Update import upd_done
            upd_done()
        except:       
            pass    
        if os.path.exists('/var/lib/dpkg/status'):
            session.open(Revolmain)
        else:
            session.open(plgnstrt)
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(desc_plug,
          main,
          title_plug,
          44)]
    return []

def mainmenu(session, **kwargs):
    main(session, **kwargs)

def Plugins(**kwargs):
    ico_path = 'logo.png'
    if not os.path.exists('/var/lib/dpkg/status'):
        ico_path = res_plugin_path + 'pics/logo.png'
    result = [PluginDescriptor(name =desc_plug, description =title_plug, where =[PluginDescriptor.WHERE_PLUGINMENU], icon =ico_path, fnc =main)]
    return result

'''======================================================'''
