from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QPaintEvent, QPixmap, QBrush, QColor, \
    QPalette
from PyQt5.QtWidgets import QLineEdit, QLabel, QComboBox, QPushButton, QDialog, QDialogButtonBox, \
    QGroupBox, QCheckBox, QWidget, QStylePainter, QStyleOptionGroupBox, QStyle

from aas.model.base import *
from aas.model.concept import *
from aas.model.provider import *
from aas.model.submodel import *

from aas_editor.models import DictItem
from aas_editor.settings import DEFAULT_ATTRS_TO_HIDE
from aas_editor.util import issubtype, inheritors, isMeta, getTypeName, isoftype, isIterableType, \
    getReqParams4init, getParams4init


class AddDialog(QDialog):
    """Base abstract class for custom dialogs for adding data"""

    def __init__(self, parent=None, title=""):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.buttonOk.setDisabled(True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2,2,2,2)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def getObj2add(self):
        pass


def checkIfAccepted(func):
    """Decorator for checking if user clicked ok"""

    def wrap(addDialog):
        if addDialog.result() == QDialog.Accepted:
            return func(addDialog)
        else:
            raise ValueError("Adding was cancelled")

    return wrap


def getInputWidget(objType, rmDefParams=True, title="", attrsToHide: dict = None,
                   parent=None, objVal=None) -> QtWidgets.QWidget:
    print(objType, objType.__str__, objType.__repr__, objType.__class__)

    if objVal and not isoftype(objVal, objType):
        raise TypeError("Given object type does not match to real object type:", objType, objVal)

    attrsToHide = attrsToHide if attrsToHide else DEFAULT_ATTRS_TO_HIDE.copy()
    if isMeta(objType) and not isIterableType(objType):
        objTypes = inheritors(objType)
        widget = TypeOptionObjGroupBox(objTypes, attrsToHide=attrsToHide,
                                       rmDefParams=rmDefParams, title=title,
                                       parent=parent, objVal=objVal)
    elif isIterableType(objType):
        widget = IterableGroupBox(objType, rmDefParams=rmDefParams, parent=parent, objVal=objVal)
    elif issubtype(objType, Union):
        objTypes = objType.__args__
        widget = TypeOptionObjGroupBox(objTypes, attrsToHide=attrsToHide, rmDefParams=rmDefParams,
                                       title=title, parent=parent)
    elif issubtype(objType, AASReference):
        try:
            if objType.__args__:
                type_ = objType.__args__[0]
                attrsToHide["type_"] = type_
        except AttributeError:
            pass
        widget = ObjGroupBox(objType, attrsToHide=attrsToHide, rmDefParams=rmDefParams,
                             title=title, parent=parent, objVal=objVal)
    elif issubtype(objType, (bool, str, int, float, Enum, Type)):
        widget = StandardInputWidget(objType, parent=parent, objVal=objVal)
    else:
        widget = ObjGroupBox(objType, rmDefParams=rmDefParams, attrsToHide=attrsToHide,
                             title=title, parent=parent, objVal=objVal)
    return widget


class AddObjDialog(AddDialog):
    def __init__(self, objType, parent=None, title="", rmDefParams=True,
                 objVal=None):
        title = title if title else f"Add {getTypeName(objType)}"
        AddDialog.__init__(self, parent, title=title)
        self.buttonOk.setEnabled(True)
        # if obj is given and rmDefParams = True, save all init params of obj in attrsToHide
        # and show user only required params to set
        if objVal and rmDefParams:
            attrsToHide = {}

            params, defaults = getParams4init(objType)
            for key in params.keys():
                try:
                    attrsToHide[key] = getattr(objVal, key.rstrip("_"))  # TODO fix if aas changes
                except AttributeError:
                    attrsToHide[key] = getattr(objVal, key)

            reqParams = getReqParams4init(objType, rmDefParams=True)
            for key in reqParams.keys():
                try:
                    attrsToHide.pop(key.rstrip("_"))  # TODO fix if aas changes
                except KeyError:
                    attrsToHide.pop(key)

            self.inputWidget = getInputWidget(objType, rmDefParams=rmDefParams,
                                              attrsToHide=attrsToHide, objVal=objVal)
        else:
            self.inputWidget = getInputWidget(objType, rmDefParams=rmDefParams, objVal=objVal)
        self.inputWidget.setObjectName("mainBox")
        self.inputWidget.setStyleSheet("#mainBox{border:0;}") #FIXME
        self.layout().insertWidget(0, self.inputWidget)

    def getInputWidget(self):
        pass

    @checkIfAccepted
    def getObj2add(self):
        return self.inputWidget.getObj2add()


@unique
class GroupBoxType(Enum):
    SIMPLE = 0
    CLOSABLE = 1
    ADDABLE = 2


class GroupBox(QGroupBox):
    """Groupbox which also can be closable groupbox"""
    def __init__(self, objType, parent=None, title="", attrsToHide: dict = None, rmDefParams=True,
                 objVal=None):
        super().__init__(parent)
        if title:
            self.setTitle(title)

        self.objType = objType
        self.attrsToHide = attrsToHide if attrsToHide else DEFAULT_ATTRS_TO_HIDE.copy()
        self.rmDefParams = rmDefParams
        self.objVal = objVal

        self.setAlignment(Qt.AlignLeft)
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        self.type = GroupBoxType.SIMPLE

    def paintEvent(self, a0: QPaintEvent) -> None:
        if not self.isCheckable():
            super(GroupBox, self).paintEvent(a0)
        else:
            paint = QStylePainter(self)
            option = QStyleOptionGroupBox()
            self.initStyleOption(option)
            #  don't remove the original check box control, as we want to keep
            #  it as a placeholder
            option.subControls &= ~QStyle.SC_GroupBoxCheckBox
            paint.drawComplexControl(QStyle.CC_GroupBox, option)

            #  re-use the style option, it contians enough info to make sure
            #  the button is correctly checked
            option.rect = self.style().subControlRect(
                QStyle.CC_GroupBox, option, QStyle.SC_GroupBoxCheckBox, self)

            option.rect.moveLeft(option.rect.left() - 1)
            option.rect.setWidth(option.rect.width() + 2)
            option.rect.moveTop(option.rect.top() - 1)
            option.rect.setHeight(option.rect.height() + 2)

            paint.save()
            px = QPixmap(option.rect.width(), option.rect.height())
            px.fill(self.palette().color(self.backgroundRole()))
            brush = QBrush(px)
            paint.fillRect(option.rect, brush)
            paint.restore()

            if self.isClosable():
                paint.drawPrimitive(QStyle.PE_IndicatorTabClose, option)
            elif self.isAddable():
                paint.drawPrimitive(QStyle.PE_IndicatorSpinPlus, option)

            self.setStyleSheet(
                "GroupBox::indicator:checked:hover,"
                "GroupBox::indicator:checked:focus,"
                "GroupBox::indicator:checked:pressed"
                "{"
                "    color: red;"
                "}")

    def setClosable(self, b: bool) -> None:
        self.type = GroupBoxType.CLOSABLE if b else GroupBoxType.SIMPLE
        self.setCheckable(b)

    def isClosable(self) -> bool:
        return self.isCheckable() and self.type is GroupBoxType.CLOSABLE

    def setAddable(self, b: bool) -> None:
        self.type = GroupBoxType.ADDABLE if b else GroupBoxType.SIMPLE
        self.setCheckable(b)

    def isAddable(self) -> bool:
        return self.isCheckable() and self.type is GroupBoxType.ADDABLE


class ObjGroupBox(GroupBox):
    def __init__(self, objType, **kwargs):
        super().__init__(objType, **kwargs)

        self.attrWidgetDict = {}

        reqAttrsDict = getReqParams4init(self.objType, self.rmDefParams, self.attrsToHide)

        if reqAttrsDict:
            for attr, attrType in reqAttrsDict.items():
                # TODO delete when right _ will be deleted in aas models
                val = getattr(self.objVal, attr.rstrip("_"), None)
                widgetLayout = self._getInputWidgetLayout(attr, attrType, val)
                self.layout().addLayout(widgetLayout)
        # else: # TODO check if it works ok
        #     widgetLayout = self._getInputWidgetLayout(objName, objType, rmDefParams, objVal)
        #     self.layout().addLayout(widgetLayout)

    def _getInputWidgetLayout(self, attr: str, attrType, val) -> QtWidgets.QHBoxLayout:
        print(f"Getting widget for attr: {attr} of type: {attrType}")
        layout = QtWidgets.QHBoxLayout()
        widget = getInputWidget(attrType, rmDefParams=self.rmDefParams, objVal=val)
        self.attrWidgetDict[attr] = widget
        if isinstance(widget, QGroupBox):
            widget.setTitle(f"{attr}:")
        else:
            label = QLabel(f"{attr}:")
            layout.addWidget(label)
        layout.addWidget(widget)
        return layout

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        attrValueDict = {}
        for attr, widget in self.attrWidgetDict.items():
            attrValueDict[attr] = widget.getObj2add()
        for attr, value in self.attrsToHide.items():
            attrValueDict[attr] = value
        try:
            obj = self.objType(**attrValueDict)
        except TypeError:
            for key in DEFAULT_ATTRS_TO_HIDE:
                try:
                    attrValueDict.pop(key)
                except KeyError:
                    continue
            obj = self.objType(**attrValueDict)
        return obj


class IterableGroupBox(GroupBox):
    def __init__(self, objType, **kwargs):
        super().__init__(objType, **kwargs)
        self.argTypes = list(self.objType.__args__)
        plusButton = QPushButton(f"+ Element", self, clicked=self._addInputWidget)
        self.layout().addWidget(plusButton)
        self.inputWidgets = []
        if self.objVal:
            if isinstance(self.objVal, dict):
                self.objVal = [DictItem(key, value) for key, value in self.objVal.items()]
            for val in self.objVal:
                self._addInputWidget(val)
        else:
            self._addInputWidget()

    def _addInputWidget(self, objVal=None):
        if ... in self.argTypes:
            self.argTypes.remove(...)

        if not issubtype(self.objType, dict):
            if len(self.argTypes) == 1:
                argType = self.argTypes[0]
            else:
                raise TypeError(f"expected 1 argument, got {len(self.argTypes)}", self.argTypes)
        else: #  if parentType = dict
            if len(self.argTypes) == 2:
                DictItem._field_types["key"] = self.argTypes[0]
                DictItem._field_types["value"] = self.argTypes[1]
                argType = DictItem
            else:
                raise TypeError(f"expected 2 arguments, got {len(self.argTypes)}", self.argTypes)

        widget = getInputWidget(argType,
                                title=f"{argType} {len(self.inputWidgets)}",
                                rmDefParams=self.rmDefParams, objVal=objVal)
        widget.setClosable(True)
        widget.toggled.connect(lambda: self._delInputWidget(widget))
        self.inputWidgets.append(widget)
        self.layout().insertWidget(self.layout().count()-1, widget)

    def _delInputWidget(self, widget: QWidget):
        self.layout().removeWidget(widget)
        widget.close()
        self.inputWidgets.remove(widget)

        self.adjustSize()
        self.window().adjustSize()

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        listObj = []
        for widget in self.inputWidgets:
            listObj.append(widget.getObj2add())
        if issubtype(self.objType, tuple):
            obj = tuple(listObj)
        elif issubtype(self.objType, list):
            obj = list(listObj)
        elif issubtype(self.objType, set):
            obj = set(listObj)
        elif issubtype(self.objType, dict):
            obj = dict(listObj)
        else:
            obj = list(listObj)
        return obj


class StandardInputWidget(QtWidgets.QWidget):
    def __init__(self, attrType, parent=None, objVal=None):
        super(StandardInputWidget, self).__init__(parent)
        self.attrType = attrType
        self.widget = self._initWidget(objVal)
        widgetLayout = QtWidgets.QVBoxLayout(self)
        widgetLayout.setContentsMargins(1,1,1,1)
        widgetLayout.addWidget(self.widget)
        self.setLayout(widgetLayout)

    def _initWidget(self, objVal):
        if issubtype(self.attrType, bool):
            widget = QCheckBox(self)
            widget.setChecked(bool(objVal))
        elif issubtype(self.attrType, str):
            widget = QLineEdit(self)
            widget.setText(objVal) if objVal else ""
        elif issubtype(self.attrType, int):
            widget = QLineEdit(self)
            widget.setValidator(QIntValidator())
            widget.setText(objVal) if objVal is not None else ""
        elif issubtype(self.attrType, float):
            widget = QLineEdit(self)
            widget.setValidator(QDoubleValidator())
            widget.setText(objVal) if objVal is not None else ""
        elif issubtype(self.attrType, (Enum, Type)):
            widget = QComboBox(self)
            if issubtype(self.attrType, Enum):
                # add enum types to types
                types = [member for member in self.attrType]
            else:  # Type
                union = self.attrType.__args__[0]
                if type(union) == TypeVar:
                    # add Type inheritors to types
                    baseType = union.__bound__
                    types = inheritors(baseType)
                else:
                    # add Union Type attrs to types
                    types = union.__args__

            for typ in types:
                widget.addItem(getTypeName(typ), typ)
            widget.model().sort(0, Qt.AscendingOrder)
            if objVal:
                widget.setCurrentIndex(widget.findData(objVal))

        return widget

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        if issubtype(self.attrType, bool):
            obj = self.widget.isChecked()
        elif issubtype(self.attrType, str):
            obj = self.widget.text()
        elif issubtype(self.attrType, int):
            obj = int(self.widget.text())
        elif issubtype(self.attrType, float):
            obj = float(self.widget.text())
        elif issubtype(self.attrType, (Enum, Type)):
            obj = self.widget.currentData()
        return obj


class TypeOptionObjGroupBox(GroupBox):
    def __init__(self, objTypes, **kwargs):
        super(TypeOptionObjGroupBox, self).__init__(objTypes, **kwargs)

        self._initTypeComboBox()
        currObjType = self.typeComboBox.currentData()

        self.widget = getInputWidget(currObjType, self.rmDefParams, attrsToHide=self.attrsToHide,
                                     parent=self, objVal=self.objVal)
        self.layout().addWidget(self.widget)

        # change input widget for new type if type in combobox changed
        self.typeComboBox.currentIndexChanged.connect(
            lambda i: self._replGroupBox(self.typeComboBox.itemData(i)))

    def _initTypeComboBox(self):
        """Init func for ComboBox where desired Type of input data will be chosen"""
        self.typeComboBox = QComboBox(self)
        for typ in self.objType:
            self.typeComboBox.addItem(getTypeName(typ), typ)
            self.typeComboBox.model().sort(0, Qt.AscendingOrder)
        if self.objVal:
            self.typeComboBox.setCurrentIndex(self.typeComboBox.findData(type(self.objVal)))
        else:
            self.typeComboBox.setCurrentIndex(0)
        self.layout().insertWidget(0, self.typeComboBox)

    def _replGroupBox(self, chosenType):
        """Changes input GroupBox due to chosenType structure"""
        newWidget = getInputWidget(chosenType, self.rmDefParams,
                                   attrsToHide=self.attrsToHide, parent=self)
        self.layout().replaceWidget(self.widget, newWidget)
        self.widget.close()
        newWidget.showMinimized()
        self.widget = newWidget
        self.window().adjustSize()

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        return self.widget.getObj2add()

# todo reimplement when Datatypes Data, Duration, etc. are ready
