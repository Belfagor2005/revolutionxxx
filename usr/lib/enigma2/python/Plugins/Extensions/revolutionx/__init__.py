# -*- coding: utf-8 -*-

from __future__ import absolute_import
__author__ = "Lululla"
__email__ = "ekekaz@gmail.com"
__copyright__ = 'Copyright (c) 2024 Lululla'
__license__ = "GPL-v2"
__version__ = "1.0.0"

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext
import os

plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/revolutionx'
PluginLanguageDomain = 'revolutionx'
PluginLanguagePath = 'Extensions/revolutionx/locale'


isDreamOS = False
if os.path.exists("/usr/bin/apt-get"):
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
        traceback.print_exc(file=open('/tmp/tracebackx.log', 'a'))
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
    currversion = '1.0'
    version_file = os.path.join(plugin_path, 'version')
    if os.path.exists(version_file):
        try:
            fp = open(version_file, 'r').readlines()
            for line in fp:
                if 'version' in line:
                    currversion = line.split('=')[1].strip()
        except:
            pass
    logdata("Plugin ", plugin_path)
    logdata("Version ", currversion)
    return (currversion)


def localeInit():
    if isDreamOS:
        lang = language.getLanguage()[:2]
        os.environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


if isDreamOS:
    def _(txt):
        return gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
else:
    def _(txt):
        translated = gettext.dgettext(PluginLanguageDomain, txt)
        if translated:
            return translated
        else:
            print(("[%s] fallback to default translation for %s" % (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)

localeInit()
language.addCallback(localeInit)

installer_url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0JlbGZhZ29yMjAwNS9yZXZvbHV0aW9ueHh4L21haW4vaW5zdGFsbGVyLnNo'
developer_url = 'aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9CZWxmYWdvcjIwMDUvcmV2b2x1dGlvbnh4eA=='
