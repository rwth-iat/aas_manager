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


class AddObjDialog(AddDialog):
    def __init__(self, objType, parent=None, allParams=False, objName=""):
        objName = objName if objName else objType.__name__
        AddDialog.__init__(self, parent, f"Add {objName}")
        self.buttonOk.setEnabled(True)
        self.objGroupBox = ObjGroupBox(objType, "", parent=self, allParams=allParams, objName=objName)
        self.objGroupBox.setObjectName("mainBox")
        self.objGroupBox.setStyleSheet("#mainBox{border:0;}")
        self.objGroupBox.setFlat(True)
        self.dialogLayout.insertWidget(0, self.objGroupBox)

    def getInputWidget(self):
        pass

    @checkIfAccepted
    def getObj2add(self):
        return self.objGroupBox.getObj2add()


class ObjGroupBox(QGroupBox):
    def __init__(self, objType, title, parent=None, attrsToHide: dict = None, allParams=False, objName=""):
        super().__init__(title, parent)
        self.setAlignment(Qt.AlignLeft)

        self.objType = objType
        self.attrsToHide = attrsToHide if attrsToHide else {}
        self.attrWidgetDict = {}
        layout = QtWidgets.QVBoxLayout(self)

        if issubtype(objType, (bool, str, int, float, Enum, Type, list, tuple)):
            widgetLayout = self.getInputWidgetLayout(objName, objType)
            layout.addLayout(widgetLayout)
        else:
            rmDefaultAttrs = False if allParams else True
            reqAttrsDict = getReqParams4init(objType, rmDefaultAttrs)
            if self.attrsToHide:
                for attr in self.attrsToHide:
                    reqAttrsDict.pop(attr)

            for attr, attrType in reqAttrsDict.items():
                widgetLayout = self.getInputWidgetLayout(attr, attrType)
                layout.addLayout(widgetLayout)

        self.setLayout(layout)

    def getInputWidgetLayout(self, attr, attrType) -> QtWidgets.QHBoxLayout:
        print(f"Getting widget for attr: {attr} of type: {attrType}")
        layout = QtWidgets.QHBoxLayout()
        label = QLabel(f"{attr}:")
        widget = self.getInputWidget(attrType)
        self.attrWidgetDict[attr] = widget
        if isinstance(widget, QGroupBox):
            widget.setTitle(f"{attr}:")
        else:
            layout.addWidget(label)
        layout.addWidget(widget)
        return layout

    @staticmethod
    def getInputWidget(attrType) -> QtWidgets.QWidget:
        print(attrType, attrType.__str__, attrType.__repr__, attrType.__class__)
        if issubtype(attrType, (bool, str, int, float, Enum, Type)):
            widget = StandardInputWidget(attrType)
        elif issubtype(attrType, (list, tuple)):# typing.Iterable):
            argTypes = list(attrType.__args__)
            if ... in argTypes:
                argTypes.remove(...)
            if len(argTypes) == 1:
                argType = argTypes[0]
            else:
                raise TypeError(f"expected 1 argument, got {len(argTypes)}", argTypes)
            widget = ListGroupBox(argType, "")
        elif issubtype(attrType, AASReference):
            type_ = attrType.__args__[0]
            widget = ObjGroupBox(attrType, "", None, attrsToHide={"type_": type_})
        else:
            widget = ObjGroupBox(attrType, "", None)
        return widget

    def getObj2add(self):
        if issubtype(self.objType, (bool, str, int, float, Enum, Type, list, tuple)):
            attr, widget = self.attrWidgetDict.popitem()
            obj = widget.getObj2add()
        else:
            attrValueDict = {}
            for attr, widget in self.attrWidgetDict.items():
                attrValueDict[attr] = widget.getObj2add()
            for attr, value in self.attrsToHide.items():
                attrValueDict[attr] = value
            obj = self.objType(**attrValueDict)
        return obj


class ListGroupBox(QGroupBox):
    def __init__(self, objType, title, parent=None):
        super().__init__(title, parent)
        self.objType = objType
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

        plusButton = QPushButton(f"+ {self.objType.__name__}", self)
        plusButton.clicked.connect(self.addGroupBox)
        self.layout.addWidget(plusButton)

        self.objGroupBoxes = []
        self.addGroupBox()

    def addGroupBox(self):
        objGroupBox = ObjGroupBox(self.objType, f"{self.objType.__name__} {len(self.objGroupBoxes)}", self)
        self.objGroupBoxes.append(objGroupBox)
        self.layout.insertWidget(self.layout.count()-1, objGroupBox)

    def getObj2add(self):
        listObj = []
        for objGroupBox in self.objGroupBoxes:
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
                widget.addItem(str(typ), typ)
        elif issubtype(self.attrType, Type):
            widget = QComboBox(self)
            union = self.attrType.__args__[0]
            types = union.__args__
            for typ in types:
                widget.addItem(str(typ), typ)
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
