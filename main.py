import sys

from aas_editor.editorApp import EditorApp

from PyQt5 import QtWidgets
from PyQt5.QtCore import QFile, QTextStream

from aas.examples.data.example_aas import create_full_example
from aas.examples.data.example_aas import create_example_asset_administration_shell
from aas.examples.data.example_aas import create_example_concept_dictionary


def main():
    app = QtWidgets.QApplication(sys.argv)

    shell = create_example_asset_administration_shell(create_example_concept_dictionary())
    obj_store = create_full_example()
    for i in obj_store:
        print(i)

    window = EditorApp()
    window.importTestPack(obj_store)
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()
