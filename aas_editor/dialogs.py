from PyQt5 import QtWidgets
from aas.model import base


class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.buttonOk = QtWidgets.QPushButton('Ok', self)
        self.buttonOk.clicked.connect(self.accept)
        self.buttonOk.setDisabled(True)
        self.buttonCancel = QtWidgets.QPushButton('Cancel', self)
        self.buttonCancel.clicked.connect(self.reject)
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.addWidget(self.buttonOk, 10, 0)
        self.layout.addWidget(self.buttonCancel, 10, 1)


class AddPackageDialog(Dialog):
    def __init__(self, parent=None):
        Dialog.__init__(self, parent)
        self.setWindowTitle("Add Package")
        self.nameLabel = QtWidgets.QLabel("Package name:", self)
        self.nameLineEdit = QtWidgets.QLineEdit(self)
        self.nameLineEdit.textChanged.connect(self.validate)
        self.layout.addWidget(self.nameLabel, 0, 0)
        self.layout.addWidget(self.nameLineEdit, 0, 1)

    def validate(self, nameText):
        if nameText:
            self.buttonOk.setDisabled(False)
        else:
            self.buttonOk.setDisabled(True)


class AddAssetDialog(Dialog):
    def __init__(self, parent=None, defaultKind=base.AssetKind.INSTANCE,
                 defaultIdType=base.IdentifierType.IRI, defaultId=""):
        Dialog.__init__(self, parent)
        self.setWindowTitle("Add asset")

        self.kindLabel = QtWidgets.QLabel("Kind:", self)
        self.kindComboBox = QtWidgets.QComboBox(self)
        items = [str(member) for member in type(defaultKind)]
        self.kindComboBox.addItems(items)
        self.kindComboBox.setCurrentText(str(defaultKind))

        self.idTypeLabel = QtWidgets.QLabel("id_type:", self)
        self.idTypeComboBox = QtWidgets.QComboBox(self)
        items = [str(member) for member in type(defaultIdType)]
        self.idTypeComboBox.addItems(items)
        self.idTypeComboBox.setCurrentText(str(defaultIdType))

        self.idLabel = QtWidgets.QLabel("id:", self)
        self.idLineEdit = QtWidgets.QLineEdit(defaultId, self)
        self.idLineEdit.textChanged.connect(self.validate)

        self.layout.addWidget(self.kindLabel, 0, 0)
        self.layout.addWidget(self.kindComboBox, 0, 1)
        self.layout.addWidget(self.idTypeLabel, 1, 0)
        self.layout.addWidget(self.idTypeComboBox, 1, 1)
        self.layout.addWidget(self.idLabel, 2, 0)
        self.layout.addWidget(self.idLineEdit, 2, 1)

    def validate(self, nameText):
        if nameText:
            self.buttonOk.setDisabled(False)
        else:
            self.buttonOk.setDisabled(True)

class AddShellDialog(Dialog):
    def __init__(self, parent=None, defaultIdType=base.IdentifierType.IRI, defaultId="", assetsToChoose=None):
        Dialog.__init__(self, parent)
        self.setWindowTitle("Add shell")

        self.idTypeLabel = QtWidgets.QLabel("id_type:", self)
        self.idTypeComboBox = QtWidgets.QComboBox(self)
        items = [str(member) for member in type(defaultIdType)]
        self.idTypeComboBox.addItems(items)
        self.idTypeComboBox.setCurrentText(str(defaultIdType))

        self.idLabel = QtWidgets.QLabel("id:", self)
        self.idLineEdit = QtWidgets.QLineEdit(defaultId, self)
        self.idLineEdit.textChanged.connect(self.validate)

        self.assetLabel = QtWidgets.QLabel("Asset:", self)
        self.assetComboBox = QtWidgets.QComboBox(self)
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


class AddDescriptionDialog(Dialog):
    def __init__(self, parent=None, defaultLang=""):
        Dialog.__init__(self, parent)
        self.setWindowTitle("Add description")

        self.langLabel = QtWidgets.QLabel("language:", self)
        self.langLineEdit = QtWidgets.QLineEdit(defaultLang, self)
        self.langLineEdit.textChanged.connect(self.validate)

        self.descrLabel = QtWidgets.QLabel("description:", self)
        self.descrLineEdit = QtWidgets.QLineEdit(self)
        self.descrLineEdit.textChanged.connect(self.validate)

        self.layout.addWidget(self.langLabel, 0, 0)
        self.layout.addWidget(self.langLineEdit, 0, 1)
        self.layout.addWidget(self.descrLabel, 1, 0)
        self.layout.addWidget(self.descrLineEdit, 1, 1)

    def validate(self):
        if self.langLineEdit.text() and self.descrLineEdit.text():
            self.buttonOk.setDisabled(False)
        else:
            self.buttonOk.setDisabled(True)
