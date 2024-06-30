#  Copyright (C) Igor Garmaev, IAT der RWTH Aachen
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import sys
import logging

import pytest

from PyQt6 import QtWidgets
from PyQt6 import QtWebEngineWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QAbstractButton
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w",
                    format="%(asctime)s | %(levelname)s | %(message)s")

@pytest.fixture
def app(qtbot):
    app = QtWidgets.QApplication("./main.py")
    return app
        
def find_button_by_text(widget, text):
    if isinstance(widget, QToolButton) and widget.text() == text:
        return widget

    for child in widget.findChildren(QWidget):
        result = find_button_by_text(child, text)
        if result:
            return result

    return None
    
def find_menu_by_text(widget, text):
    if isinstance(widget, QMenu) and widget.title() == text:
        return widget

    for child in widget.findChildren(QWidget):
        result = find_menu_by_text(child, text)
        if result:
            return result

    return None
    
def print_widgets_text(widget, depth=0):
    if isinstance(widget, QMenu):
        print("  " * depth + widget.title())
    elif isinstance(widget, QToolButton):
        print("  " * depth + widget.text())
    else:
        print("  " * depth + widget.objectName() + " - " + widget.metaObject().className())

    for child in widget.findChildren(QWidget):
        print_widgets_text(child, depth + 1)

def click_widget(widget):
    if widget:
        QTest.mouseClick(widget, Qt.LeftButton)
        
def test_gui(qtbot):
    from aas_editor.editorApp import EditorApp as CurrentApp
    window = CurrentApp("./test.aasx")
    window.show()
    qtbot.addWidget(window)
    qtbot.waitUntil(window.isVisible)
    assert window.isVisible(), f"Window not visible"
    
    tree = window.mainTreeView
    tree.expandAll()
    model = tree.model()

    if root.isValid():
    root_data = model.data(root)
    print(f"Iterating Through {root_data}")
    for row in range(model.rowCount(root)):
        item_index = model.index(row, 0, root)
        item_data = model.data(item_index)
        print(f"Itering Items Under {item_data}")
        for subrow in range(model.rowCount(item_index)):
            subitem_index = model.index(subrow, 0, item_index)
            subitem_data = model.data(subitem_index)
            print(f"Item: {subitem_data}")



    subm = find_menu_by_text(window, "Add existing submodel")
    click_widget(subm)
    
    QTest.keyPress(window, Qt.Key_N, Qt.ControlModifier)
    QTest.keyRelease(window, Qt.Key_N, Qt.ControlModifier)
    
    current_focus_window = None
    
    for widget in QApplication.topLevelWidgets():
        #print(widget)
        if widget.isActiveWindow():
            current_focus_window = widget
            break
            
    #print(current_focus_window)
