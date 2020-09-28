from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit, QLabel, QComboBox, QPushButton, QVBoxLayout, QDialog, \
    QDialogButtonBox, QGroupBox, QCheckBox

from aas.model.aas import *
from aas.model.base import *
from aas.model.concept import *
from aas.model.provider import *
from aas.model.submodel import *

from aas_editor.qt_models import Package


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
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.buttonBox, 10, 0)
        self.setLayout(self.layout)

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
        self.layout.addWidget(self.nameLabel, 0, 0)
        self.layout.addWidget(self.nameLineEdit, 0, 1)

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

        self.layout.addWidget(self.kindLabel, 0, 0)
        self.layout.addWidget(self.kindComboBox, 0, 1)
        self.layout.addWidget(self.idTypeLabel, 1, 0)
        self.layout.addWidget(self.idTypeComboBox, 1, 1)
        self.layout.addWidget(self.idLabel, 2, 0)
        self.layout.addWidget(self.idLineEdit, 2, 1)

    def validate(self, nameText):
        self.buttonOk.setEnabled(True) if nameText else self.buttonOk.setDisabled(True)

    @checkIfAccepted
    def getObj2add(self):
        kind = eval(self.kindComboBox.currentText())
        ident = Identifier(self.idLineEdit.text(), eval(self.idTypeComboBox.currentText()))
        return Asset(kind, ident)


class AddShellDialog(AddDialog):
    def __init__(self, parent=None, defaultIdType=base.IdentifierType.IRI, defaultId="", assetsToChoose=None):
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

        self.layout.addWidget(self.idTypeLabel, 0, 0)
        self.layout.addWidget(self.idTypeComboBox, 0, 1)
        self.layout.addWidget(self.idLabel, 1, 0)
        self.layout.addWidget(self.idLineEdit, 1, 1)
        self.layout.addWidget(self.assetLabel, 2, 0)
        self.layout.addWidget(self.assetComboBox, 2, 1)

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
        self.layout.addLayout(self.descrsLayout,0,0)

        self.descrGroupBoxes = []
        self.addDescrField(defaultLang)

        plusDescr = QPushButton("+description", self)
        plusDescr.clicked.connect(self.addDescrField)
        self.layout.addWidget(plusDescr, 9, 0)

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

        self.layout.addWidget(self.revisionLabel, 0, 0)
        self.layout.addWidget(self.revisionLineEdit, 0, 1)
        self.layout.addWidget(self.versionLabel, 1, 0)
        self.layout.addWidget(self.versionLineEdit, 1, 1)

    def validate(self, text):
        self.buttonOk.setEnabled(True) if text else self.buttonOk.setDisabled(True)

    @checkIfAccepted
    def getObj2add(self):
        version = self.versionLineEdit.text()
        revision = self.revisionLineEdit.text()
        return AdministrativeInformation(version, revision if revision else None)


class KeyGroupBox(QGroupBox):
    def __init__(self, title, parent=None, defaultType=base.KeyElements.ASSET, defaultIdType=base.IdentifierType.IRI):
        super().__init__(title, parent)
        layout = QtWidgets.QGridLayout(self)

        self.typeLabel = QLabel("&Type:", self)
        self.typeComboBox = QComboBox(self)
        items = [str(member) for member in type(defaultType)]
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
        items = [str(member) for member in type(defaultIdType)]
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
    def __init__(self, parent=None, defaultType=base.KeyElements.ASSET, defaultIdType=base.IdentifierType.IRI):
        AddDialog.__init__(self, parent, "Add AASReference")

        self.buttonOk.setEnabled(True)

        # self.typeLabel = QLabel("&Ref. object type:", self)
        # self.typeComboBox = QComboBox(self)
        # items = [str(member) for member in type(_RT)]
        # self.typeComboBox.addItems(items)

        self.keysLayout = QtWidgets.QGridLayout(self)
        self.layout.addLayout(self.keysLayout, 0, 0)

        self.keyGroupBoxes = []
        self.addKeyField(defaultType, defaultIdType)

        plusKey = QPushButton("+key", self)
        plusKey.clicked.connect(lambda: self.addKeyField(defaultType, defaultIdType))
        self.layout.addWidget(plusKey, 9, 0)

    # def validate(self, text):
    #     self.buttonOk.setEnabled(True)

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
