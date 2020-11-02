import sys

from aas_editor.editorApp import EditorApp
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)

    window = EditorApp()
    # window.packTreeModel.addItem(Package("aas_files/TestPackage.aasx"))
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()
