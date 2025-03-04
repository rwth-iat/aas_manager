#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import copy
import traceback
import webbrowser

from PyQt6.QtGui import QGuiApplication
from basyx.aas.model.base import *

from enum import Enum, unique
from inspect import isabstract
from typing import Union, List, Dict, Optional

from PyQt6.QtCore import Qt, QRect, QSize, QTimer, pyqtSignal
from PyQt6.QtWidgets import QPushButton, QDialog, QDialogButtonBox, \
    QGroupBox, QWidget, QVBoxLayout, QMessageBox, QScrollArea, QFrame, QFormLayout

from aas_editor.editWidgets import StandardInputWidget
from aas_editor.settings import DEFAULTS, DEFAULT_COMPLETIONS, ATTRIBUTE_COLUMN, OBJECT_ROLE, \
    DEFAULT_INHERITOR, AAS_METAMODEL_VERSION
from settings import VERSION, APPLICATION_NAME, APPLICATION_INFO, COPYRIGHT_YEAR, CONTRIBUTORS, DEVELOPER_WEB, CONTACT, \
    REPORT_ERROR_LINK, APPLICATION_LINK, LICENSE
from aas_editor.utils.util import inheritors, getReqParams4init, getParamsAndTypehints4init, getDefaultVal, \
    actualizeAASParents, delAASParent
from aas_editor.utils.util_type import getTypeName, issubtype, isoftype, isSimpleIterableType, \
    isIterableType, isIterable, isOptional, removeOptional, typeHintToType
from aas_editor.utils.util_classes import ClassesInfo, PreObject
from aas_editor.additional.classes import DictItem
from aas_editor import editWidgets
from aas_editor import widgets


def isValOk4Typehint(val, typehint):
    if isoftype(val, typehint):
        return True
    elif isoftype(val, PreObject):
        if val.existingObjUsed:
            return isoftype(val.existingObj, typehint)
        else:
            return issubtype(val.objType, typehint)
    else:
        return False


class AboutDialog(QMessageBox):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setText(
            f"{APPLICATION_NAME}<br>"
            f"{APPLICATION_INFO}<br><br>"
            f"Website: <a href='{DEVELOPER_WEB}'>{DEVELOPER_WEB}</a><br>"
            f"Project Homepage: <a href='{APPLICATION_LINK}'>{APPLICATION_LINK}</a><br>"
            f"Version: {VERSION}<br>"
            f"AAS Metamodel Version: {AAS_METAMODEL_VERSION}<br>"
            f"Contributors: {CONTRIBUTORS}<br>"
            f"Contact: {CONTACT}<br>"
            f"License: {LICENSE}<br>"
            f"Copyright (C) {COPYRIGHT_YEAR}"
        )
        self.setIconPixmap(self.parentWidget().windowIcon().pixmap(QSize(64, 64)))


class ErrorMessageBox(QMessageBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setWindowTitle("Error")

        # Each Error message box will have "Report Button" for opening an url
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        reportButton = self.addButton("Report Bug", QMessageBox.ButtonRole.HelpRole)
        reportButton.clicked.disconnect()
        reportButton.clicked.connect(self.reportButtonClicked)

    def reportButtonClicked(self):
        webbrowser.open(REPORT_ERROR_LINK)

    @classmethod
    def withTraceback(cls, parent, text: str):
        err_msg = traceback.format_exc()
        box = cls(parent)
        box.setText(text)
        box.setDetailedText(err_msg)
        return box

    @classmethod
    def withDetailedText(cls, parent, text: str):
        box = cls(parent)
        if "\n\n" in text:
            text, detailedText = text.split("\n\n", 1)
            box.setDetailedText(detailedText)
        box.setText(text)
        return box


class AddDialog(QDialog):
    """Base abstract class for custom dialogs for adding data"""
    REC = QGuiApplication.primaryScreen().geometry()
    MAX_HEIGHT = int(REC.height() * 0.9)
    MIN_WIDTH = 450
    SAVED_POSITION = None

    def __init__(self, parent=None, title=""):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                          QDialogButtonBox.StandardButton.Cancel, self)
        self.buttonCancel = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
        self.buttonCancel.released.connect(self.reject)
        self.buttonOk = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        self.buttonOk.released.connect(self.accept)
        self.buttonOk.setDisabled(True)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 300, 600))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.setMinimumWidth(self.MIN_WIDTH)
        self.setMaximumHeight(self.MAX_HEIGHT)

        self.verticalLayout = QVBoxLayout(self)
        self.buttonBox.setContentsMargins(*self.verticalLayout.getContentsMargins())
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayoutScroll = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayoutScroll.setContentsMargins(0, 0, 0, 0)

        self.restorePosition()

    def adjustSize(self) -> None:
        layoutSize = self.layout().sizeHint()
        buttonsSize = self.buttonBox.sizeHint()
        result = QSize(max(layoutSize.width(), buttonsSize.width(), self.width()),
                       layoutSize.height() + 7 + buttonsSize.height())
        self.resize(result)

    def layout(self) -> 'QLayout':
        return self.verticalLayoutScroll

    def getObj2add(self):
        pass

    def closeEvent(self, event):
        self.savePosition()
        super().closeEvent(event)

    def reject(self):
        self.savePosition()
        super().reject()
        
    def accept(self):
        self.savePosition()
        super().accept()
        
    def savePosition(self):
        AddDialog.SAVED_POSITION = self.pos()
        
    def restorePosition(self):
        if AddDialog.SAVED_POSITION:
            self.move(AddDialog.SAVED_POSITION)

def checkIfAccepted(func):
    """Decorator for checking if user clicked ok"""

    def wrap(addDialog):
        if addDialog.result() == QDialog.DialogCode.Accepted:
            return func(addDialog)
        else:
            raise ValueError("Adding was cancelled")

    return wrap


class InputWidgetUtil:

    @classmethod
    def handleTypeHint(cls, objTypeHint, parent):
        return cls._handleTypeHint(objTypeHint, parent)

    @classmethod
    def _handleTypeHint(cls, objTypeHint, parent):
        objTypeHint = removeOptional(objTypeHint)
        return objTypeHint

    @classmethod
    def getInputWidget(cls, objTypeHint, rmDefParams=True, title="", paramsToHide: dict = None, parent=None,
                       objVal=None, paramsToAttrs=None, includeInheritedTyps=True, **kwargs) -> QWidget:
        optional = True if isOptional(objTypeHint) else False
        objTypeHint = cls.handleTypeHint(objTypeHint, parent)

        if objVal and not isValOk4Typehint(objVal, objTypeHint):
            print("Given object type does not match to real object type:", objTypeHint, objVal)
            objVal = None

        paramsToAttrs = paramsToAttrs if paramsToAttrs else ClassesInfo.paramsToAttrs(objTypeHint)
        paramsToHide = cls.handleParamsToHide(objTypeHint, objVal, rmDefParams, paramsToHide, paramsToAttrs)

        kwargs = {
            **kwargs,
            "rmDefParams": rmDefParams,
            "title": title,
            "paramsToHide": paramsToHide,
            "paramsToAttrs": paramsToAttrs,
            "parent": parent,
            "objVal": objVal,
            "optional": optional
        }
        widget = cls.getWidget4typehint(objTypeHint, includeInheritedTyps, **kwargs)
        return widget

    @classmethod
    def handleParamsToHide(cls, objTypeHint, objVal, rmDefParams, paramsToHide, paramsToAttrs):
        # if obj is given and rmDefParams = True, save all not mandatory init params of obj with val in paramsToHide
        # if obj is given and rmDefParams = False, save all hidden init params of obj with val in paramsToHide
        # and show user only required params to set

        paramsToHide = paramsToHide if paramsToHide else ClassesInfo.defaultParamsToHide(objTypeHint)

        params, paramsDefaults = getParamsAndTypehints4init(objTypeHint)
        reqParams = getReqParams4init(objTypeHint, rmDefParams=True)
        hiddenAttrs = ClassesInfo.hiddenAttrs(objTypeHint)

        for param in params.keys():
            attr = paramsToAttrs.get(param, param)

            if rmDefParams and objVal:
                if param in reqParams:
                    continue
                else:
                    paramsToHide[param] = getattr(objVal, attr)
            elif attr in hiddenAttrs and param not in paramsToHide:
                if objVal:
                    paramsToHide[param] = getattr(objVal, attr)
                elif param in paramsDefaults:
                    paramsToHide[param] = paramsDefaults[param]
        return paramsToHide

    @classmethod
    def getWidget4typehint(cls, objTypeHint, includeInheritedTyps, **kwargs):
        if isabstract(objTypeHint) and not isIterableType(objTypeHint):
            objTypes = inheritors(objTypeHint)
            kwargs["defType"] = DEFAULT_INHERITOR.get(objTypeHint, None)
            widget = TypeOptionObjGroupBox(objTypes, **kwargs)
        elif issubtype(objTypeHint, LangStringSet):
            widget = LangStringSetGroupBox(objTypeHint, **kwargs)
        elif isSimpleIterableType(objTypeHint):
            widget = IterableGroupBox(objTypeHint, **kwargs)
        elif issubtype(objTypeHint, Union):
            objTypes = objTypeHint.__args__
            widget = TypeOptionObjGroupBox(objTypes, **kwargs)
        elif issubtype(objTypeHint, ModelReference):
            widget = ModelReferenceGroupBox(objTypeHint, **kwargs)
        elif issubtype(objTypeHint, editWidgets.SpecialInputWidget.types):
            widget = editWidgets.SpecialInputWidget(objTypeHint, **kwargs)
        elif issubtype(objTypeHint, editWidgets.StandardInputWidget.types):
            widget = editWidgets.StandardInputWidget(objTypeHint, **kwargs)
        elif includeInheritedTyps and inheritors(objTypeHint):
            objTypes = list(inheritors(objTypeHint))
            objTypes.append(objTypeHint)
            kwargs["defType"] = DEFAULT_INHERITOR.get(objTypeHint, None)
            widget = TypeOptionObjGroupBox(objTypes, **kwargs)
        else:
            widget = ObjGroupBox(objTypeHint, **kwargs)
        return widget


class AddObjDialog(AddDialog):
    def __init__(self, objTypeHint, parent: 'TreeView', title="", rmDefParams=True, objVal=None, **kwargs):
        title = title if title else f"Add {getTypeName(objTypeHint)}"
        AddDialog.__init__(self, parent, title=title)
        self.buttonOk.setEnabled(True)

        if not isoftype(objVal, PreObject):
            objVal = copy.deepcopy(objVal)
        actualizeAASParents(objVal)

        kwargs = {
            **kwargs,
            "rmDefParams": rmDefParams,
            "objVal": objVal,
            "parent": self,
        }

        self.inputWidget = InputWidgetUtil.getInputWidget(objTypeHint, **kwargs)
        self.inputWidget.setObjectName("mainBox")
        self.inputWidget.setStyleSheet("#mainBox{border:0;}")  # FIXME
        self.layout().addWidget(self.inputWidget)
        QTimer.singleShot(0, self.adjustSize)

    def getInputWidget(self):
        pass

    @checkIfAccepted
    def getObj2add(self):
        return self.inputWidget.getObj2add()

    @checkIfAccepted
    def getPreObj(self):
        return self.inputWidget.getPreObj()


@unique
class GroupBoxType(Enum):
    SIMPLE = 0
    CLOSABLE = 1


class GroupBox(QGroupBox):
    """Groupbox which also can be closable groupbox"""
    closeClicked = pyqtSignal()

    def __init__(self, objTypeHint, parent=None, title="", paramsToHide: dict = None, rmDefParams=True,
                 objVal=None, paramsToAttrs=None, optional=False, **kwargs):
        super().__init__(parent)
        if title:
            self.setTitle(title)

        self.objTypeHint = objTypeHint
        self.paramsToHide = paramsToHide if paramsToHide else ClassesInfo.defaultParamsToHide(objTypeHint)
        self.paramsToAttrs = paramsToAttrs if paramsToAttrs else ClassesInfo.paramsToAttrs(objTypeHint)
        self.rmDefParams = rmDefParams
        self.objVal = objVal
        self.optional = optional

        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(QFormLayout(self))
        self.type = GroupBoxType.SIMPLE
        self.toggled.connect(lambda x: self.closeClicked.emit())

    def layout(self) -> QFormLayout:
        return super().layout()

    def setClosable(self, b: bool) -> None:
        self.type = GroupBoxType.CLOSABLE if b else GroupBoxType.SIMPLE
        self.setCheckable(b)

    def isClosable(self) -> bool:
        return self.isCheckable() and self.type is GroupBoxType.CLOSABLE

    def setVal(self, val):
        pass

    def adjustSize(self) -> None:
        oldSize = self.size()
        super(GroupBox, self).adjustSize()
        newSize = self.size()
        if oldSize != newSize:
            QTimer.singleShot(0, lambda: self.window().adjustSize())
        newSize = self.size()
        if newSize.width() < oldSize.width():
            self.resize(oldSize.width(), newSize.height())


class ObjGroupBox(GroupBox):
    def __init__(self, objTypeHint, parent=None, paramsToHide: dict = None, objVal=None, paramsToAttrs: dict = None,
                 **kwargs):
        super().__init__(objTypeHint, objVal=objVal, parent=parent, paramsToHide=paramsToHide,
                         paramsToAttrs=paramsToAttrs, **kwargs)

        self.inputWidgets: List[QWidget] = []
        self.paramWidgets: Dict[str, QWidget] = {}

        reqInitParamsTypehints = getReqParams4init(self.objTypeHint, self.rmDefParams, self.paramsToHide,
                                                   delOptional=False)
        self.defaultParams =  tuple(getParamsAndTypehints4init(self.objTypeHint)[1].keys())

        sortedReqInitParamsTypehints = sorted(reqInitParamsTypehints.items(),
                                              key=lambda x: int(x[0] in self.defaultParams))
        self.reqParamsDict = dict(sortedReqInitParamsTypehints)
        self.kwargs = kwargs.copy() if kwargs else {}
        self.initLayout()

    def initLayout(self):
        if self.reqParamsDict:
            for param in self.reqParamsDict:
                self.kwargs["completions"] = DEFAULT_COMPLETIONS.get(self.objTypeHint, {}).get(param, [])
                val = self.getVal4param(param)
                widget = self.getInitialInputWidget(param, val, **self.kwargs)
                self.insertInputWidget(widget, param)

    def getVal4param(self, param):
        attr = self.paramsToAttrs.get(param, param)
        if hasattr(self.objVal, attr):
            val = getattr(self.objVal, attr)
        else:
            val = DEFAULTS.get(self.objTypeHint, {}).get(param, getDefaultVal(self.objTypeHint, param, None))
        return val

    def getInitialInputWidget(self, param: str, val, **kwargs) -> QWidget:
        paramTypeHint = self.reqParamsDict[param]
        if isOptional(paramTypeHint):
            if val is None or \
                    (isinstance(val, PreObject) and
                     val.existingObjUsed and
                     val.existingObj is None):
                return self.getCreatePushBtn(param)
        return self.getInputWidget(param, val, **kwargs)

    def getInputWidget(self, param: str, val, **kwargs) -> QWidget:
        paramTypeHint = self.reqParamsDict[param]
        print(f"Getting widget for param: {param} of type: {paramTypeHint}")
        widget = InputWidgetUtil.getInputWidget(paramTypeHint, objVal=val, **kwargs)
        self.paramWidgets[param] = widget

        if widget.optional and isinstance(widget, (GroupBox, StandardInputWidget)):
            widget.setClosable(True)
            widget.closeClicked.connect(self.replaceOptionalParamWidgetWithCreateBtn)
        return widget

    def insertInputWidget(self, widget: QWidget, param: str, row: int = -1):
        title = self.getWidgetTitle(param)
        self.layout().insertRow(row, title, widget)
        self.inputWidgets.append(widget)
        self.adjustSize()

    def getWidgetTitle(self, param: str):
        title = param.strip("_")
        if param not in self.defaultParams:
            title = f"{title}*"
        return title

    def getPreObj(self):
        kwargs = {}
        for param, widget in self.paramWidgets.items():
            kwargs[param] = widget.getPreObj()
        for param, value in self.paramsToHide.items():
            value = delAASParent(value)
            kwargs[param] = value
        try:
            return PreObject(self.objTypeHint, (), kwargs)
        except TypeError:
            positional_arg_defaults = ClassesInfo.positionalArgDefaults(self.objTypeHint)
            for arg in positional_arg_defaults:
                kwargs[arg] = positional_arg_defaults[arg]
            for arg in ClassesInfo.defaultParamsToHide(object):
                try:
                    kwargs.pop(arg)
                except KeyError:
                    continue
        return PreObject(self.objTypeHint, (), kwargs)

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        return self.getPreObj().init()

    def delInputWidget(self, widget: QWidget):
        self.inputWidgets.remove(widget)
        for paramName, paramWidget in self.paramWidgets.items():
            if widget is paramWidget:
                self.paramWidgets.pop(paramName)
                break
        self.layout().removeRow(widget)
        self.adjustSize()

    def replaceOptionalParamWidgetWithCreateBtn(self):
        widget = self.sender()
        widgetRow = self.findWidgetRow(widget)

        widgets = list(self.paramWidgets.values())
        if widgetRow is not None and widget in widgets:
            params = list(self.paramWidgets.keys())
            paramName = params[widgets.index(widget)]
            btn = self.getCreatePushBtn(paramName)
            self.layout().insertRow(widgetRow, self.getWidgetTitle(paramName), btn)
            self.delInputWidget(widget)
        self.layout().update()

    def findWidgetRow(self, widget: QWidget):
        layout: QFormLayout = self.layout()
        for row in range(layout.rowCount()):
            item = layout.itemAt(row, QFormLayout.ItemRole.FieldRole)
            if widget == item.widget():
                return row
        return None

    def getCreatePushBtn(self, paramName: str):
        btn = editWidgets.CreateOptionalParamBtn("Create", paramName=paramName,
                                                 objTypehint=self.reqParamsDict[paramName],
                                                 parent=self, clicked=self.addWidget4optionalParam)
        return btn

    def addWidget4optionalParam(self):
        layout: QFormLayout = self.layout()
        for row in range(layout.rowCount()):
            try:
                item = layout.itemAt(row, QFormLayout.ItemRole.FieldRole)
                if self.sender() == item.widget():
                    createBtn: editWidgets.CreateOptionalParamBtn = item.widget()
                    kwargs = copy.copy(self.kwargs)
                    kwargs.update({"optional": True})
                    widget = self.getInputWidget(createBtn.paramName, val=None, **kwargs)
                    layout.removeRow(row)
                    self.insertInputWidget(widget, createBtn.paramName, row)
                    break
            except Exception as e:
                ErrorMessageBox.withTraceback(self, str(e)).exec()

    def setVal4param(self, param: str, val):
        paramWidget = self.paramWidgets[param]
        paramWidget.setVal(val)

    def setVal(self, val):
        if val and isValOk4Typehint(val, self.objTypeHint):
            self.objVal = val
            for widget in reversed(self.inputWidgets):
                self.delInputWidget(widget)
            self.initLayout()
        else:
            print("Value does not fit to req obj type", type(val), self.objTypeHint)


class SingleWidgetGroupBox(GroupBox):
    def __init__(self, widget: Union[editWidgets.StandardInputWidget, editWidgets.SpecialInputWidget], parent=None):
        super(SingleWidgetGroupBox, self).__init__(widget.objType, parent)
        self.inputWidget = widget
        self.layout().addWidget(widget)

    def getPreObj(self):
        return self.inputWidget.getPreObj()

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        return self.getPreObj().init()

    def setVal(self, val):
        self.inputWidget.setVal(val)


class IterableGroupBox(GroupBox):
    def __init__(self, objTypeHint, **kwargs):
        super().__init__(objTypeHint, **kwargs)
        self.argTypes = list(self.objTypeHint.__args__)
        self.kwargs = kwargs.copy() if kwargs else {}
        plusButton = QPushButton(f"Add Item", self,
                                 toolTip="Add item",
                                 clicked=self._addInputWidget)
        self.layout().addRow(plusButton)
        self.inputWidgets = []
        self.setVal(self.objVal)

    def _getItemType(self):
        if ... in self.argTypes:
            self.argTypes.remove(...)

        if not issubtype(self.objTypeHint, dict):
            if len(self.argTypes) == 1:
                argType = self.argTypes[0]
            else:
                raise TypeError(f"expected 1 argument, got {len(self.argTypes)}", self.argTypes)
        else:  # if parentType = dict
            if len(self.argTypes) == 2:
                DictItem.__new__.__annotations__["key"] = self.argTypes[0]
                DictItem.__new__.__annotations__["value"] = self.argTypes[1]
                argType = DictItem
            else:
                raise TypeError(f"expected 2 arguments, got {len(self.argTypes)}", self.argTypes)
        return argType

    def _addInputWidget(self, objVal=None):
        itemType = self._getItemType()

        self.kwargs.update({
            "title": f"{getTypeName(itemType)} {len(self.inputWidgets) + 1}",
            "rmDefParams": self.rmDefParams,
            "objVal": objVal
        })
        widget = InputWidgetUtil.getInputWidget(itemType, **self.kwargs)
        if not isinstance(widget, GroupBox):
            widget = SingleWidgetGroupBox(widget)
        widget.setClosable(True)
        widget.setFlat(True)
        widget.toggled.connect(lambda: self.delInputWidget(widget))
        self.inputWidgets.append(widget)
        self.layout().insertRow(self.layout().count()-1, widget)
        self.adjustSize()

    def delInputWidget(self, widget: QWidget):
        self.layout().removeWidget(widget)
        widget.close()
        self.inputWidgets.remove(widget)
        for i, widget in enumerate(self.inputWidgets):
            res: str = widget.title().rstrip("0123456789")
            widget.setTitle(f"{res}{i + 1}")
        self.adjustSize()
        self.window().adjustSize()

    def getPreObj(self):
        listObj = []
        for widget in self.inputWidgets:
            listObj.append(widget.getPreObj())
        typ = typeHintToType(self.objTypeHint)
        return PreObject(typ, (listObj,), {})

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        return self.getPreObj().init()

    def setVal(self, val):
        if isinstance(val, dict):
            val = [DictItem(key, value) for key, value in val.items()]
        elif isoftype(val, PreObject) and issubtype(val.objType, dict):
            val = [DictItem(item[0], item[1]) for item in val.args]  # FIXME: look how PreObjects for dicts are created
        elif isoftype(val, PreObject) and issubtype(val.objType, LangStringSet):
            val = [DictItem(item[0], item[1]) for item in val.args[0].args[0]]  # FIXME: look how PreObjects for dicts are created


        if val and \
                (isIterable(val) or
                 (isoftype(val, PreObject) and isIterableType(val.objType))):
            for widget in reversed(self.inputWidgets):
                self.delInputWidget(widget)
            self.objVal = val
            for val in self.objVal:
                self._addInputWidget(val)
        else:
            print("Value is not iterable")
            for widget in reversed(self.inputWidgets):
                self.delInputWidget(widget)


class LangStringSetGroupBox(IterableGroupBox):
    def __init__(self, objTypeHint, **kwargs):
        self.langStringTypeHint = objTypeHint
        objTypeHint = Dict[str, str]
        super().__init__(objTypeHint, **kwargs)

    def getPreObj(self):
        preObjDict = super().getPreObj()
        return PreObject(self.langStringTypeHint, (preObjDict,), {})

    def setVal(self, val):
        if isinstance(val, LangStringSet):
            super().setVal(copy.copy(val._dict))
        else:
            super().setVal(val)


class TypeOptionObjGroupBox(GroupBox):
    """GroupBox with option to choose widget for which type will be generated"""

    def __init__(self, objTypes: Iterable, defType=str, **kwargs):
        objTypes = list(objTypes)
        super(TypeOptionObjGroupBox, self).__init__(objTypes[0], **kwargs)

        self.objTypes = objTypes
        # remove abstract types
        for typ in list(self.objTypes):
            if isabstract(typ):
                self.objTypes.remove(typ)

        self.initTypeComboBox()
        if defType is not None and defType in objTypes:
            index = self.typeComboBox.findText(getTypeName(defType), Qt.MatchFlag.MatchExactly)
            if index > -1:
                self.typeComboBox.setCurrentIndex(index)
        currObjType = self.typeComboBox.currentData()

        kwargs["parent"] = self
        kwargs["title"] = ""
        self.widget = QWidget()
        self.replaceGroupBoxWidget(currObjType, **kwargs)
        self.layout().addRow(self.widget)

        # change input widget for new type if type in combobox changed
        self.typeComboBox.currentIndexChanged.connect(
            lambda i: self.replaceGroupBoxWidget(self.typeComboBox.itemData(i), **kwargs))

    def initTypeComboBox(self):
        """Init func for ComboBox where desired Type of input data will be chosen"""
        self.typeComboBox = widgets.CompleterComboBox(self)
        for typ in self.objTypes:
            self.typeComboBox.addItem(getTypeName(typ), typ)
            self.typeComboBox.model().sort(0, Qt.SortOrder.AscendingOrder)
        if self.objVal:
            objValType = self.objVal.objType if isoftype(self.objVal, PreObject) else type(self.objVal)
            self.typeComboBox.setCurrentIndex(self.typeComboBox.findData(objValType))
        else:
            self.typeComboBox.setCurrentIndex(0)
        self.layout().addRow(self.typeComboBox)

    def replaceGroupBoxWidget(self, objType, **kwargs):
        """Changes input GroupBox due to objType structure"""
        kwargs["objVal"] = self.objVal
        kwargs["paramsToHide"] = {}
        kwargs["paramsToAttrs"] = {}
        includeInheritedTyps = False if inheritors(objType) else False
        newWidget = InputWidgetUtil.getInputWidget(objType, includeInheritedTyps=includeInheritedTyps, **kwargs)
        self.layout().replaceWidget(self.widget, newWidget)
        self.widget.close()
        newWidget.showMinimized()
        self.widget = newWidget
        if isinstance(self.widget, QGroupBox):
            self.widget.setFlat(True)
        if isinstance(self.widget, (ObjGroupBox, IterableGroupBox)) and not self.widget.inputWidgets:
            self.widget.hide()
        self.adjustSize()

    def getPreObj(self):
        return self.widget.getPreObj()

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        return self.widget.getObj2add()

    def setVal(self, val):
        valType = val.objType if isoftype(val, PreObject) else type(val)
        if valType in self.objTypes:
            self.objVal = val
            self.typeComboBox.setCurrentIndex(self.typeComboBox.findData(type(self.objVal)))


class ChooseItemDialog(AddDialog):
    def __init__(self, view: 'TreeView', columnsToShow=(ATTRIBUTE_COLUMN,),
                 validator=lambda chosenIndex: chosenIndex.isValid(),
                 parent: Optional[QWidget] = None, title: str = ""):
        super(ChooseItemDialog, self).__init__(parent, title)
        self.setFixedHeight(500)
        self.validator = validator
        self.view = view
        self.view.setParent(self)
        self.view.setModelWithProxy(self.view.sourceModel())
        self.view.expandAll()
        self.view.setHeaderHidden(True)

        for column in range(self.view.model().columnCount()):
            if column not in columnsToShow:
                self.view.hideColumn(column)

        self.searchBar = widgets.SearchBar(self.view, parent=self, filterColumns=columnsToShow)
        self.toolBar = widgets.ToolBar(self)
        self.toolBar.addAction(self.view.collapseAllAct)
        self.toolBar.addAction(self.view.expandAllAct)
        self.toolBar.addWidget(self.searchBar)

        self.layout().insertWidget(0, self.toolBar)
        self.layout().insertWidget(1, self.view)
        self.buildHandlers()

    def buildHandlers(self):
        self.view.selectionModel().currentChanged.connect(self.validate)

    def validate(self):
        chosenIndex = self.view.currentIndex()
        if chosenIndex.isValid() and self.validator(chosenIndex):
            self.buttonOk.setEnabled(True)
        else:
            self.buttonOk.setDisabled(True)

    def getObj2add(self):
        return self.view.currentIndex()

    def getChosenItem(self):
        return self.getObj2add()


class ModelReferenceGroupBox(ObjGroupBox):
    # use CHOOSE_FRM_VIEW if no chooseFrmView is given
    # can be changed outside of class
    CHOOSE_FRM_VIEW = None

    def __init__(self, objTypeHint, chooseFrmView=None, **kwargs):
        super(ModelReferenceGroupBox, self).__init__(objTypeHint, **kwargs)
        self.chooseFrmView: 'TreeView' = chooseFrmView if chooseFrmView else self.CHOOSE_FRM_VIEW
        if self.chooseFrmView:
            plusButton = QPushButton(f"Choose from local", self,
                                     toolTip="Choose element for reference",
                                     clicked=self.chooseFromLocal)
            self.layout().addRow(plusButton)

    def chooseFromLocal(self):
        tree = widgets.PackTreeView(editEnabled=False)
        sourceModel = self.chooseFrmView.sourceModel()
        tree.setModel(sourceModel)

        dialog = ChooseItemDialog(
            view=tree, parent=self, title="Choose item for reference",
            validator=lambda chosenIndex: isinstance(chosenIndex.data(OBJECT_ROLE), Referable))

        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("Item adding accepted")
            item = dialog.getChosenItem()
            referable = item.data(OBJECT_ROLE)
            reference = ModelReference.from_referable(referable)
            self.setVal(reference)
        else:
            print("Item adding cancelled")
        dialog.deleteLater()
