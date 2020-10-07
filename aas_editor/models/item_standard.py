from PyQt5.QtCore import QObject


class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None):
        super().__init__(parent)
        self.obj = obj
        self.objName = name

    @property
    def objectName(self):
        if self.objName:
            return self.objName
        elif hasattr(self.obj, "id_short") and self.obj.id_short:
            return self.obj.id_short
        else:
            return self.obj.__class__.__name__

    def row(self):
        if self.parent():
            return self.parent().children().index(self)
        else:
            return 0