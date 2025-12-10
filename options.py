#!/usr/bin/python3
#
# Name: ALT Mirror Switcher
# Autor: Aleksandr Shamaraev <shad@altlinux.org>
# License: GPLv2+
# URL: https://altlinux.space/aleksandershad
#

import os
import configparser

from PySide6.QtWidgets import QMessageBox
from gettext import gettext, bindtextdomain, textdomain

from constants import source_path, conf_path, alt_ms, locale_path

def _setup_gettext():
    try:
        locale.setlocale(locale.LC_ALL, "")
    except:
        pass
    bindtextdomain(alt_ms, locale_path)
    textdomain(alt_ms)

def check_active(_active):
    if os.path.exists(conf_path):
        _config = configparser.ConfigParser()
        _config.read(conf_path)
        if os.path.exists(_config.get('mirror','file')):
            enabled_list(_config.get('mirror','file'), _config.get('mirror','protocol'), 1)
            _setup_gettext()
            _msg = QMessageBox()
            print(gettext("The active mirror restored!"))
            _msg.setText(gettext("The active mirror restored!"))
            _msg.exec()
            return _config.get('mirror','activ')
        else:
            return _active    
    else:
        return _active

def check_branch():
    _active_branch = os.popen('rpm --eval %_priority_distbranch').read()
    _active_mirror = os.popen('rpm -qa | grep apt-conf-').read()
    if _active_branch in _active_mirror:
        return True
    elif ("p11" == _active_branch) and ("branch" in _active_mirror):
        return True
    else:
        return False

def enabled_list(_new_list, _protocol, x): #x - если это 1 то учитывать протокол, если 0, то нет
    _tmp_f = _new_list+'.tmp'
    os.rename(_new_list, _tmp_f)
    with open(_tmp_f, 'r') as _old_f, open(_new_list, 'w') as _new_f:
        for _s in _old_f:
            if x == 1:
                if _protocol in _s:
                    _new_f.write(_s.strip().replace("#", "", 1)+'\n')
                else:
                    _new_f.write(_s)
            else:
                if 'rpm' in _s:
                    _new_f.write(_s.strip().replace("#", "", 1)+'\n')
                else:
                    _new_f.write(_s)
    os.remove(_tmp_f)


def disable_active(_active_f):
    _tmp_f = _active_f+'.tmp'
    os.rename(_active_f, _tmp_f)
    with open(_tmp_f, 'r') as _old_f, open(_active_f, 'w') as _new_f:
        for _s in _old_f:
            if _s.lstrip()[0:3] == 'rpm':
                _new_f.write('#' + _s)
            else:
                _new_f.write(_s)
    os.remove(_tmp_f)


def disable_source():
    _tmp_f = source_path + '.tmp'
    os.rename(source_path, _tmp_f)
    with open(_tmp_f, 'r') as _old_f, open(source_path, 'w') as _new_f:
        for _s in _old_f:
            if _s.lstrip()[0:3] == 'rpm':
                _new_f.write('#' + _s)
            else:
                _new_f.write(_s)
    os.remove(_tmp_f)