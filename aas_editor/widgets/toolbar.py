#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

from typing import List, Optional, Tuple

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QSizePolicy, QToolBar, QWidget

from aas_editor.settings.app_settings import TOOLBARS_HEIGHT, Setting

TOOLBAR_ICON_SIZE = 20  # smaller than the bar: buttons get padding, more of them fit
# Native styles put wide padding, gaps and separators between buttons
COMPACT_STYLE = """
QToolBar { spacing: 0px; padding: 0px; border: none; }
QToolBar QToolButton { padding: 2px; margin: 0px; border: none; }
QToolBar QToolButton:hover { background: rgba(128, 128, 128, 0.25); border-radius: 3px; }
QToolBar::separator { width: 1px; margin: 4px 3px; border: none;
    border-image: none; background: rgba(128, 128, 128, 0.5); }
"""


class ToolBar(QToolBar):
    def __init__(self, parent: Optional[QWidget] = ...):
        super(ToolBar, self).__init__(parent)
        self.setFixedHeight(TOOLBARS_HEIGHT)
        self.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        self.setStyleSheet(COMPACT_STYLE)
        # Keep all buttons: search and path fields beside the bar shrink instead
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # (label, action) in toolbar order; separators have label None
        self._buttons: List[Tuple[Optional[str], QAction]] = []

    def addButton(self, action: QAction, label: str) -> None:
        """Add a button the user can hide via buttonsMenu()."""
        self.addAction(action)
        self._buttons.append((label, action))

    def addSeparator(self) -> QAction:
        separator = super().addSeparator()
        self._buttons.append((None, separator))
        return separator

    def buttonsMenu(self, title: str, hiddenSetting: Setting) -> QMenu:
        """Menu to show/hide each button; hidden labels are kept in the setting."""
        hidden = set(hiddenSetting.value())
        menu = QMenu(title, self)
        for label, action in self._buttons:
            if label is None:
                continue
            self._showButton(action, label not in hidden)

            def toggle(checked: bool, label: str = label, action: QAction = action):
                if checked:
                    hidden.discard(label)
                else:
                    hidden.add(label)
                hiddenSetting.setValue(sorted(hidden))
                self._showButton(action, checked)

            menu.addAction(QAction(action.icon(), label, menu, checkable=True,
                                   checked=label not in hidden, toggled=toggle))
        return menu

    def _showButton(self, action: QAction, show: bool) -> None:
        if show == (action in self.actions()):
            return
        if not show:
            self.removeAction(action)
            return
        # Insert before the next button or separator still in the bar
        index = [a for _, a in self._buttons].index(action)
        following = [a for _, a in self._buttons[index + 1:] if a in self.actions()]
        self.insertAction(following[0] if following else None, action)

    def toggleViewAction(self):
        action = super().toggleViewAction()
        action.setText("Toolbar")
        action.setStatusTip("Show/hide toolbar")
        return action
