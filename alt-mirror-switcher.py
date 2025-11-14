#!/usr/bin/python3
#
# Name: ALT Mirror Switcher
# Version: 0.4.1
# Autor: Aleksandr Shamaraev <shad@altlinux.org>
# License: GPLv2+
# URL: https://altlinux.space/aleksandershad
#

import os
import sys
import glob

from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QHBoxLayout
from PySide6.QtWidgets import QRadioButton, QLabel, QWidget, QVBoxLayout, QMessageBox, QCheckBox

class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ALT mirror switcher - 0.4.1")
        self.resize(200, 50)

        #путь до файлов зеркал
        path_list = '/etc/apt/sources.list.d/'
        print('path: '+path_list)
        
        self._list = []

        self._active = ''
        self._active_f = ''
        self._active_protocol = ''

        _tmp = ''

        self._combobox = QComboBox()

        #получение именно альтовских списков репозитория
        print('getting specifically Alt repository lists')
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
        print('filling in the drop-down list of mirrors and determining the active one')
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
        
        self._button = QPushButton("Set mirror")

        self._button.clicked.connect(self.set_mirror)

        _n_labele = QLabel('Active mirror:')

        if self._active != '':
            self._lable = QLabel('<b>' + self._active + '<b>')
        else:
            self._lable = QLabel('<b>No active mirror!<b>')

        _n2_labele = QLabel('Protocols:')

        self._r1_button = QRadioButton('http')
        self._r1_button.setChecked(True)
        self._r2_button = QRadioButton('ftp')
        self._r3_button = QRadioButton('rsync')
        self._r4_button = QRadioButton('file')

        _n4_labele = QLabel('Options:')

        self._checkbox = QCheckBox('disable /etc/apt/sources.list')
        self._checkbox.setChecked(True)
      
        _n3_labele = QLabel('Mirrors list:')

        self._msg = QMessageBox()

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
            print ('set default protocol: http')
            _protocol = 'http:'

        if (self._active.strip() == self._combobox.currentText().strip()) and (self._active_protocol == _protocol):
            self._msg.setText("This mirror and procol has already been selected!")
            self._msg.exec()
        else:
            #ищем новое зеркало
            _new_list = ''

            for _t in self._list:        
                with open(_t,'r') as _f:
                    for _s in _f:
                        if self._combobox.currentText() == _s.strip().replace("#", "", 1):
                            print('find :' + _t)
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
                self._msg.setText("No required protocol! Stopped.")
                self._msg.exec()
                return

            # ремарим активное зеркало
            if self._active != '':
                print('disabled: ' + self._active_f)
                _tmp_f = self._active_f+'.tmp'
                os.rename(self._active_f, _tmp_f)
                with open(_tmp_f, 'r') as _old_f, open(self._active_f, 'w') as _new_f:
                    for _s in _old_f:
                        if _s.lstrip()[0:3] == 'rpm':
                            _new_f.write('#' + _s)
                        else:
                            _new_f.write(_s)
                os.remove(_tmp_f)
            
            #устанавливаем новое зеркало
            print('setting: ' + self._combobox.currentText())
           
            _tmp_f = _new_list+'.tmp'
            os.rename(_new_list, _tmp_f)
            with open(_tmp_f, 'r') as _old_f, open(_new_list, 'w') as _new_f:
                for _s in _old_f:
                    if _protocol in _s:
                        _new_f.write(_s.strip().replace("#", "", 1)+'\n')
                    else:
                        _new_f.write(_s)
            os.remove(_tmp_f)

            self._active_protocol = _protocol
            self._active = self._combobox.currentText()
            self._active_f = _new_list
            self._lable.setText('<b>' + self._combobox.currentText() + '<b>')
            
            # ремарим /etc/apt/sources.list
            if self._checkbox.isChecked():
                print('disabled: /etc/apt/sources.list')
                _tmp_f = '/etc/apt/sources.list.tmp'
                os.rename('/etc/apt/sources.list', _tmp_f)
                with open(_tmp_f, 'r') as _old_f, open('/etc/apt/sources.list', 'w') as _new_f:
                    for _s in _old_f:
                        if _s.lstrip()[0:3] == 'rpm':
                            _new_f.write('#' + _s)
                        else:
                            _new_f.write(_s)
                os.remove(_tmp_f)

            self._msg.setText("Done!")
            self._msg.exec()

app = QApplication([])
alt_mirror_switcher = Window()
alt_mirror_switcher.show()
app.exec()
