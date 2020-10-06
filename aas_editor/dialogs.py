import typing

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QLineEdit, QLabel, QComboBox, QPushButton, QDialog, QDialogButtonBox, \
    QGroupBox, QCheckBox
from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.provider import *
from aas.model.submodel import *

from aas_editor.qt_models import Package
from aas_editor.util import getReqParams4init


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


class AddPackDialog(AddDialog):
    def __init__(self, parent=None):
        AddDialog.__init__(self, parent, "Add Package")
        self.nameLabel = QLabel("&Package name:", self)
        self.nameLineEdit = QLineEdit(self)
        self.nameLabel.setBuddy(self.nameLineEdit)

        self.nameLineEdit.textChanged.connect(self.validate)
        self.nameLineEdit.setFocus()
        self.dialogLayout.addWidget(self.nameLabel, 0, 0)
        self.dialogLayout.addWidget(self.nameLineEdit, 0, 1)

    def validate(self, nameText):
        self.buttonOk.setEnabled(True) if nameText else self.buttonOk.setDisabled(True)

    @checkIfAccepted
    def getObj2add(self):
        return Package(name=self.nameLineEdit.text())


class AddAssetDialog(AddDialog):
    def __init__(self, parent=None, defaultKind=AssetKind.INSTANCE,
                 defaultIdType=IdentifierType.IRI, defaultId=""):
        AddDialog.__init__(self, parent, "Add asset")
        self.kindLabel = QLabel("&Kind:", self)
        self.kindComboBox = QComboBox(self)
        self.kindLabel.setBuddy(self.kindComboBox)
        items = [str(member) for member in type(defaultKind)]
        self.kindComboBox.addItems(items)
        self.kindComboBox.setCurrentText(str(defaultKind))

        self.idTypeLabel = QLabel("id_&type:", self)
        self.idTypeComboBox = QComboBox(self)
        self.idTypeLabel.setBuddy(self.idTypeComboBox)
        items = [str(member) for member in type(defaultIdType)]
        self.idTypeComboBox.addItems(items)
        self.idTypeComboBox.setCurrentText(str(defaultIdType))

        self.idLabel = QLabel("&id:", self)
        self.idLineEdit = QLineEdit(defaultId, self)
        self.idLabel.setBuddy(self.idLineEdit)
        self.idLineEdit.textChanged.connect(self.validate)
        self.idLineEdit.setFocus()

        self.dialogLayout.addWidget(self.kindLabel, 0, 0)
        self.dialogLayout.addWidget(self.kindComboBox, 0, 1)
        self.dialogLayout.addWidget(self.idTypeLabel, 1, 0)
        self.dialogLayout.addWidget(self.idTypeComboBox, 1, 1)
        self.dialogLayout.addWidget(self.idLabel, 2, 0)
        self.dialogLayout.addWidget(self.idLineEdit, 2, 1)

    def validate(self, nameText):
        self.buttonOk.setEnabled(True) if nameText else self.buttonOk.setDisabled(True)

    @checkIfAccepted
    def getObj2add(self):
        kind = eval(self.kindComboBox.currentText())
        ident = Identifier(self.idLineEdit.text(), eval(self.idTypeComboBox.currentText()))
        return Asset(kind, ident)


class AddShellDialog(AddDialog):
    def __init__(self, parent=None, defaultIdType=base.IdentifierType.IRI, defaultId="",
                 assetsToChoose=None):
        AddDialog.__init__(self, parent)
        self.setWindowTitle("Add shell")

        self.idTypeLabel = QLabel("id_type:", self)
        self.idTypeComboBox = QComboBox(self)
        items = [str(member) for member in type(defaultIdType)]
        self.idTypeComboBox.addItems(items)
        self.idTypeComboBox.setCurrentText(str(defaultIdType))

        self.idLabel = QLabel("id:", self)
        self.idLineEdit = QLineEdit(defaultId, self)
        self.idLineEdit.textChanged.connect(self.validate)
        self.idLineEdit.setFocus()

        self.assetLabel = QLabel("Asset:", self)
        self.assetComboBox = QComboBox(self)
        self.assetComboBox.addItems(assetsToChoose)

        self.dialogLayout.addWidget(self.idTypeLabel, 0, 0)
        self.dialogLayout.addWidget(self.idTypeComboBox, 0, 1)
        self.dialogLayout.addWidget(self.idLabel, 1, 0)
        self.dialogLayout.addWidget(self.idLineEdit, 1, 1)
        self.dialogLayout.addWidget(self.assetLabel, 2, 0)
        self.dialogLayout.addWidget(self.assetComboBox, 2, 1)

    def validate(self, nameText):
        if nameText:
            self.buttonOk.setDisabled(False)
        else:
            self.buttonOk.setDisabled(True)


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


class AddAdministrationDialog(AddDialog):
    def __init__(self, parent=None):
        AddDialog.__init__(self, parent, "Add administration")

        self.versionLabel = QLabel("&Version:", self)
        self.versionLineEdit = QLineEdit(self)
        self.versionLabel.setBuddy(self.versionLineEdit)
        self.versionLineEdit.setFocus()

        self.revisionLabel = QLabel("&Revision:", self)
        self.revisionLineEdit = QLineEdit(self)
        self.revisionLabel.setBuddy(self.revisionLineEdit)
        self.revisionLineEdit.textChanged.connect(self.validate)

        self.dialogLayout.addWidget(self.revisionLabel, 0, 0)
        self.dialogLayout.addWidget(self.revisionLineEdit, 0, 1)
        self.dialogLayout.addWidget(self.versionLabel, 1, 0)
        self.dialogLayout.addWidget(self.versionLineEdit, 1, 1)

    def validate(self, text):
        self.buttonOk.setEnabled(True) if text else self.buttonOk.setDisabled(True)

    @checkIfAccepted
    def getObj2add(self):
        version = self.versionLineEdit.text()
        revision = self.revisionLineEdit.text()
        return AdministrativeInformation(version, revision if revision else None)


class KeyGroupBox(QGroupBox):
    def __init__(self, title, parent=None, defaultType=base.KeyElements.ASSET,
                 defaultIdType=base.IdentifierType.IRI):
        super().__init__(title, parent)
        layout = QtWidgets.QGridLayout(self)

        self.typeLabel = QLabel("&Type:", self)
        self.typeComboBox = QComboBox(self)
        items = [str(member) for member in base.KeyElements]
        self.typeComboBox.addItems(items)
        self.typeComboBox.setCurrentText(str(defaultType))

        self.localLabel = QLabel("&Local:", self)
        self.localCheckBox = QCheckBox("Local:", self)
        self.localLabel.setBuddy(self.localCheckBox)

        self.valueLabel = QLabel("&Value:", self)
        self.valueLineEdit = QLineEdit(self)
        self.valueLabel.setBuddy(self.valueLineEdit)
        self.valueLineEdit.setFocus()

        self.idTypeLabel = QLabel("id_type:", self)
        self.idTypeComboBox = QComboBox(self)
        items = [str(member) for member in base.IdentifierType]
        self.idTypeComboBox.addItems(items)
        self.idTypeComboBox.setCurrentText(str(defaultIdType))

        layout.addWidget(self.typeLabel, 0, 0)
        layout.addWidget(self.typeComboBox, 0, 1)
        layout.addWidget(self.localLabel, 1, 0)
        layout.addWidget(self.localCheckBox, 1, 1)
        layout.addWidget(self.valueLabel, 2, 0)
        layout.addWidget(self.valueLineEdit, 2, 1)
        layout.addWidget(self.idTypeLabel, 3, 0)
        layout.addWidget(self.idTypeComboBox, 3, 1)
        self.setLayout(layout)


class AddAASRefDialog(AddDialog):
    def __init__(self, parent=None, defaultType=base.KeyElements.ASSET,
                 defaultIdType=base.IdentifierType.IRI):
        AddDialog.__init__(self, parent, "Add AASReference")
        self.buttonOk.setEnabled(True)

        self.keysLayout = QtWidgets.QGridLayout(self)
        self.dialogLayout.addLayout(self.keysLayout, 0, 0)

        self.keyGroupBoxes = []
        self.addKeyField(defaultType, defaultIdType)

        plusKey = QPushButton("+key", self)
        plusKey.clicked.connect(lambda: self.addKeyField(defaultType, defaultIdType))
        self.dialogLayout.addWidget(plusKey, 9, 0)

    def addKeyField(self, defaultType, defaultIdType):
        keyGroupBox = KeyGroupBox("Key", self, defaultType, defaultIdType)
        self.keyGroupBoxes.append(keyGroupBox)
        self.keysLayout.addWidget(keyGroupBox)

    @checkIfAccepted
    def getObj2add(self):
        keys = []
        for keyGroupBox in self.keyGroupBoxes:
            type = eval(keyGroupBox.typeComboBox.currentText())
            local = keyGroupBox.localCheckBox.isChecked()
            value = keyGroupBox.valueLineEdit.text()
            id_type = eval(keyGroupBox.idTypeComboBox.currentText())
            key = Key(type, local, value, id_type)
            keys.append(key)
        return AASReference(tuple(keys), Referable)


class AddObjDialog(AddDialog):
    def __init__(self, objType, parent=None):
        AddDialog.__init__(self, parent, f"Add {objType.__name__}")
        self.buttonOk.setEnabled(True)
        self.objGroupBox = ObjGroupBox(objType, "", parent=self)
        self.dialogLayout.insertWidget(0, self.objGroupBox)

    def getInputWidget(self):
        pass

    @checkIfAccepted
    def getObj2add(self):
        return self.objGroupBox.getObj2add()


class ObjGroupBox(QGroupBox):
    def __init__(self, objType, title, parent=None, attrsToHide: dict = None):
        super().__init__(title, parent)
        self.objType = objType
        self.attrsToHide = attrsToHide if attrsToHide else {}
        self.attrWidgetDict = {}
        layout = QtWidgets.QVBoxLayout(self)
        reqAttrsDict = getReqParams4init(objType)
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
        if issubclass(attrType, (bool, str, int, float, Enum)):
            widget = StandardInputWidget(attrType)
        elif issubclass(attrType, (list, tuple)):# typing.Iterable):
            argTypes = list(attrType.__args__)
            if ... in argTypes:
                argTypes.remove(...)
            if len(argTypes) == 1:
                argType = argTypes[0]
            else:
                raise TypeError(f"expected 1 argument, got {len(argTypes)}", argTypes)
            widget = ListGroupBox(argType, "")
        elif hasattr(attrType, "_gorg") and issubclass(attrType._gorg, AASReference): # todo check if gorg is ok in other versions of python
            type_ = attrType.__args__[0]
            widget = ObjGroupBox(attrType, "", None, attrsToHide={"type_":type_})
        else:
            widget = ObjGroupBox(attrType, "", None)
        return widget

    def getObj2add(self):
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
        objGroupBox = ObjGroupBox(self.objType,
                                  f"{self.objType.__name__} {len(self.objGroupBoxes)}", self)
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
        if issubclass(self.attrType, bool):
            widget = QCheckBox(self)
        elif issubclass(self.attrType, str):
            widget = QLineEdit(self)
        elif issubclass(self.attrType, int):
            widget = QLineEdit(self)
            widget.setValidator(QIntValidator())
        elif issubclass(self.attrType, float):
            widget = QLineEdit(self)
            widget.setValidator(QDoubleValidator())
        elif issubclass(self.attrType, Enum):
            widget = QComboBox(self)
            items = [str(member) for member in self.attrType]
            widget.addItems(items)
        return widget

    def getObj2add(self):
        if issubclass(self.attrType, bool):
            obj = self.widget.isChecked()
        elif issubclass(self.attrType, str):
            obj = self.widget.text()
        elif issubclass(self.attrType, int):
            obj = int(self.widget.text())
        elif issubclass(self.attrType, float):
            obj = float(self.widget.text())
        elif issubclass(self.attrType, Enum):
            obj = eval(self.widget.currentText())
        return obj
