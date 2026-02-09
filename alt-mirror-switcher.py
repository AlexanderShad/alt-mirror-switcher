#!/usr/bin/python3
#
# Name: ALT Mirror Switcher
# Autor: Aleksandr Shamaraev <shad@altlinux.org>
# License: GPLv2+
# URL: https://altlinux.space/aleksandershad
#

import os
import sys
import glob
import locale
import configparser

from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QDate
from PySide6.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, QHBoxLayout
from PySide6.QtWidgets import QRadioButton, QLabel, QWidget, QVBoxLayout, QMessageBox, QCheckBox
from PySide6.QtWidgets import QButtonGroup, QDateEdit
from gettext import gettext

from __init__ import version
from constants import alt_ms, locale_path, path_list, source_path, conf_path
from constants import ams_path, exclude_list, archive_link, archive_end
from options import disable_source, disable_active, enabled_list, check_branch, check_active, _setup_gettext
from options import check_ams_mirror, del_ams_path, check_protocol, check_arch


class Window(QMainWindow):
    
    def _archive_sisyphus(self):
        if self._checkbox4.isChecked():
            self._r1_button.setEnabled(False)
            self._r2_button.setEnabled(False)
            self._r3_button.setEnabled(False)
            self._r4_button.setEnabled(False)
            self._r5_button.setEnabled(False)
            self._checkbox.setEnabled(False)
            self._checkbox2.setEnabled(False)
            self._checkbox3.setEnabled(False)
            self._combobox.setEnabled(False)
            self._date.setVisible(True)
            self._button.setText(gettext("set the date of the archive 'Sisyphus'"))
        else:
            self._r1_button.setEnabled(True)
            self._r2_button.setEnabled(True)
            self._r3_button.setEnabled(True)
            self._r4_button.setEnabled(True)
            self._r5_button.setEnabled(True)
            self._checkbox.setEnabled(True)
            self._checkbox2.setEnabled(True)
            self._checkbox3.setEnabled(True)
            self._combobox.setEnabled(True)
            self._date.setVisible(False)
            self._button.setText(gettext("Set mirror"))

    def _change_rb(self):
        if self._r5_button.isChecked():
            self._checkbox3.setEnabled(True)
        else:
            self._checkbox3.setEnabled(False)

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

    def __init__(self):
        super().__init__()

        _setup_gettext()

        self._msg = QMessageBox()

        if not check_branch(): # проверка совпадения текущего бранча на системе и пакета зеркал под этот бранч
            self._msg.setText(gettext("A difference in branches was detected. If you are using Sisyphus, <b>install apt-conf-sisyphus</b>."))
            self._msg.exec()
            sys.exit()

        if not check_ams_mirror(): # проверка совпадения текущего бранча на системе и фактически выбанного дополнительного листа
            self._msg.setText(gettext("A branch difference was detected. You are using additional mirrors from a different branch."))
            self._msg.exec()
            sys.exit()

        self.setWindowTitle("ALT mirror switcher - "+version)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/32x32/apps/altlinux.png"))
        self.setFixedSize(QSize(400, 300))

        #путь до файлов зеркал
        print(gettext("path: ") + path_list)
        
        self._list = []

        self._active = ''
        self._active_f = ''
        self._active_protocol = ''

        self._checked_flag = True

        _tmp = ''
        _gui_protocol = ''

        self._combobox = QComboBox()

        #получение именно альтовских списков репозитория
        print(gettext("getting specifically Alt repository lists"))
        for _file in glob.glob(glob.escape(path_list) + "/*.list"):
            if _file != exclude_list:
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
                        if 'https:' in _s:
                            self._active_protocol = 'https:'
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
            self._active = check_active(self._active)
            if self._active != '':
                self._lable = QLabel('<b>' + self._active + '<b>')
                _config = configparser.ConfigParser()
                _config.read(conf_path)
                self._active_f = _config.get('mirror','file')
            else:
                self._lable = QLabel('<b>' + gettext("No active mirror!") + '<b>')

        _n2_labele = QLabel(gettext("Protocols:"))

        if self._active_protocol == '':
            if os.path.exists(conf_path):
                _config = configparser.ConfigParser()
                _config.read(conf_path)
                _gui_protocol = _config.get('mirror','protocol')
            else:
                _gui_protocol = 'http:'
        else:
            _gui_protocol = self._active_protocol

        self._r1_button = QRadioButton('http')
        self._r2_button = QRadioButton('ftp')
        self._r3_button = QRadioButton('rsync')
        self._r4_button = QRadioButton('file')
        self._r5_button = QRadioButton('https')

        self._rb_group = QButtonGroup()
        self._rb_group.addButton(self._r1_button)
        self._rb_group.addButton(self._r2_button)
        self._rb_group.addButton(self._r3_button)
        self._rb_group.addButton(self._r4_button)
        self._rb_group.addButton(self._r5_button)

        if _gui_protocol == 'http:':
            self._r1_button.setChecked(True)
        if _gui_protocol == 'ftp:':
            self._r2_button.setChecked(True)
        if _gui_protocol == 'rsync:':
            self._r3_button.setChecked(True)
        if _gui_protocol == 'file:':
            self._r4_button.setChecked(True)

        _n4_labele = QLabel(gettext("Options:"))

        self._checkbox = QCheckBox(gettext("disable ") + source_path)
        _config = configparser.ConfigParser()
        _config.read(conf_path)
        try:
            if _config.get('options','checkbox') == '1':
                self._checkbox.setChecked(True)
            else:
                self._checkbox.setChecked(False)
        except:
            self._checkbox.setChecked(True)
            pass
        self._checkbox.stateChanged.connect(self._check_enabled)

        self._checkbox2 = QCheckBox(gettext("disable system *.list and enable ") + source_path)
        self._checkbox2.setChecked(False)
        self._checkbox2.stateChanged.connect(self._check_disabled)

        self._checkbox3 = QCheckBox(gettext("convert http -> https if https not found"))
        if _gui_protocol == 'https:':
            self._r5_button.setChecked(True)
            self._checkbox3.setEnabled(True)
            self._checkbox3.setChecked(True)
        else:
            self._checkbox3.setEnabled(False)
            self._checkbox3.setChecked(False)

        self._checkbox4 = QCheckBox(gettext("set the date of the archive 'Sisyphus'"))
        self._date = QDateEdit(QDate.currentDate())
        self._date.setVisible(False)

        __branch = os.popen('rpm --eval %_priority_distbranch').read().strip()
        if __branch != 'sisyphus':
            self._checkbox4.setEnabled(False)
            self._checkbox4.setChecked(False)
        else:
            self._checkbox4.setEnabled(True)
            _config = configparser.ConfigParser()
            _config.read(conf_path)
            try:
                if _config.get('options','archive') == '1':
                    self._checkbox4.setChecked(True)
                    self._r1_button.setEnabled(False)
                    self._r2_button.setEnabled(False)
                    self._r3_button.setEnabled(False)
                    self._r4_button.setEnabled(False)
                    self._r5_button.setEnabled(False)
                    self._checkbox.setEnabled(False)
                    self._checkbox2.setEnabled(False)
                    self._checkbox3.setEnabled(False)
                    self._combobox.setEnabled(False)
                    self._date.setVisible(True)
                    self._button.setText(gettext("set the date of the archive 'Sisyphus'"))
            except:
                pass

        self._checkbox4.stateChanged.connect(self._archive_sisyphus)
      
        self._rb_group.buttonClicked.connect(self._change_rb)

        _n3_labele = QLabel(gettext("Mirrors list:"))

        _layout = QVBoxLayout()
        _layout2 = QHBoxLayout()
        _layout3 = QHBoxLayout()
        _layout.addWidget(_n_labele)
        _layout.addWidget(self._lable)
        _layout.addWidget(_n2_labele)
        _layout2.addWidget(self._r1_button)
        _layout2.addWidget(self._r5_button)
        _layout2.addWidget(self._r2_button)
        _layout2.addWidget(self._r3_button)
        _layout2.addWidget(self._r4_button)
        _layout.addLayout(_layout2)
        _layout.addWidget(_n4_labele)
        _layout.addWidget(self._checkbox)
        _layout.addWidget(self._checkbox2)
        _layout.addWidget(self._checkbox3)
        _layout3.addWidget(self._checkbox4)
        _layout3.addWidget(self._date)
        _layout.addLayout(_layout3)
        _layout.addWidget(_n3_labele)
        _layout.addWidget(self._combobox)
        _layout.addWidget(self._button)

        _container = QWidget()
        _container.setLayout(_layout)
        
        self.setCentralWidget(_container)

    def set_mirror(self):

        #переключение Сизиф на дату, если включено
        if self._checkbox4.isChecked():
            if self._date.date() > QDate.currentDate():
                self._msg.setText(gettext("The specified date is greater than the current date!"))
                self._msg.exec()
                return
            else:
                if self._active != '':
                    disable_active(self._active_f)
                disable_source()
                del_ams_path()
                self._ok_date = str(self._date.date().toPython()).replace("-","/")
                with open(ams_path, 'w') as _arch_f:
                    _arch_f.write('# Sisyphus archive: ' + self._ok_date + "\n\n")
                    _arch_f.write(archive_link+self._ok_date+archive_end[0] + "\n")
                    _arch_f.write(archive_link+self._ok_date+archive_end[1] + "\n")
                    _arch_f.write(archive_link+self._ok_date+archive_end[2] + "\n")
                self._active_protocol = "http:"
                self._active = '# Sisyphus archive: ' + self._ok_date
                self._active_f = ams_path
                self._lable.setText('<b>' + '# Sisyphus archive: ' + self._ok_date + '<b>')
                _config = configparser.ConfigParser()
                _config.add_section('mirror')
                _config.set('mirror', 'activ', '# Sisyphus archive: ' + self._ok_date)
                _config.set('mirror', 'file', self._active_f)
                _config.set('mirror', 'protocol', self._active_protocol)
                _config.add_section('options')
                if self._checkbox.isChecked():
                    _config.set('options', 'checkbox', '1')
                else:
                    _config.set('options', 'checkbox', '0')
                if self._checkbox4.isChecked():
                    _config.set('options', 'archive', '1')
                    _config.set('options', 'arch_date', self._ok_date)
                else:
                    _config.set('options', 'archive', '0')
                    _config.set('options', 'arch_date', '')
                with open(conf_path, 'w') as configfile:
                    _config.write(configfile)
                self._msg.setText(gettext("Done!"))
                self._msg.exec()
                return
        #-----------------------------------------

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
        
        if self._r5_button.isChecked():
            _protocol = 'https:'
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
            if os.path.exists(conf_path):
                os.remove(conf_path)
            del_ams_path()
            self._msg.setText(gettext("Done!"))
            self._msg.exec()
        elif (self._active.strip() == self._combobox.currentText().strip()) and (self._active_protocol == _protocol):
            self._msg.setText(gettext("This mirror and procol has already been selected!"))
            self._msg.exec()
        else:
            #ищем новое зеркало, если верхний блок пропущен
            _new_list = ''

            for _t in self._list:        
                with open(_t,'r') as _f:
                    for _s in _f:
                        if self._combobox.currentText() == _s.strip().replace("#", "", 1):
                            print(gettext("find: ") + _t)
                            _new_list = _t
                            break
            
            # -- в этом месте все проверки до переключения 
            if not check_arch(_new_list):
                self._msg.setText(gettext("This mirror does not contain the required architecture."))
                self._msg.exec()
                return

            #---------------------------------------------
            # проверяем включена ли конвертация http -> https и если да, то работаем по ней и выходим
            if (self._checkbox3.isEnabled() and self._checkbox3.isChecked()):
                __flag = check_protocol(_new_list,"http:",0)          
                if __flag != 1:
                    self._msg.setText(gettext("No required protocol! Stopped."))
                    self._msg.exec()
                    return
                if ((self._active != '') and (self._active != ams_path)):
                    disable_active(self._active_f)
                    print(gettext("disabled: ") + self._active_f)
                #переносим в https
                _tmp_f = ams_path
                _del_temp_list = 0
                if _new_list == ams_path:
                    os.rename(_new_list,_new_list+'.tmp')
                    _new_list=_new_list+'.tmp'
                    _del_temp_list = 1
                else:
                    del_ams_path()
                with open(_new_list, 'r') as _old_f, open(_tmp_f, 'w') as _new_f:
                    for _s in _old_f:
                        if "http:" in _s:
                            _new_f.write((_s.strip().replace("#", "", 1)).replace("http:","https:")+'\n')
                if _del_temp_list == 1:
                    os.remove(_new_list)
                self._active_protocol = "https:"
                self._active = self._combobox.currentText()
                self._active_f = ams_path
                self._lable.setText('<b>' + self._combobox.currentText() + '<b>')
                _config = configparser.ConfigParser()
                _config.add_section('mirror')
                _config.set('mirror', 'activ', self._combobox.currentText())
                _config.set('mirror', 'file', self._active_f)
                _config.set('mirror', 'protocol', self._active_protocol)
                _config.add_section('options')
                if self._checkbox.isChecked():
                    _config.set('options', 'checkbox', '1')
                else:
                    _config.set('options', 'checkbox', '0')
                if self._checkbox4.isChecked():
                    _config.set('options', 'archive', '1')
                    _config.set('options', 'arch_date', self._ok_date)
                else:
                    _config.set('options', 'archive', '0')
                    _config.set('options', 'arch_date', '')
                with open(conf_path, 'w') as configfile:
                    _config.write(configfile)
                if self._checkbox.isChecked():
                    disable_source()
                    print(gettext("disabled: ") + source_path)
                self._msg.setText(gettext("Done!"))
                self._msg.exec()
                return
            #---------------------------------------------

            # проверка на наличие протокола
            __flag = check_protocol(_new_list,_protocol,0)          
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

            #заполнение конфигфайла, нужно для того, что бы отловить активное зеркало
            #если допустим использовалось дополнительное, не системное, зеркало, так
            #как оно сбрасывается после обновления пакета
            _config = configparser.ConfigParser()
            _config.add_section('mirror')
            _config.set('mirror', 'activ', self._combobox.currentText())
            _config.set('mirror', 'file', self._active_f)
            _config.set('mirror', 'protocol', self._active_protocol)
            _config.add_section('options')
            if self._checkbox.isChecked():
                _config.set('options', 'checkbox', '1')
            else:
                _config.set('options', 'checkbox', '0')
            if self._checkbox4.isChecked():
                _config.set('options', 'archive', '1')
                _config.set('options', 'arch_date', self._ok_date)
            else:
                _config.set('options', 'archive', '0')
                _config.set('options', 'arch_date', '')
            with open(conf_path, 'w') as configfile:
                _config.write(configfile)
            
            # ремарим /etc/apt/sources.list
            if self._checkbox.isChecked():
                disable_source()
                print(gettext("disabled: ") + source_path)

            del_ams_path()
            self._msg.setText(gettext("Done!"))
            self._msg.exec()

app = QApplication([])
alt_mirror_switcher = Window()
alt_mirror_switcher.show()
app.exec()