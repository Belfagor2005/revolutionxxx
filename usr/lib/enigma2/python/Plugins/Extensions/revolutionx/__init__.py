#!/usr/bin/python
# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import gettext, base64
from os import environ as os_environ
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/revolutionx/'
PluginLanguageDomain = 'revolution'
PluginLanguagePath = 'Extensions/revolution/res/locale'
# UrlSvr = 'aHR0cDov+L3BhdGJ+1d2ViLmN+vbS9pcH+R2Lw=='
# UrlSvr = UrlSvr.replace('+', '')
# UrlLst = base64.b64decode(UrlSvr)
try:
    from enigma import eMediaDatabase
    isDreamOS = True
except:
    isDreamOS = False

def localeInit():
    if isDreamOS:
        lang = language.getLanguage()[:2]
        os_environ['LANGUAGE'] = lang
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


if isDreamOS:
    _ = lambda txt: gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
    localeInit()
    language.addCallback(localeInit)
else:
    def _(txt):
        if gettext.dgettext(PluginLanguageDomain, txt):
            return gettext.dgettext(PluginLanguageDomain, txt)
        else:
            print(("[%s] fallback to default translation for %s" % (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)
    language.addCallback(localeInit())

