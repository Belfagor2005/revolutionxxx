#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext
import os

PluginLanguageDomain = 'revolutionx'
PluginLanguagePath = 'Extensions/revolutionx/res/locale'
THISPLUG = '/usr/lib/enigma2/python/Plugins/Extensions/revolutionx'
isDreamOS = False
if os.path.exists("/var/lib/dpkg/status"):
    isDreamOS = True


def paypal():
    conthelp = "If you like what I do you\n"
    conthelp += "can contribute with a coffee\n"
    conthelp += "scan the qr code and donate € 1.00"
    return conthelp


def trace_error():
    import traceback
    import sys
    try:
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=open('/tmp/traceback.log', 'a'))
    except:
        pass


def logdata(name='', data=None):
    try:
        data = str(data)
        fp = open('/tmp/revolution.log', 'a')
        fp.write(str(name) + ': ' + data + "\n")
        fp.close()
    except:
        trace_error()
        pass


def getversioninfo():
    currversion = '1.8'
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


def localeInit():
    if isDreamOS:  # check if opendreambox image
        lang = language.getLanguage()[:2]  # getLanguage returns e.g. "fi_FI" for "language_country"
        os.environ["LANGUAGE"] = lang  # Enigma doesn't set this (or LC_ALL, LC_MESSAGES, LANG). gettext needs it!
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


if isDreamOS:  # check if DreamOS image
    _ = lambda txt: gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
else:
    def _(txt):
        if gettext.dgettext(PluginLanguageDomain, txt):
            return gettext.dgettext(PluginLanguageDomain, txt)
        else:
            print(("[%s] fallback to default translation for %s" % (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)
localeInit()
language.addCallback(localeInit)
