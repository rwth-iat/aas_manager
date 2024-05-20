import sys
import logging
from PyQt6 import QtWidgets
from PyQt6 import QtWebEngineWidgets
from aas_editor.editorApp import EditorApp as prog


def main():
    app = QtWidgets.QApplication(sys.argv)
  
    try:
        window = prog()
        window.show()
    except exception:
        print(f"Can not open the program. Please see: {exception}")

    try:
        window.openAASFile('test.aasx')
    except exception:
        print(f"Can not open the test file. Please see: {exception}")
      
    indices = window.packTreeModel.iterItems()
    for index in indices:
        if window.packTreeModel.objByIndex(index).objName == 'submodels':
            print("Submodels here")
            # To implement
            # Add new submodel
            # Delete submodel
        
    app.exec()


if __name__ == "__main__":
    main()
