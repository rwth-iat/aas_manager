import typing

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QLineEdit, QLabel, QComboBox, QPushButton, QDialog, QDialogButtonBox, \
    QGroupBox, QCheckBox
from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.provider import *
from aas.model.submodel import *

from aas_editor.models import Package
from aas_editor.util import getReqParams4init, issubtype


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


class DescrGroupBox(QGroupBox):
    def __init__(self, title, parent=None, defaultLang=""):
        super().__init__(title, parent)
        layout = QtWidgets.QGridLayout(self)

        self.langLabel = QLabel("&Language:", self)
        self.langLineEdit = QLineEdit(defaultLang, self)
        self.langLabel.setBuddy(self.langLineEdit)
        self.langLineEdit.setFocus()

        self.descrLabel = QLabel("&Description:", self)
        self.descrLineEdit = QLineEdit(self)
        self.descrLabel.setBuddy(self.descrLineEdit)

        layout.addWidget(self.langLabel, 0, 0)
        layout.addWidget(self.langLineEdit, 0, 1)
        layout.addWidget(self.descrLabel, 0, 2)
        layout.addWidget(self.descrLineEdit, 0, 3)
        self.setLayout(layout)


class AddDescriptionDialog(AddDialog):
    def __init__(self, parent=None, defaultLang=""):
        AddDialog.__init__(self, parent, "Add description")
        self.buttonOk.setEnabled(True)

        self.descrsLayout = QtWidgets.QGridLayout(self)
        self.dialogLayout.addLayout(self.descrsLayout, 0, 0)

        self.descrGroupBoxes = []
        self.addDescrField(defaultLang)

        plusDescr = QPushButton("+description", self)
        plusDescr.clicked.connect(self.addDescrField)
        self.dialogLayout.addWidget(plusDescr, 9, 0)

    def addDescrField(self, defaultLang):
        descrGroupBox = DescrGroupBox("", self, defaultLang=defaultLang)
        self.descrGroupBoxes.append(descrGroupBox)
        self.descrsLayout.addWidget(descrGroupBox)

    @checkIfAccepted
    def getObj2add(self):
        descrUpdateDict = {}
        for descrGroupBox in self.descrGroupBoxes:
            lang = descrGroupBox.langLineEdit.text()
            descr = descrGroupBox.descrLineEdit.text()
            if lang and descr:
                descrUpdateDict[lang] = descr
        return descrUpdateDict


def getInputWidget(attrType, rmDefParams=True, objName="") -> QtWidgets.QWidget:
    print(attrType, attrType.__str__, attrType.__repr__, attrType.__class__)
    if issubtype(attrType, (bool, str, int, float, Enum, Type)):
        widget = StandardInputWidget(attrType)
    elif issubtype(attrType, (list, tuple, set)):# typing.Iterable):
        argTypes = list(attrType.__args__)
        if ... in argTypes:
            argTypes.remove(...)
        if len(argTypes) == 1:
            argType = argTypes[0]
        else:
            raise TypeError(f"expected 1 argument, got {len(argTypes)}", argTypes)
        widget = ListGroupBox(argType, "")
    elif issubtype(attrType, dict):
        argTypes = list(attrType.__args__)
        if ... in argTypes:
            argTypes.remove(...)
        if len(argTypes) == 2:
            keyType = argTypes[0]
            valueType = argTypes[1]
        else:
            raise TypeError(f"expected 2 argument, got {len(argTypes)}", argTypes)
        widget = ListGroupBox(argType, "")
    elif issubtype(attrType, AASReference):
        type_ = attrType.__args__[0]
        widget = ObjGroupBox(attrType, "", None, attrsToHide={"type_": type_},
                             rmDefParams=rmDefParams, objName=objName)
    else:
        widget = ObjGroupBox(attrType, "", None, rmDefParams=rmDefParams, objName=objName)
    return widget


class AddObjDialog(AddDialog):
    def __init__(self, objType, parent=None, rmDefParams=True, objName=""):
        objName = objName if objName else objType.__name__
        AddDialog.__init__(self, parent, f"Add {objName}")
        self.buttonOk.setEnabled(True)
        self.inputWidget = getInputWidget(objType, rmDefParams=rmDefParams, objName=objName)
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
                 objName=""):
        super().__init__(title, parent)

        self.objType = objType
        self.attrsToHide = attrsToHide if attrsToHide else {}
        self.attrWidgetDict = {}

        reqAttrsDict = getReqParams4init(objType, rmDefParams, attrsToHide)

        if reqAttrsDict:
            for attr, attrType in reqAttrsDict.items():
                widgetLayout = self.getInputWidgetLayout(attr, attrType)
                self.layout().addLayout(widgetLayout)
        else:
            widgetLayout = self.getInputWidgetLayout(objName, objType)
            self.layout().addLayout(widgetLayout)


    def getInputWidgetLayout(self, attr, attrType) -> QtWidgets.QHBoxLayout:
        print(f"Getting widget for attr: {attr} of type: {attrType}")
        layout = QtWidgets.QHBoxLayout()
        label = QLabel(f"{attr}:")
        widget = getInputWidget(attrType)
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


class ListGroupBox(GroupBox):
    def __init__(self, objType, title, parent=None):
        super().__init__(title, parent)
        self.objType = objType
        plusButton = QPushButton(f"+ {self.objType.__name__}", self)
        plusButton.clicked.connect(self.addInputWidget)
        self.layout().addWidget(plusButton)
        self.inputWidgets = []
        self.addInputWidget()

    def addInputWidget(self):
        widget = getInputWidget(self.objType,
                                objName=f"{self.objType.__name__} {len(self.inputWidgets)}")
        self.inputWidgets.append(widget)
        self.layout.insertWidget(self.layout.count()-1, widget)

    def getObj2add(self):
        listObj = []
        for objGroupBox in self.inputWidgets:
            listObj.append(objGroupBox.getObj2add())
        castedListobj = typing.cast(self.objType, listObj)
        return castedListobj


class StandardInputWidget(QtWidgets.QWidget):
    def __init__(self, attrType, parent=None):
        super(StandardInputWidget, self).__init__(parent)
        self.attrType = attrType
        self.widget = self._initWidget()
        widgetLayout = QtWidgets.QVBoxLayout(self)
        widgetLayout.addWidget(self.widget)
        self.setLayout(widgetLayout)

    def _initWidget(self):
        if issubtype(self.attrType, bool):
            widget = QCheckBox(self)
        elif issubtype(self.attrType, str):
            widget = QLineEdit(self)
        elif issubtype(self.attrType, int):
            widget = QLineEdit(self)
            widget.setValidator(QIntValidator())
        elif issubtype(self.attrType, float):
            widget = QLineEdit(self)
            widget.setValidator(QDoubleValidator())
        elif issubtype(self.attrType, Enum):
            widget = QComboBox(self)
            items = [member for member in self.attrType]
            for typ in items:
                widget.addItem(typ.name, typ)
        elif issubtype(self.attrType, Type):
            widget = QComboBox(self)
            union = self.attrType.__args__[0]
            types = union.__args__
            for typ in types:
                widget.addItem(typ.__name__, typ)
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


class TypeOptionObjGroupBox(ObjGroupBox):
    def __init__(self, objMetatype, title, parent=None, attrsToHide: dict = None, allParams=False, objName=""):
        QGroupBox.__init__(title, parent)
        self.setAlignment(Qt.AlignLeft)

        self.objType = objType
        self.attrsToHide = attrsToHide if attrsToHide else {}
        self.attrWidgetDict = {}
        layout = QtWidgets.QVBoxLayout(self)

        rmDefaultAttrs = False if allParams else True
        reqAttrsDict = getReqParams4init(objType, rmDefaultAttrs)
        if self.attrsToHide:
            for attr in self.attrsToHide:
                reqAttrsDict.pop(attr)

        if reqAttrsDict:
            for attr, attrType in reqAttrsDict.items():
                widgetLayout = self.getInputWidgetLayout(attr, attrType)
                layout.addLayout(widgetLayout)
        else:
            widgetLayout = self.getInputWidgetLayout(objName, objType)
            layout.addLayout(widgetLayout)

        self.setLayout(layout)

    def getInputWidgetLayout(self, attr, attrType) -> QtWidgets.QHBoxLayout:
        print(f"Getting widget for attr: {attr} of type: {attrType}")
        layout = QtWidgets.QHBoxLayout()
        label = QLabel(f"{attr}:")
        widget = getInputWidget(attrType)
        self.attrWidgetDict[attr] = widget
        if isinstance(widget, QGroupBox):
            widget.setTitle(f"{attr}:")
        else:
            layout.addWidget(label)
        layout.addWidget(widget)
        return layout

    # def getObj2add(self):
    #     attrValueDict = {}
    #     for attr, widget in self.attrWidgetDict.items():
    #         attrValueDict[attr] = widget.getObj2add()
    #     for attr, value in self.attrsToHide.items():
    #         attrValueDict[attr] = value
    #     obj = self.objType(**attrValueDict)
    #     return obj