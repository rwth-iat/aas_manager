#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import datetime
import decimal
from abc import abstractmethod
from enum import Enum
from typing import Type, TypeVar

import dateutil
import pytz
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QDateTimeEdit, QCheckBox, QCompleter, \
    QDateEdit, QSpinBox, QHBoxLayout, QPlainTextEdit, QPushButton, QFileDialog
from basyx.aas.model.datatypes import Date

from aas_editor.utils.util import inheritors
from aas_editor.utils.util_classes import PreObject
from aas_editor.utils.util_type import issubtype, getTypeName, isoftype
from aas_editor import widgets


class BytesEdit(QWidget):
    def __init__(self, parent=None):
        super(BytesEdit, self).__init__(parent)
        self._initLayout()

        self.plainTextEdit = QPlainTextEdit("b''", self)
        plusButton = QPushButton(f"Choose file", self,
                                 toolTip="Choose file",
                                 clicked=self.chooseFile)

        self.layout().addWidget(self.plainTextEdit)
        self.layout().addWidget(plusButton)

    def chooseFile(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open AAS file")
        if file:
            with open(file, "rb") as f:
                self.plainTextEdit.setPlainText(str(f.read()))

    def _initLayout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self)
        self.setLayout(layout)

    def getPreObj(self):
        text = self.plainTextEdit.toPlainText()
        if not text:
            return PreObject(type(None), (), {})
        elif text.startswith(("b'", 'b"')) and text.endswith(("'", '"')):
            return PreObject(eval, (text,), {})
        else:
            raise ValueError("Value must be of type: b'text'")

    def getObj2add(self):
        return self.getPreObj().init()

    def setPlainText(self, text):
        self.plainTextEdit.setPlainText(text)


class WidgetWithTZinfo(QWidget):
    @abstractmethod
    def __init__(self, parent=None):
        super(WidgetWithTZinfo, self).__init__(parent)
        self._initLayout()

    def _initLayout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self)
        self.setLayout(layout)

    def initTZinfoEdit(self):
        self.tzinfoEdit = SpecialInputWidget(datetime.tzinfo)
        self.layout().addWidget(self.tzinfoEdit)


class DurationEdit(QWidget):
    def __init__(self, parent=None):
        super(DurationEdit, self).__init__(parent)
        self._initLayout()
        self.initLineEdits()

    def _initLayout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self)
        self.setLayout(layout)

    def initLineEdits(self):
        self.yearsEdit = QSpinBox(self, value=0, maximum=10**6, minimum=-10**6, suffix=" years")
        self.monthsEdit = QSpinBox(self, value=0, maximum=10**6, minimum=-10**6, suffix=" months")
        self.daysEdit = QSpinBox(self, value=0, maximum=10**6, minimum=-10**6, suffix=" days")
        self.hoursEdit = QSpinBox(self, value=0, maximum=10**6, minimum=-10**6, suffix=" hours")
        self.minutesEdit = QSpinBox(self, value=0, maximum=10**6, minimum=-10**6, suffix=" min")
        self.secondsEdit = QSpinBox(self, value=0, maximum=10**6, minimum=-10**6, suffix=" s")
        self.microsecondsEdit = QSpinBox(self, value=0, maximum=10**6, minimum=-10**6, suffix=" μs")

        self.lineEdits = (self.yearsEdit, self.monthsEdit, self.daysEdit,
                          self.hoursEdit, self.minutesEdit, self.secondsEdit, self.microsecondsEdit)
        for lineEdit in self.lineEdits:
            lineEdit.setButtonSymbols(QSpinBox.NoButtons)
            self.layout().addWidget(lineEdit)

    def duration(self) -> dateutil.relativedelta.relativedelta:
        kwargs = {
            "years": self.yearsEdit.value(),
            "months": self.monthsEdit.value(),
            "days": self.daysEdit.value(),
            "hours": self.hoursEdit.value(),
            "minutes": self.minutesEdit.value(),
            "seconds": self.secondsEdit.value(),
            "microseconds": self.microsecondsEdit.value(),
        }
        duration = dateutil.relativedelta.relativedelta(**kwargs).days
        return duration

    def setDuration(self, val: dateutil.relativedelta.relativedelta):
        if isinstance(val, dateutil.relativedelta.relativedelta):
            self.yearsEdit.setValue(val.years)
            self.monthsEdit.setValue(val.months)
            self.daysEdit.setValue(val.days)
            self.hoursEdit.setValue(val.hours)
            self.minutesEdit.setValue(val.minutes)
            self.secondsEdit.setValue(val.seconds)
            self.microsecondsEdit.setValue(val.microseconds)
        else:
            raise TypeError("arg1 must be instance of type dateutil.relativedelta.relativedelta:",
                            type(val))


class DateEdit(WidgetWithTZinfo):
    def __init__(self, parent=None):
        super(DateEdit, self).__init__(parent)
        self.initQDateEdit()
        self.initTZinfoEdit()

    def initQDateEdit(self):
        self.dateEdit = QDateEdit(self)
        self.dateEdit.setKeyboardTracking(False)
        self.dateEdit.setDisplayFormat("dd.MM.yyyy")
        self.layout().addWidget(self.dateEdit)

    def date(self) -> Date:
        date = self.dateEdit.date().toPyDate()
        dateDate = Date(year=date.year, month=date.month, day=date.day)
        return dateDate

    def setDate(self, val: datetime.date):
        assert isinstance(val, datetime.date), "val must be instance of type datetime.date"
        self.dateEdit.setDate(val)


class DateTimeEdit(WidgetWithTZinfo):
    def __init__(self, parent=None):
        super(DateTimeEdit, self).__init__(parent)
        self.initQDateTimeEdit()
        self.initTZinfoEdit()

    def initQDateTimeEdit(self):
        self.dateTimeEdit = QDateTimeEdit(self)
        self.dateTimeEdit.setKeyboardTracking(False)
        self.dateTimeEdit.setDisplayFormat("dd.MM.yyyy hh:mm:ss.zzz")
        self.layout().addWidget(self.dateTimeEdit)

    def dateTime(self) -> datetime.datetime:
        dateTime = self.dateTimeEdit.dateTime().toPyDateTime()
        tzinfo = self.tzinfoEdit.getObj2add()
        dateTime = dateTime.replace(tzinfo=tzinfo)
        return dateTime

    def setDateTime(self, val: datetime.datetime):
        assert isinstance(val, datetime.datetime), "val must be instance of type datetime.datetime"
        self.dateTimeEdit.setDateTime(val)
        self.tzinfoEdit.setVal(val.tzinfo)


class TimeEdit(WidgetWithTZinfo):
    def __init__(self, parent=None):
        super(TimeEdit, self).__init__(parent)
        self.initQTimeEdit()
        self.initTZinfoEdit()

    def initQTimeEdit(self):
        self.timeEdit = QDateTimeEdit(self)
        self.timeEdit.setKeyboardTracking(False)
        self.timeEdit.setDisplayFormat("hh:mm:ss.zzz")
        self.layout().addWidget(self.timeEdit)

    def time(self) -> datetime.time:
        time = self.timeEdit.time().toPyTime()
        tzinfo = self.tzinfoEdit.getObj2add()
        time = time.replace(tzinfo=tzinfo)
        return time

    def setTime(self, val: datetime.time):
        assert isinstance(val, datetime.time), "val must be instance of type datetime.time"
        self.timeEdit.setTime(val)
        self.tzinfoEdit.setVal(val.tzinfo)


class StandardInputWidget(QWidget):
    types = (bool, str, int, float, Enum, Type)

    def __init__(self, attrType, parent=None, objVal=None, optional=False, useValidators=True, **kwargs):
        super(StandardInputWidget, self).__init__(parent)
        self.objType = attrType
        self.optional = optional
        self.useValidators = useValidators
        self.widget = self._initWidget(**kwargs)
        self.setVal(objVal)
        widgetLayout = QVBoxLayout(self)
        widgetLayout.setContentsMargins(1, 1, 1, 1)
        widgetLayout.addWidget(self.widget)
        self.setLayout(widgetLayout)

    def _initWidget(self, **kwargs):
        if issubtype(self.objType, bool):
            widget = QCheckBox(self)
        elif issubtype(self.objType, str):
            widget = widgets.LineEdit(self)
            if kwargs.get("completions"):
                completer = QCompleter(kwargs["completions"], self)
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                widget.setCompleter(completer)
        elif issubtype(self.objType, int):
            widget = widgets.LineEdit(self)
            if self.useValidators:
                widget.setValidator(QIntValidator())
        elif issubtype(self.objType, float):
            widget = widgets.LineEdit(self)
            if self.useValidators:
                widget.setValidator(QDoubleValidator())
        elif issubtype(self.objType, (Enum, Type)):
            if issubtype(self.objType, Enum):
                # add enum types to types
                types = [member for member in self.objType]
            else:  # Type
                union = self.objType.__args__[0]
                if type(union) == TypeVar:
                    # add Type inheritors to types
                    baseType = union.__bound__
                    types = inheritors(baseType)
                else:
                    # add Union Type attrs to types
                    types = union.__args__

            widget = widgets.ComboBox(self) if len(types) <= 6 else widgets.CompleterComboBox(self)

            for typ in types:
                widget.addItem(getTypeName(typ), typ)
            widget.model().sort(0, Qt.AscendingOrder)

            if widget.count():
                widget.setCurrentIndex(0)

        return widget

    def getPreObj(self):
        if issubtype(self.objType, bool):
            return PreObject(self.objType, (self.widget.isChecked(),), {})
        elif issubtype(self.objType, (str, int, float)):
            return PreObject(self.objType, (self.widget.text(),), {})
        elif issubtype(self.objType, Enum):
            return PreObject(self.objType, (self.widget.currentData(),), {})
        elif issubtype(self.objType, Type):
            return PreObject.useExistingObject(self.widget.currentData())

    def getObj2add(self):
        return self.getPreObj().init()

    def setVal(self, val):
        if isoftype(val, PreObject):
            if val.existingObjUsed:
                val = val.existingObj
            else:
                val = val.args[0]

        if issubtype(self.objType, bool) and isoftype(val, bool):
            self.widget.setChecked(bool(val))
        elif issubtype(self.objType, (str, int, float)) and isoftype(val, (str, int, float)):
            self.widget.setText(str(val))
        elif issubtype(self.objType, (Enum, Type)):
            index = self.widget.findData(val)
            if index >= 0:
                self.widget.setCurrentIndex(index)


class SpecialInputWidget(StandardInputWidget):
    types = (dateutil.relativedelta.relativedelta,
             datetime.time, datetime.date, datetime.datetime, datetime.tzinfo,
             decimal.Decimal, bytes, bytearray)

    def _initWidget(self, **kwargs):
        if issubtype(self.objType, datetime.tzinfo):
            timezones = pytz.all_timezones
            widget = widgets.CompleterComboBox(self)
            widget.addItem("None", None)
            for timezone in timezones:
                widget.addItem(timezone, timezone)
        elif issubtype(self.objType, datetime.datetime):
            widget = DateTimeEdit(self)
        elif issubtype(self.objType, datetime.date):
            widget = DateEdit(self)
        elif issubtype(self.objType, datetime.time):
            widget = TimeEdit(self)
        elif issubtype(self.objType, dateutil.relativedelta.relativedelta):
            widget = DurationEdit(self)
        elif issubtype(self.objType, decimal.Decimal):
            widget = widgets.LineEdit(self)
            if self.useValidators:
                widget.setValidator(QDoubleValidator())
        elif issubtype(self.objType, (bytes, bytearray)):
            widget = BytesEdit(self)
        return widget

    def getPreObj(self):
        if issubtype(self.objType, datetime.tzinfo):
            text = self.widget.currentData()
            if text is not None:
                return PreObject(pytz.timezone, (text,), {})
            else:
                return PreObject(type(None), (), {})
        elif issubtype(self.objType, datetime.datetime):
            return PreObject.useExistingObject(self.widget.datetime())
            raise NotImplementedError(f"The function for the type {self.objType} is notimplemented yet")
        elif issubtype(self.objType, datetime.date):
            return PreObject.useExistingObject(self.widget.date())
            raise NotImplementedError(f"The function for the type {self.objType} is notimplemented yet")
            obj = self.widget.date()
        elif issubtype(self.objType, datetime.time):
            return PreObject.useExistingObject(self.widget.time())
            raise NotImplementedError(f"The function for the type {self.objType} is notimplemented yet")
        elif issubtype(self.objType, dateutil.relativedelta.relativedelta):
            return PreObject.useExistingObject(self.widget.duration())
            raise NotImplementedError(f"The function for the type {self.objType} is notimplemented yet")
        elif issubtype(self.objType, decimal.Decimal):
            return PreObject(decimal.Decimal, (self.widget.text(),), {})
        elif issubtype(self.objType, bytes):
            return self.widget.getPreObj()
        elif issubtype(self.objType, bytearray):
            return self.widget.getPreObj()

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        if issubtype(self.objType, datetime.tzinfo):
            text = self.widget.currentData()
            if text is not None:
                obj = pytz.timezone(text)
            else:
                obj = None
        elif issubtype(self.objType, datetime.datetime):
            obj = self.widget.dateTime()
        elif issubtype(self.objType, datetime.date):
            obj = self.widget.date()
        elif issubtype(self.objType, datetime.time):
            obj = self.widget.time()
        elif issubtype(self.objType, dateutil.relativedelta.relativedelta):
            obj = self.widget.duration()
        elif issubtype(self.objType, decimal.Decimal):
            obj = decimal.Decimal(self.widget.text())
        elif issubtype(self.objType, bytes):
            obj = self.widget.getObj2add()
        elif issubtype(self.objType, bytearray):
            obj = self.widget.getObj2add()
            if obj is not None:
                obj = bytearray(obj)
        return obj

    def setVal(self, val):
        if not isoftype(val, PreObject):
            if issubtype(self.objType, bytes) and issubtype(val.objType, bytes):
                self.widget.setPlainText(val.args[0])
                # TODO: impement for date types
        elif val is not None:
            if issubtype(self.objType, datetime.datetime) and isoftype(val, datetime.datetime):
                self.widget.setDateTime(val)
            elif issubtype(self.objType, datetime.date) and isoftype(val, datetime.date):
                self.widget.setDate(val)
            elif issubtype(self.objType, datetime.time) and isoftype(val, datetime.time):
                self.widget.setTime(val)
            elif issubtype(self.objType, datetime.tzinfo) and isoftype(val, datetime.tzinfo):
                self.widget.setCurrentIndex(self.widget.findData(val))
            elif issubtype(self.objType, dateutil.relativedelta.relativedelta) \
                    and isoftype(val, dateutil.relativedelta.relativedelta):
                self.widget.setDuration(val)
            elif issubtype(self.objType, decimal.Decimal) and isoftype(val, (decimal.Decimal, int, float)):
                self.widget.setText(str(float(val)))
            elif issubtype(self.objType, bytes) and isoftype(val, bytes):
                text = val.decode("utf-8")
                self.widget.setPlainText(text)


class CreateOptionalParamBtn(QPushButton):
    def __init__(self, title, paramName, objTypehint, **kwargs):
        super(CreateOptionalParamBtn, self).__init__(title, **kwargs)
        self.paramName = paramName
        self.paramTypehint = objTypehint
