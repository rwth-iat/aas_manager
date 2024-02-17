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
from collections import namedtuple
from enum import Enum
from typing import Type, TypeVar

import dateutil
import pytz
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator, QDoubleValidator

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDateTimeEdit, QCheckBox, QCompleter, \
    QDateEdit, QHBoxLayout, QPlainTextEdit, QPushButton, QFileDialog, QLineEdit, QToolButton
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
    def __init__(self, parent=None, useValidators=True):
        super(DurationEdit, self).__init__(parent)
        self.useValidators = useValidators
        self._initLayout()
        self.initLineEdits()

    def _initLayout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self)
        self.setLayout(layout)

    def initLineEdits(self):
        self.yearsEdit = QLineEdit(self)
        self.monthsEdit = QLineEdit(self)
        self.daysEdit = QLineEdit(self)
        self.hoursEdit = QLineEdit(self)
        self.minutesEdit = QLineEdit(self)
        self.secondsEdit = QLineEdit(self)
        self.microsecondsEdit = QLineEdit(self)

        self.yearsEdit.setPlaceholderText("years")
        self.monthsEdit.setPlaceholderText("months")
        self.daysEdit.setPlaceholderText("days")
        self.hoursEdit.setPlaceholderText("hours")
        self.minutesEdit.setPlaceholderText("minutes")
        self.secondsEdit.setPlaceholderText("s")
        self.microsecondsEdit.setPlaceholderText("μs")

        self.lineEdits = (self.yearsEdit, self.monthsEdit, self.daysEdit,
                          self.hoursEdit, self.minutesEdit, self.secondsEdit, self.microsecondsEdit)
        for lineEdit in self.lineEdits:
            self.layout().addWidget(lineEdit)
            if self.useValidators:
                lineEdit.setValidator(QIntValidator())

    def duration(self) -> dateutil.relativedelta.relativedelta:
        return self.getObj2add()

    def setVal(self, val: dateutil.relativedelta.relativedelta):
        if isoftype(val, PreObject):
            if val.existingObjUsed:
                val = val.existingObj
            else:
                Duration_kwargs = namedtuple("Duration_kwargs", "years months days hours minutes seconds microseconds")
                val = Duration_kwargs(**val.kwargs)
        if isinstance(val, (dateutil.relativedelta.relativedelta, Duration_kwargs)):
            self.yearsEdit.setText(val.years)
            self.monthsEdit.setText(val.months)
            self.daysEdit.setText(val.days)
            self.hoursEdit.setText(val.hours)
            self.minutesEdit.setText(val.minutes)
            self.secondsEdit.setText(val.seconds)
            self.microsecondsEdit.setText(val.microseconds)
        else:
            raise TypeError("arg1 must be instance of type dateutil.relativedelta.relativedelta:", type(val))

    def setDuration(self, val: dateutil.relativedelta.relativedelta):
        self.setVal(val)

    def getPreObj(self):
        kwargs = {
            "years": PreObject(int, (self.yearsEdit.text(),), {}) if self.yearsEdit.text() else 0,
            "months": PreObject(int, (self.monthsEdit.text(),), {}) if self.monthsEdit.text() else 0,
            "days": PreObject(int, (self.daysEdit.text(),), {}) if self.daysEdit.text() else 0,
            "hours": PreObject(int, (self.hoursEdit.text(),), {}) if self.hoursEdit.text() else 0,
            "minutes": PreObject(int, (self.minutesEdit.text(),), {}) if self.minutesEdit.text() else 0,
            "seconds": PreObject(int, (self.secondsEdit.text(),), {}) if self.secondsEdit.text() else 0,
            "microseconds": PreObject(int, (self.microsecondsEdit.text(),), {}) if self.microsecondsEdit.text() else 0,
        }
        return PreObject(dateutil.relativedelta.relativedelta, tuple(), kwargs)

    def getObj2add(self):
        return self.getPreObj().init()


class DateEdit(QDateEdit):
    def __init__(self, parent=None):
        super(DateEdit, self).__init__(parent)
        self.initQDateEdit()

    def initQDateEdit(self):
        self.setKeyboardTracking(False)
        self.setDisplayFormat("dd.MM.yyyy")

    def date(self) -> Date:
        date = super().date().toPyDate()
        dateDate = Date(year=date.year, month=date.month, day=date.day)
        return dateDate

    def setDate(self, val: datetime.date):
        assert isinstance(val, datetime.date), "val must be instance of type datetime.date"
        super().setDate(val)


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
    closeClicked = pyqtSignal()

    types = (bool, str, int, float, decimal.Decimal, Enum, Type)

    def __init__(self, attrType, parent=None, objVal=None, optional=False, useValidators=True, **kwargs):
        super(StandardInputWidget, self).__init__(parent)
        self.objType = attrType
        self.optional = optional
        self.useValidators = useValidators
        self.widget = self._initWidget(**kwargs)
        self.setVal(objVal)
        self.setupLayout()

    def setupLayout(self):
        widgetLayout = QHBoxLayout(self)
        widgetLayout.setContentsMargins(1, 1, 1, 1)
        widgetLayout.addWidget(self.widget)
        self.setLayout(widgetLayout)

    def setClosable(self, closable=True):
        if closable:
            # Add close btn next to widget
            self.closeBtn = CloseButton(self)
            self.closeBtn.clicked.connect(lambda x: self.closeClicked.emit())
            self.layout().insertWidget(0, self.closeBtn)

    def _initWidget(self, **kwargs):
        if issubtype(self.objType, bool):
            widget = QCheckBox(self)
        elif issubtype(self.objType, str):
            widget = widgets.LineEdit(self)
            if kwargs.get("completions"):
                completer = QCompleter(kwargs["completions"], self)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                widget.setCompleter(completer)
        elif issubtype(self.objType, int):
            widget = widgets.LineEdit(self)
            if self.useValidators:
                widget.setValidator(QIntValidator())
        elif issubtype(self.objType, (float, decimal.Decimal)):
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
            widget.model().sort(0, Qt.SortOrder.AscendingOrder)

            if widget.count():
                widget.setCurrentIndex(0)

        return widget

    def getPreObj(self):
        if issubtype(self.objType, bool):
            return PreObject(self.objType, (self.widget.isChecked(),), {})
        elif issubtype(self.objType, (str, int, float, decimal.Decimal)):
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
        elif issubtype(self.objType, decimal.Decimal) and isoftype(val, (decimal.Decimal, int, float)):
            self.widget.setText(str(float(val)))
        elif issubtype(self.objType, (Enum, Type)):
            index = self.widget.findData(val)
            if index >= 0:
                self.widget.setCurrentIndex(index)


class SpecialInputWidget(StandardInputWidget):
    types = (dateutil.relativedelta.relativedelta,
             datetime.time, datetime.date, datetime.datetime, datetime.tzinfo,
             bytes, bytearray)

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
            widget = DurationEdit(self, useValidators=self.useValidators)
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
            return PreObject.useExistingObject(self.widget.dateTime())
        elif issubtype(self.objType, datetime.date):
            return PreObject.useExistingObject(self.widget.date())
        elif issubtype(self.objType, datetime.time):
            return PreObject.useExistingObject(self.widget.time())
        elif issubtype(self.objType, (dateutil.relativedelta.relativedelta, bytes, bytearray)):
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
        elif issubtype(self.objType, (dateutil.relativedelta.relativedelta, bytes, bytearray)):
            obj = self.widget.getObj2add()
            if obj is not None and issubtype(self.objType, bytearray):
                obj = bytearray(obj)
        return obj

    def setVal(self, val):
        if isoftype(val, PreObject):
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
            elif issubtype(self.objType, bytes) and isoftype(val, bytes):
                # text = val.decode("utf-8")
                self.widget.setPlainText(str(val))


class CreateOptionalParamBtn(QPushButton):
    def __init__(self, title, paramName, objTypehint, **kwargs):
        super(CreateOptionalParamBtn, self).__init__(title, **kwargs)
        self.paramName = paramName
        self.paramTypehint = objTypehint

class CloseButton(QToolButton):
    """Close button for optional params.
    A separate class is needed for the stylesheet to work properly"""
    def __init__(self, parent=None):
        super(CloseButton, self).__init__(parent)
