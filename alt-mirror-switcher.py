#!/usr/bin/python3
#
# Name: ALT Mirror Switcher
# Autor: Aleksandr Shamaraev <shad@altlinux.org>
# License: GPLv2+
# URL: https://altlinux.space/aleksandershad
#

import sys
import glob
import locale

from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QHBoxLayout
from PySide6.QtWidgets import QRadioButton, QLabel, QWidget, QVBoxLayout, QMessageBox, QCheckBox
from gettext import gettext, bindtextdomain, textdomain

from constants import version, alt_ms, locale_path, path_list, source_path
from options import disable_source, disable_active, enabled_list, check_branch


class Window(QMainWindow):
    
    def _checkbox_(self):
        if self._checkbox2.isChecked():
            self._button.setText(gettext("disable system *.list and enable ") + source_path)
        else:
            self._button.setText(gettext("Set mirror"))            

    def _check_enabled(self):
        if self._checkbox2.isChecked() and self._checked_flag:
            self._checked_flag = False
            self._checkbox2.setChecked(False)
        else:
            self._checked_flag = True
        self._checkbox_()

    def _check_disabled(self):
        if self._checkbox.isChecked() and self._checked_flag:           
            self._checked_flag = False
            self._checkbox.setChecked(False)
        else:
            self._checked_flag = True
        self._checkbox_()        

    def _setup_gettext(self):
        try:
            locale.setlocale(locale.LC_ALL, "")
        except:
            pass
        bindtextdomain(alt_ms, locale_path)
        textdomain(alt_ms)

    def __init__(self):
        super().__init__()

        self._setup_gettext()

        self._msg = QMessageBox()

        if check_branch(): # проверка совпадения текущего бранча на системе и пакета зеркал под этот бранч
            self._msg.setText(gettext("A difference in branches was detected. If you are using Sisyphus, <b>install apt-conf-sisyphus</b>."))
            self._msg.exec()
            sys.exit()

        self.setWindowTitle("ALT mirror switcher - "+version)
        self.resize(200, 50)

        #путь до файлов зеркал
        print(gettext("path: ") + path_list)
        
        self._list = []

        self._active = ''
        self._active_f = ''
        self._active_protocol = ''

        self._checked_flag = True

        _tmp = ''

        self._combobox = QComboBox()

        #получение именно альтовских списков репозитория
        print(gettext("getting specifically Alt repository lists"))
        for _file in glob.glob(glob.escape(path_list) + "/*.list"):
            with open(_file,'r') as file:
                for _s in file:
                    if '[alt]' in _s:
                        self._list.append(_file)
                        break
                    if '[p1' in _s:
                        self._list.append(_file)
                        break

        #заполнение выпадающего списка зеркал и опредление активного
        print(gettext("filling in the drop-down list of mirrors and determining the active one"))
        for _t in self._list:        
            with open(_t,'r') as _f:
                for _s in _f:
                    self._combobox.addItem(_s.strip().replace("#", "", 1))
                    _tmp = _s.strip().replace("#", "", 1)
                    break
                for _s in _f:
                    if _s.lstrip()[0:3] == 'rpm':
                        self._active = _tmp
                        self._active_f = _t
                        if 'http:' in _s:
                            self._active_protocol = 'http:'
                        if 'ftp:' in _s:
                            self._active_protocol = 'ftp:'
                        if 'rsync:' in _s:
                            self._active_protocol = 'rsync:'
                        if 'file:' in _s:
                            self._active_protocol = 'file:'
                        break

        self._combobox.setEditable(False)
        
        self._button = QPushButton(gettext("Set mirror"))

        self._button.clicked.connect(self.set_mirror)

        _n_labele = QLabel(gettext("Active mirror:"))

        if self._active != '':
            self._lable = QLabel('<b>' + self._active + '<b>')
        else:
            self._lable = QLabel('<b>' + gettext("No active mirror!") + '<b>')

        _n2_labele = QLabel(gettext("Protocols:"))

        self._r1_button = QRadioButton('http')
        self._r1_button.setChecked(True)
        self._r2_button = QRadioButton('ftp')
        self._r3_button = QRadioButton('rsync')
        self._r4_button = QRadioButton('file')

        _n4_labele = QLabel(gettext("Options:"))

        self._checkbox = QCheckBox(gettext("disable ") + source_path)
        self._checkbox.setChecked(True)
        self._checkbox.stateChanged.connect(self._check_enabled)

        self._checkbox2 = QCheckBox(gettext("disable system *.list and enable ") + source_path)
        self._checkbox2.setChecked(False)
        self._checkbox2.stateChanged.connect(self._check_disabled)

      
        _n3_labele = QLabel(gettext("Mirrors list:"))

        _layout = QVBoxLayout()
        _layout2 = QHBoxLayout()
        _layout.addWidget(_n_labele)
        _layout.addWidget(self._lable)
        _layout.addWidget(_n2_labele)
        _layout2.addWidget(self._r1_button)
        _layout2.addWidget(self._r2_button)
        _layout2.addWidget(self._r3_button)
        _layout2.addWidget(self._r4_button)
        _layout.addLayout(_layout2)
        _layout.addWidget(_n4_labele)
        _layout.addWidget(self._checkbox)
        _layout.addWidget(self._checkbox2)
        _layout.addWidget(_n3_labele)
        _layout.addWidget(self._combobox)
        _layout.addWidget(self._button)

        _container = QWidget()
        _container.setLayout(_layout)
        
        self.setCentralWidget(_container)

    def set_mirror(self):
        #выбор протокола для установки
        _protocol = ''
        _flag_protocol = 0

        if self._r1_button.isChecked():
            _protocol = 'http:'
            _flag_protocol = 1
            
        if self._r2_button.isChecked():
            _protocol = 'ftp:'
            _flag_protocol = 1

        if self._r3_button.isChecked():
            _protocol = 'rsync:'
            _flag_protocol = 1

        if self._r4_button.isChecked():
            _protocol = 'file:'
            _flag_protocol = 1

        if _flag_protocol == 0:
            print (gettext("set default protocol: http"))
            _protocol = 'http:'

        if self._checkbox2.isChecked() and not self._checkbox.isChecked():
            #востановление sorce/etc/apt/sources.list
            if self._active != '':
                disable_active(self._active_f)
                print(gettext("disabled: ") + self._active_f)
                self._active_protocol = _protocol
                self._active = ''
                self._active_f = ''
                self._lable.setText('<b>' + gettext("No active mirror!") + '<b>')
            enabled_list(source_path, "nil", 0)
            print(gettext("enabled: ") + source_path)
            self._msg.setText(gettext("Done!"))
            self._msg.exec()
        elif (self._active.strip() == self._combobox.currentText().strip()) and (self._active_protocol == _protocol):
            self._msg.setText(gettext("This mirror and procol has already been selected!"))
            self._msg.exec()
        else:
            #ищем новое зеркало
            _new_list = ''

            for _t in self._list:        
                with open(_t,'r') as _f:
                    for _s in _f:
                        if self._combobox.currentText() == _s.strip().replace("#", "", 1):
                            print(gettext("find: ") + _t)
                            _new_list = _t
                            break

            # проверка на наличие протокола
            __flag = 0
            with open(_new_list, 'r') as __f:
                for _s in __f:
                    if _protocol in _s:
                        __flag = 1
                        break
            if __flag != 1:
                self._msg.setText(gettext("No required protocol! Stopped."))
                self._msg.exec()
                return

            # ремарим активное зеркало
            if self._active != '':
                disable_active(self._active_f)
                print(gettext("disabled: ") + self._active_f)
            
            #устанавливаем новое зеркало
            enabled_list(_new_list, _protocol, 1)
            print(gettext("setting: ") + self._combobox.currentText())

            self._active_protocol = _protocol
            self._active = self._combobox.currentText()
            self._active_f = _new_list
            self._lable.setText('<b>' + self._combobox.currentText() + '<b>')
            
            # ремарим /etc/apt/sources.list
            if self._checkbox.isChecked():
                disable_source()
                print(gettext("disabled: ") + source_path)

            self._msg.setText(gettext("Done!"))
            self._msg.exec()

app = QApplication([])
alt_mirror_switcher = Window()
alt_mirror_switcher.show()
app.exec()