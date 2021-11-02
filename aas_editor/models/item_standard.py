#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import io
from collections import namedtuple
from types import GeneratorType

from PyQt5.QtGui import QBrush, QIcon, QColor
from PyQt5.QtCore import QObject, QVariant

from aas_editor.package import StoredFile
from aas_editor.settings.app_settings import PACKAGE_ROLE, NAME_ROLE, OBJECT_ROLE, \
    ATTRIBUTE_COLUMN, \
    VALUE_COLUMN, IS_LINK_ROLE, TYPE_HINT_ROLE, PARENT_OBJ_ROLE, TYPE_COLUMN, \
    TYPE_HINT_COLUMN, TYPE_CHECK_ROLE, IS_MEDIA_ROLE, IS_URL_MEDIA_ROLE, MEDIA_CONTENT_ROLE, \
    TYPE_ROLE
from aas_editor.settings.aas_settings import TYPE_ICON_DICT, LINK_TYPES, MEDIA_TYPES
from aas_editor.settings.icons import FILE_ICON, MIME_TYPE_ICON_DICT
from aas_editor.utils.util import getDescription, getAttrDoc, simplifyInfo
from aas_editor.utils.util_type import checkType, getTypeName, getTypeHintName, isIterable, \
    getAttrTypeHint, getIterItemTypeHint
from PyQt5.QtCore import Qt

from aas_editor.utils.util_classes import DictItem, ClassesInfo

MediaContent = namedtuple("MediaContent", ("value", "mime_type"))


class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None, new=True, typehint=None):
        super().__init__(parent)
        self.new = new
        self.changed = False
        self.bg = QBrush(QColor(0, 0, 0, 0))

        # following attrs will be set during self.obj = obj
        self.typecheck = None
        self.doc = None
        self.icon = QIcon()

        self._obj = obj
        self.objTypeName = getTypeName(type(self.obj))
        self.updateIcon()

        self.objName = name
        self.doc = getAttrDoc(self.objName, self.parentObj)

        self.typehint = typehint if typehint else self.getTypeHint()
        self.typecheck = checkType(self.obj, self.typehint)

    def __str__(self):
        return f"{getTypeName(type(self))}: {self.data(Qt.DisplayRole)}"

    @property
    def displayValue(self):
        return simplifyInfo(self.obj, self.objectName)

    @property
    def obj(self):
        # try:
        #     obj = getattr(self.parentObj, self.objName)
        #     if not isinstance(obj, GeneratorType):
        #         return obj
        # except (TypeError, AttributeError):
        #     pass
        return self._obj

    @obj.setter
    def obj(self, obj):
        self._obj = obj
        try:
            self.typecheck = checkType(self.obj, self.typehint)
        except AttributeError:
            pass
        self.objTypeName = getTypeName(type(self.obj))
        self.updateIcon()
        self.doc = getAttrDoc(self.objName, self.parentObj)

    @property
    def objName(self) -> str:
        return self._objName

    @objName.setter
    def objName(self, value):
        self._objName = value
        self.doc = getAttrDoc(self.objName, self.parentObj)

    @property
    def objectName(self) -> str:
        if self.objName:
            return self.objName
        elif hasattr(self.obj, "id_short") and self.obj.id_short:
            return self.obj.id_short
        elif hasattr(self.obj, "name") and self.obj.name:
            return self.obj.name
        else:
            return getTypeName(self.obj.__class__)

    @property
    def typehint(self) -> str:
        return self._typehint

    @typehint.setter
    def typehint(self, value):
        self._typehint = value
        self.typecheck = checkType(self.obj, self.typehint)
        self.updateTypehintName()

    def updateTypehintName(self):
        try:
            self.typehintName = getTypeHintName(self.typehint)
        except TypeError as e:
            print(e)
            self.typehintName = str(self.typehint)

    def updateIcon(self):
        if isinstance(self.obj, StoredFile):
            try:
                self.obj: StoredFile
                mime_type: str = self.obj.mime_type
                self.icon = QIcon(MIME_TYPE_ICON_DICT[mime_type])
            except KeyError:
                mime_type = mime_type.rsplit("/")[0]
                self.icon = QIcon(MIME_TYPE_ICON_DICT.get(mime_type, FILE_ICON))
        else:
            try:
                self.icon = QIcon(TYPE_ICON_DICT[type(self.obj)])
            except KeyError:
                for cls in TYPE_ICON_DICT:
                    if isinstance(self.obj, cls):
                        self.icon = QIcon(TYPE_ICON_DICT[cls])

    def setData(self, value, role, column=ATTRIBUTE_COLUMN):
        if role == Qt.BackgroundRole and isinstance(value, QBrush):
            self.bg = value
            return True
        return False

    def data(self, role, column=ATTRIBUTE_COLUMN):
        if role == Qt.WhatsThisRole:
            return self.doc
        if role == NAME_ROLE:
            return self.objectName
        if role == OBJECT_ROLE:
            return self.obj
        if role == TYPE_ROLE:
            return type(self.obj)
        if role == TYPE_HINT_ROLE:
            return self.typehint
        if role == TYPE_CHECK_ROLE:
            return self.typecheck
        if role == PARENT_OBJ_ROLE:
            return self.parentObj
        if role == PACKAGE_ROLE:
            return self.package
        if role == IS_LINK_ROLE:
            return self.isLink
        if role == IS_MEDIA_ROLE:
            return self.isMedia
        if role == IS_URL_MEDIA_ROLE:
            return self.isUrlMedia
        if role == MEDIA_CONTENT_ROLE:
            return self.getMediaContent()
        if role == Qt.BackgroundRole:
            return self.bg
        if role == Qt.DecorationRole and column == 0:
            return self.icon
        if role == Qt.DisplayRole:
            if column == ATTRIBUTE_COLUMN:
                return self.objectName
            if column == VALUE_COLUMN:
                return self.displayValue
            if column == TYPE_COLUMN:
                return self.objTypeName
            if column == TYPE_HINT_COLUMN:
                return self.typehintName
        if role == Qt.ToolTipRole:
            toolTip = self.getToolTip(column)
            if toolTip:
                return toolTip
        if role == Qt.EditRole:
            if column == ATTRIBUTE_COLUMN:
                return self.objectName
            if column == VALUE_COLUMN:
                if isinstance(self.obj, DictItem):
                    return self.obj.value
                return self.obj
        return QVariant()

    def setParent(self, a0: 'QObject') -> None:
        super().setParent(a0)
        if a0 is None:
            return
        if a0.data(PACKAGE_ROLE):
            try:
                self.package = a0.data(PACKAGE_ROLE)
            except AttributeError:
                return

    @property
    def parentObj(self):
        try:
            return self.parent().obj
        except AttributeError:
            return None

    @property
    def isLink(self) -> bool:
        if self.package and isinstance(self.obj, LINK_TYPES):
            try:
                self.obj.resolve(self.package.objStore)
                return True
            except (AttributeError, KeyError, NotImplementedError, TypeError) as e:
                print(e)
                return False
        return False

    @property
    def isMedia(self) -> bool:
        if self.obj and isinstance(self.obj, MEDIA_TYPES):
            return True
        return False

    @property
    def isUrlMedia(self) -> bool:
        value = self.obj.value
        return isinstance(value, str) and value.startswith(("http", "www."))

    def row(self):
        if self.parent():
            return self.parent().children().index(self)
        else:
            return 0

    def getTypeHint(self):
        attrTypehint = None
        attrName = self.data(NAME_ROLE)

        try:
            attrTypehint = getAttrTypeHint(type(self.parentObj), attrName, delOptional=False)
            return attrTypehint
        except KeyError:
            print("Typehint could not be gotten")

        if isIterable(self.parentObj):
            attrTypehint = ClassesInfo.addType(type(self.parentObj))
            if not attrTypehint and self.parent().data(TYPE_HINT_ROLE):
                parentTypehint = self.parent().data(TYPE_HINT_ROLE)
                try:
                    attrTypehint = getIterItemTypeHint(parentTypehint)
                except KeyError:
                    print("Typehint could not be gotten")
        return attrTypehint

    def getMediaContent(self):
        if self.isUrlMedia or isinstance(self.obj.value, bytes):
            return MediaContent(self.obj.value, str(self.obj.mime_type))
        elif isinstance(self.obj.value, str) and self.obj.value in self.package.fileStore:
            file_content = io.BytesIO()
            self.package.fileStore.write_file(self.obj.value, file_content)
            return MediaContent(file_content.getvalue(), str(self.obj.mime_type))
        elif not self.obj.value:
            return MediaContent(b"Value is not given", "text/plain")
        else:
            return MediaContent(b"Media not found", "text/plain")

    def getToolTip(self, column):
        if column == ATTRIBUTE_COLUMN:
            if self.doc:
                return self.doc.replace(": ", "\n\n", 1)
            else:
                return self.objectName
        if column == VALUE_COLUMN:
            if self.typecheck:
                return self.displayValue
            else:
                return f"{self.displayValue}\n\nThe value must be of type '{self.typehintName}', not of type '{self.objTypeName}'!"
        if column == TYPE_COLUMN:
            if self.typecheck:
                return self.objTypeName
            else:
                return f"{self.objTypeName}\n\nThe value must be of type '{self.typehintName}', not of type '{self.objTypeName}'!"
        if column == TYPE_HINT_COLUMN:
            return self.typehintName
        return None
