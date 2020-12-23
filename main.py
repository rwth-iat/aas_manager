import sys
from PyQt5.QtWebEngineWidgets import *
from PyQt5 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)

    from aas_editor.editorApp import EditorApp
    window = EditorApp()
    # window.packTreeModel.addItem(Package("aas_files/TestPackage.aasx"))
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()
