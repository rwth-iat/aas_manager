from typing import Optional

from PyQt5.QtWidgets import QToolBar, QWidget

from aas_editor.settings import TOOLBARS_HEIGHT


class ToolBar(QToolBar):
    def __init__(self, parent: Optional[QWidget] = ...):
        super(ToolBar, self).__init__(parent)
        self.setFixedHeight(TOOLBARS_HEIGHT)
