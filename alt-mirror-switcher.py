#!/usr/bin/python3
#
# Name: ALT Mirror Switcher
# Version: 0.2.1
# Autor: Aleksandr Shamaraev <shad@altlinux.org>
# License: GPLv2+
# URL: https://github.com/AlexanderShad
#

import os
import sys
import glob

from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QLabel, QWidget, QVBoxLayout, QMessageBox

class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ALT mirror switcher")
        self.resize(200, 50)

        #пусть до файлов зеркал
        path_list = '/etc/apt/sources.list.d/'
        print('path: '+path_list)
        
        self._list = []

        _active = ''
        self._active_f = ''

        _tmp = ''

        self._combobox = QComboBox()

        #получение именно альтовских списков репозитория
        print('getting specifically Alt repository lists')
        for _file in glob.glob(glob.escape(path_list) + "/*.list"):
            with open(_file) as file:
                if ('[alt]' or '[p11]') in file.read():
                    self._list.append(_file)

        #заполнение выпадающего списка зерка и опредление активного
        print('filling in the drop-down list of mirrors and determining the active one')
        for _t in self._list:        
            with open(_t,'r') as _f:
                for _s in _f:
                    self._combobox.addItem(_s.strip().replace("#", "", 1))
                    _tmp = _s.strip().replace("#", "", 1)
                    break
                for _s in _f:
                    if _s.lstrip()[0:3] == 'rpm':
                        _active = _tmp
                        self._active_f = _t
                        break

        self._combobox.setEditable(False)
        
        self._button = QPushButton("Set mirror")

        self._button.clicked.connect(self.set_mirror)

        self._lable = QLabel()

        self._lable.setText(_active)

        self._msg = QMessageBox()

        _layout = QVBoxLayout()
        _layout.addWidget(self._lable)
        _layout.addWidget(self._combobox)
        _layout.addWidget(self._button)

        _container = QWidget()
        _container.setLayout(_layout)
        
        self.setCentralWidget(_container)

    def set_mirror(self):
        if self._lable.text().strip() == self._combobox.currentText().strip():
            self._msg.setText("This mirror has already been selected")
            self._msg.exec()
        else:
            # ремарим активное зеркало
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

            _new_list = ''

            for _t in self._list:        
                with open(_t,'r') as _f:
                    for _s in _f:
                        if self._combobox.currentText() == _s.strip().replace("#", "", 1):
                            print('find :' + _t)
                            _new_list = _t
                            break
            
            _tmp_f = _new_list+'.tmp'
            os.rename(_new_list, _tmp_f)
            with open(_tmp_f, 'r') as _old_f, open(_new_list, 'w') as _new_f:
                for _s in _old_f:
                    if 'http' in _s:
                        _new_f.write(_s.strip().replace("#", "", 1)+'\n')
                    else:
                        _new_f.write(_s)
            os.remove(_tmp_f)

            self._active_f = _new_list
            self._lable.setText(self._combobox.currentText())
            
            self._msg.setText("Done!")
            self._msg.exec()

app = QApplication([])
alt_mirror_switcher = Window()
alt_mirror_switcher.show()
app.exec()
