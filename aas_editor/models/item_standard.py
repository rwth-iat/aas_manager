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
import logging
from collections import namedtuple

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, QVariant

from aas_editor.package import StoredFile
from aas_editor import settings
from aas_editor.utils.util import getAttrDoc, simplifyInfo, getLimitStr
from aas_editor.utils.util_type import checkType, getTypeName, getTypeHintName, isIterable, \
    getAttrTypeHint, getIterItemTypeHint
from PyQt6.QtCore import Qt

from aas_editor.utils.util_classes import ClassesInfo

MediaContent = namedtuple("MediaContent", ("value", "content_type"))


class StandardItem(QObject):
    def __init__(self, obj, name=None, parent=None, new=True, typehint=None):
        super().__init__(parent)
        self.new = new
        self.changed = False

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
        return f"{getTypeName(type(self))}: {self.data(Qt.ItemDataRole.DisplayRole)}"

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
        elif (hasattr(self.obj, "id_short")
              and self.obj.id_short
              and not self.obj.id_short.startswith("generated_submodel_list_hack_")):  # FIXME: Refactor after basyx fix
            return self.obj.id_short
        elif hasattr(self.obj, "name") and self.obj.name:
            return self.obj.name
        else:
            return getTypeName(self.obj.__class__)

    @property
    def typehint(self):
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
            logging.exception(e)
            self.typehintName = str(self.typehint)

    def updateIcon(self):
        if isinstance(self.obj, StoredFile):
            self.obj: StoredFile
            content_type: str = settings.MEDIA_TYPES_INFOS.get(
                type(self.obj),{settings.CONTENT_TYPE_ATTR: "N\A"})[settings.CONTENT_TYPE_ATTR]
            self.icon = QIcon(settings.MIME_TYPE_ICON_DICT.get(content_type, settings.FILE_ICON))
        else:
            try:
                self.icon = settings.getCharsIcon(settings.TYPE_SHORTS_DICT[type(self.obj)])
            except KeyError:
                for cls in settings.TYPE_SHORTS_DICT:
                    if isinstance(self.obj, cls):
                        self.icon = settings.getCharsIcon(settings.TYPE_SHORTS_DICT[cls])

    def data(self, role, column=settings.ATTRIBUTE_COLUMN, column_name=""):
        # custom roles
        if role == settings.NAME_ROLE:
            return self.objectName
        if role == settings.OBJECT_ROLE:
            return self.obj
        if role == settings.TYPE_ROLE:
            return type(self.obj)
        if role == settings.TYPE_HINT_ROLE:
            return self.typehint
        if role == settings.TYPE_CHECK_ROLE:
            return self.typecheck
        if role == settings.PARENT_OBJ_ROLE:
            return self.parentObj
        if role == settings.PACKAGE_ROLE:
            return self.package
        if role == settings.IS_LINK_ROLE:
            return self.isLink(column, column_name)
        if role == settings.IS_MEDIA_ROLE:
            return self.isMedia
        if role == settings.IS_URL_MEDIA_ROLE:
            return self.isUrlMedia
        if role == settings.MEDIA_CONTENT_ROLE:
            return self.getMediaContent()
        # qt roles
        if role == Qt.ItemDataRole.DecorationRole and column == settings.ATTRIBUTE_COLUMN:
            return self.icon
        if role == Qt.ItemDataRole.WhatsThisRole:
            return self.doc
        if role in (Qt.ItemDataRole.ToolTipRole, Qt.ItemDataRole.StatusTipRole):
            return self._getTooltipRoleData(column, column_name)
        if role == Qt.ItemDataRole.DisplayRole:
            return self._getDisplayRoleData(column, column_name)
        if role == Qt.ItemDataRole.EditRole:
            return self._getEditRoleData(column, column_name)
        return QVariant()

    def _getEditRoleData(self, column, column_name):
        if column == settings.VALUE_COLUMN:
            return self.obj
        if column_name:
            try:
                return getattr(self.obj, column_name)
            except AttributeError:
                return QVariant()

    def _getDisplayRoleData(self, column, column_name):
        data = settings.NOT_GIVEN
        if column == settings.ATTRIBUTE_COLUMN:
            data = self.objectName
        elif column == settings.VALUE_COLUMN:
            data = self.displayValue
        elif column == settings.TYPE_COLUMN:
            data = self.objTypeName
        elif column == settings.TYPE_HINT_COLUMN:
            data = self.typehintName
        elif column_name:
            try:
                obj = getattr(self.obj, column_name)
                data = simplifyInfo(obj)
            except AttributeError as e:
                pass
            except Exception as e:
                data = e

        if data != settings.NOT_GIVEN:
            return getLimitStr(data)
        else:
            return QVariant()

    def _getTooltipRoleData(self, column, column_name):
        if column == settings.ATTRIBUTE_COLUMN:
            if self.doc:
                tooltip = self.doc.replace(": ", "\n\n", 1)
            else:
                tooltip = self.objectName
        elif column == settings.VALUE_COLUMN:
            if self.typecheck:
                tooltip = self.displayValue
            else:
                tooltip = f"{self.displayValue}\n\nThe value must be of type '{self.typehintName}', not of type '{self.objTypeName}'!"
        elif column == settings.TYPE_COLUMN:
            if self.typecheck:
                tooltip = self.objTypeName
            else:
                tooltip = f"{self.objTypeName}\n\nThe value must be of type '{self.typehintName}', not of type '{self.objTypeName}'!"
        elif column == settings.TYPE_HINT_COLUMN:
            tooltip = self.typehintName
        else:
            tooltip = self._getDisplayRoleData(column, column_name)

        tooltip = getLimitStr(tooltip)
        return tooltip if tooltip else QVariant()

    def setParent(self, a0: 'QObject') -> None:
        super().setParent(a0)
        if a0 is None:
            return
        if a0.data(settings.PACKAGE_ROLE):
            try:
                self.package = a0.data(settings.PACKAGE_ROLE)
            except AttributeError:
                return

    @property
    def parentObj(self):
        try:
            return self.parent().obj
        except AttributeError:
            return None

    def isLink(self, column: int, column_name: str) -> bool:
        data = self._getEditRoleData(column, column_name)
        if self.package and isinstance(data, settings.LINK_TYPES):
            try:
                data.resolve(self.package.objStore)
                return True
            except (AttributeError, KeyError, NotImplementedError, TypeError, IndexError) as e:
                logging.exception(e)
                return False
        return False

    @property
    def isMedia(self) -> bool:
        if self.obj and isinstance(self.obj, tuple(settings.MEDIA_TYPES_INFOS.keys())):
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
        attrName = self.data(settings.NAME_ROLE)

        try:
            attrTypehint = getAttrTypeHint(type(self.parentObj), attrName, delOptional=False)
            return attrTypehint
        except KeyError:
            logging.exception("Typehint could not be gotten")

        if isIterable(self.parentObj):
            attrTypehint = ClassesInfo.addType(type(self.parentObj))
            if not attrTypehint and self.parent().data(settings.TYPE_HINT_ROLE):
                parentTypehint = self.parent().data(settings.TYPE_HINT_ROLE)
                try:
                    attrTypehint = getIterItemTypeHint(parentTypehint)
                except KeyError:
                    logging.exception("Typehint could not be gotten")
        return attrTypehint

    def getMediaContent(self):
        if type(self.obj) in settings.MEDIA_TYPES_INFOS:
            info = settings.MEDIA_TYPES_INFOS[type(self.obj)]
            content_type_attr = info[settings.CONTENT_TYPE_ATTR]
            content_value_attr = info[settings.CONTENT_VALUE_ATTR]
            content_type = str(getattr(self.obj, content_type_attr))
            content_value = getattr(self.obj, content_value_attr)

            if self.isUrlMedia or isinstance(content_value, bytes):
                return MediaContent(content_value, content_type)
            elif isinstance(content_value, str) and content_value in self.package.fileStore:
                file_content = io.BytesIO()
                self.package.fileStore.write_file(content_value, file_content)
                return MediaContent(file_content.getvalue(), content_type)
            elif not content_value:
                return MediaContent(b"Value is not given", "text/plain")
        return MediaContent(b"Media not found", "text/plain")
