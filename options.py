#!/usr/bin/python3
#
# Name: ALT Mirror Switcher
# Autor: Aleksandr Shamaraev <shad@altlinux.org>
# License: GPLv2+
# URL: https://altlinux.space/aleksandershad
#

import os
import glob
import configparser

from PySide6.QtWidgets import QMessageBox
from gettext import gettext, bindtextdomain, textdomain

from constants import source_path, conf_path, alt_ms, locale_path, path_list, ams_path

def check_protocol(_new_list,_protocol,__flag):
    with open(_new_list, 'r') as __f:
        for _s in __f:
            if _protocol in _s:
                __flag = 1
                break
    return __flag

def del_ams_path():
    if os.path.exists(ams_path):
        os.remove(ams_path)

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

def check_ams_mirror():
    _active_branch = os.popen('rpm --eval %_priority_distbranch').read().strip()
    _ams_mirror = os.popen('rpm -qa | grep switcher-lists-').read().strip()
    _active_list = ''
    _list = []

    if _ams_mirror == '':
        return True
    if os.path.exists(conf_path):
        _config = configparser.ConfigParser()
        _config.read(conf_path)
        if os.path.exists(_config.get('mirror','file')):
            _active_list = _config.get('mirror','file')
    else:
        for _file in glob.glob(glob.escape(path_list) + "/*.list"):
            with open(_file,'r') as file:
                for _s in file:
                    if '[alt]' in _s:
                        _list.append(_file)
                        break
                    if '[p1' in _s:
                        _list.append(_file)
                        break
        for _t in _list:        
            with open(_t,'r') as _f:
                for _s in _f:
                    if _s.lstrip()[0:3] == 'rpm':
                        _active_list = _t
                        break
    if _active_list == '':
        if _active_branch in _ams_mirror:
            return True
        elif ("branch" in _ams_mirror) and ("p1" in _active_branch):
            return True
        else:
            return False
    elif "ams" in _active_list:
        if ((_active_branch in _active_list) or (_active_list == ams_path)):
            return True
        elif ("branch" in _active_list) and ("p1" in _active_branch):
            return True
        else:
            return False
    else:
        return True

def check_branch():
    _active_branch = os.popen('rpm --eval %_priority_distbranch').read().strip()
    _active_mirror = os.popen('rpm -qa | grep apt-conf-').read().strip()
    if _active_branch in _active_mirror:
        return True
    elif ("p1" in _active_branch) and ("branch" in _active_mirror):
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