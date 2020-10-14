from typing import NamedTuple

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QLineEdit, QLabel, QComboBox, QPushButton, QDialog, QDialogButtonBox, \
    QGroupBox, QCheckBox, QWidget

from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.provider import *
from aas.model.submodel import *

from aas_editor.util import getReqParams4init, issubtype, inheritors, isMeta


DictItem = NamedTuple("DictItem", key=Any, value=Any)


class AddDialog(QDialog):
    """Base abstract class for custom dialogs for adding data"""

    def __init__(self, parent=None, windowTitle=""):
        QDialog.__init__(self, parent)
        self.setWindowTitle(windowTitle)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.buttonOk.setDisabled(True)
        self.dialogLayout = QtWidgets.QVBoxLayout(self)
        self.dialogLayout.addWidget(self.buttonBox)
        self.setLayout(self.dialogLayout)

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


def getInputWidget(objType, rmDefParams=True, objName="", attrsToHide: dict = None, parent=None, objVal=None) -> QtWidgets.QWidget:
    print(objType, objType.__str__, objType.__repr__, objType.__class__)
    attrsToHide = attrsToHide if attrsToHide else {}
    if isMeta(objType):
        objTypes = inheritors(objType)
        widget = TypeOptionObjGroupBox(objTypes, "", attrsToHide=attrsToHide,
                             rmDefParams=rmDefParams, objName=objName, parent=parent)
    elif issubtype(objType, (list, tuple, set, dict)) and not issubtype(objType, DictItem):# typing.Iterable):
        widget = IterableGroupBox(objType, "", rmDefParams=rmDefParams, parent=parent, objVal=objVal)
    elif issubtype(objType, Union):
        objTypes = objType.__args__
        widget = TypeOptionObjGroupBox(objTypes, "", attrsToHide=attrsToHide,
                             rmDefParams=rmDefParams, objName=objName, parent=parent)
    elif issubtype(objType, AASReference):
        if objType.__args__:
            type_ = objType.__args__[0]
            attrsToHide["type_"] = type_
        widget = ObjGroupBox(objType, "", attrsToHide=attrsToHide,
                             rmDefParams=rmDefParams, objName=objName, parent=parent, objVal=objVal)
    elif issubtype(objType, (bool, str, int, float, Enum, Type)):
        widget = StandardInputWidget(objType, parent=parent, objVal=objVal)
    else:
        widget = ObjGroupBox(objType, "", rmDefParams=rmDefParams, attrsToHide=attrsToHide,
                             objName=objName, parent=parent, objVal=objVal)
    return widget


class AddObjDialog(AddDialog):
    def __init__(self, objType, parent=None, rmDefParams=True, objName="", objVal=None):
        objName = objName if objName else objType.__name__
        AddDialog.__init__(self, parent, f"Add {objName}")
        self.buttonOk.setEnabled(True)
        self.inputWidget = getInputWidget(objType, rmDefParams=rmDefParams, objName=objName, objVal=objVal)
        self.inputWidget.setObjectName("mainBox")
        self.inputWidget.setStyleSheet("#mainBox{border:0;}")
        self.dialogLayout.insertWidget(0, self.inputWidget)

    def getInputWidget(self):
        pass
    @checkIfAccepted
    def getObj2add(self):
        return self.inputWidget.getObj2add()


class GroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAlignment(Qt.AlignLeft)
        self.setLayout(QtWidgets.QVBoxLayout(self))


class ObjGroupBox(GroupBox):
    def __init__(self, objType, title, parent=None, attrsToHide: dict = None, rmDefParams=True,
                 objName="", objVal=None):
        super().__init__(title, parent)

        self.objType = objType
        self.attrsToHide = attrsToHide if attrsToHide else {}
        self.attrWidgetDict = {}

        reqAttrsDict = getReqParams4init(objType, rmDefParams, attrsToHide)

        if reqAttrsDict:
            for attr, attrType in reqAttrsDict.items():
                val = getattr(objVal, attr.rstrip("_"), None) # todo delete when right _ will be deleted in aas models
                widgetLayout = self._getInputWidgetLayout(attr, attrType, rmDefParams, val)
                self.layout().addLayout(widgetLayout)
        else:
            widgetLayout = self._getInputWidgetLayout(objName, objType, rmDefParams, objVal)
            self.layout().addLayout(widgetLayout)

    def _getInputWidgetLayout(self, attr:str, attrType, rmDefParams:bool, objVal:Any) -> QtWidgets.QHBoxLayout:
        print(f"Getting widget for attr: {attr} of type: {attrType}")
        layout = QtWidgets.QHBoxLayout()
        label = QLabel(f"{attr}:")
        widget = getInputWidget(attrType, rmDefParams=rmDefParams, objVal=objVal)
        self.attrWidgetDict[attr] = widget
        if isinstance(widget, QGroupBox):
            widget.setTitle(f"{attr}:")
        else:
            layout.addWidget(label)
        layout.addWidget(widget)
        return layout

    def getObj2add(self):
        attrValueDict = {}
        for attr, widget in self.attrWidgetDict.items():
            attrValueDict[attr] = widget.getObj2add()
        for attr, value in self.attrsToHide.items():
            attrValueDict[attr] = value
        obj = self.objType(**attrValueDict)
        return obj


class IterableGroupBox(GroupBox):
    def __init__(self, iterableType, title:str, parent=None, rmDefParams:bool=True, objVal: Iterable = None):
        super().__init__(title, parent)
        self.iterableType = iterableType
        self.argTypes = list(iterableType.__args__)
        plusButton = QPushButton(f"+ Element", self)
        plusButton.clicked.connect(self._addInputWidget)
        self.layout().addWidget(plusButton)
        self.inputWidgets = []
        if objVal:
            if isinstance(objVal, dict):
                objVal = [DictItem(key, value) for key, value in objVal.items()]
            for val in objVal:
                self._addInputWidget(rmDefParams, val)
        else:
            self._addInputWidget(rmDefParams)

    def _addInputWidget(self, rmDefParams, objVal=None):
        if ... in self.argTypes:
            self.argTypes.remove(...)

        if not issubtype(self.iterableType, dict):
            if len(self.argTypes) == 1:
                argType = self.argTypes[0]
            else:
                raise TypeError(f"expected 1 argument, got {len(self.argTypes)}", self.argTypes)
        else:
            if len(self.argTypes) == 2:
                DictItem._field_types["key"] = self.argTypes[0]
                DictItem._field_types["value"] = self.argTypes[1]
                argType = DictItem
            else:
                raise TypeError(f"expected 2 arguments, got {len(self.argTypes)}", self.argTypes)
        widget = getInputWidget(argType,
                                objName=f"{argType} {len(self.inputWidgets)}",
                                rmDefParams=rmDefParams, objVal=objVal)
        deleteButton = QPushButton(f"Delete", widget)
        deleteButton.clicked.connect(lambda :self._delInputWidget(deleteButton.parent()))
        widget.layout().addWidget(deleteButton)
        self.inputWidgets.append(widget)
        self.layout().insertWidget(self.layout().count()-1, widget)

    def _delInputWidget(self, widget: QWidget):
        self.layout().removeWidget(widget)
        widget.close()
        self.inputWidgets.remove(widget)

        self.adjustSize()
        self.window().adjustSize()

    def getObj2add(self):
        listObj = []
        for widget in self.inputWidgets:
            listObj.append(widget.getObj2add())
        if issubtype(self.iterableType, tuple):
            obj = tuple(listObj)
        if issubtype(self.iterableType, list):
            obj = list(listObj)
        if issubtype(self.iterableType, set):
            obj = set(listObj)
        if issubtype(self.iterableType, dict):
            obj = dict(listObj)
        return obj


class StandardInputWidget(QtWidgets.QWidget):
    def __init__(self, attrType, parent=None, objVal=None):
        super(StandardInputWidget, self).__init__(parent)
        self.attrType = attrType
        self.widget = self._initWidget(objVal)
        widgetLayout = QtWidgets.QVBoxLayout(self)
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
        elif issubtype(self.attrType, Enum):
            widget = QComboBox(self)
            items = [member for member in self.attrType]
            for typ in items:
                widget.addItem(typ.name, typ)
            if objVal:
                widget.setCurrentIndex(widget.findData(objVal))
        elif issubtype(self.attrType, Type):
            widget = QComboBox(self)
            union = self.attrType.__args__[0]
            if type(union) == TypeVar:
                baseType = union.__bound__
                types = inheritors(baseType)
            else:
                types = union.__args__
            for typ in types:
                widget.addItem(typ.__name__, typ)
            if objVal:
                widget.setCurrentIndex(widget.findData(objVal))
        return widget

    def getObj2add(self):
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


class ChooseFromDialog(AddDialog):
    def __init__(self, objList, title, parent=None):
        super(ChooseFromDialog, self).__init__(parent, title)
        self.buttonOk.setEnabled(True)

        self.objComboBox = QComboBox(self)
        for obj in objList:
            self.objComboBox.addItem(str(obj), obj)
        self.dialogLayout.insertWidget(0, self.objComboBox)

    @checkIfAccepted
    def getObj2add(self):
        obj = self.objComboBox.currentData()
        return obj


class TypeOptionObjGroupBox(GroupBox): # todo reimplement when Datatypes Data, Duration, etc. are ready
    def __init__(self, objTypes, title, parent=None, attrsToHide: dict = None, rmDefParams=False, objName="", objVal=None):
        super(TypeOptionObjGroupBox, self).__init__(title, parent)
        self.rmDefParams = rmDefParams
        self.attrsToHide = attrsToHide if attrsToHide else {}

        # init type-choose combobox
        self.typeComboBox = QComboBox(self)
        for objType in objTypes:
            self.typeComboBox.addItem(objType.__name__, objType)
        self.typeComboBox.setCurrentIndex(self.typeComboBox.findData(type(objVal)))
        self.layout().insertWidget(0, self.typeComboBox)

        currObjType = self.typeComboBox.currentData()
        self.widget = getInputWidget(currObjType, rmDefParams, attrsToHide=attrsToHide, parent=self, objVal=objVal)
        self.layout().addWidget(self.widget)

        # change input widget for new type if type in combobox changed
        self.typeComboBox.currentIndexChanged.connect(lambda i: self.replGroupBox(self.typeComboBox.itemData(i)))

    def replGroupBox(self, objType):
        newWidget = getInputWidget(objType, self.rmDefParams, attrsToHide=self.attrsToHide, parent=self)
        self.layout().replaceWidget(self.widget, newWidget)
        self.widget.close()
        newWidget.showMinimized()
        self.widget = newWidget
        self.window().adjustSize()

    def getObj2add(self):
        return self.widget.getObj2add()
