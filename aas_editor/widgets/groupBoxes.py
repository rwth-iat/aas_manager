#  Copyright (C) 2025  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
import copy
from enum import unique, Enum
from inspect import isabstract
from typing import List, Dict, Union, Iterable

from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtWidgets import QGroupBox, QFormLayout, QWidget, QPushButton, QDialog
from basyx.aas.model import LangStringSet, Referable, ModelReference

import widgets
import widgets.buttons
from additional.classes import DictItem
from widgets.widget_util import InputWidgetUtil
from settings import DEFAULT_COMPLETIONS, DEFAULTS, OBJECT_ROLE
from utils.util import getReqParams4init, getParamsAndTypehints4init, getDefaultVal, delAASParent, inheritors

from utils.util_classes import ClassesInfo, PreObject
from utils.util_type import isOptional, issubtype, getTypeName, typeHintToType, isoftype, isIterable, isIterableType, \
    isValOk4Typehint
from widgets.editWidgets import StandardInputWidget
from widgets.messsageBoxes import ErrorMessageBox


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
        btn = widgets.buttons.CreateOptionalParamBtn("Create", paramName=paramName,
                                                     objTypehint=self.reqParamsDict[paramName],
                                                     parent=self, clicked=self.addWidget4optionalParam)
        return btn

    def addWidget4optionalParam(self):
        layout: QFormLayout = self.layout()
        for row in range(layout.rowCount()):
            try:
                item = layout.itemAt(row, QFormLayout.ItemRole.FieldRole)
                if self.sender() == item.widget():
                    createBtn: widgets.buttons.CreateOptionalParamBtn = item.widget()
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
    def __init__(self, widget: Union[widgets.editWidgets.StandardInputWidget, widgets.editWidgets.SpecialInputWidget], parent=None):
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

        self.initTypeComboBox(defType=defType)
        currObjType = self.typeComboBox.currentData()

        kwargs["parent"] = self
        kwargs["title"] = ""
        self.widget = QWidget()
        self.replaceGroupBoxWidget(currObjType, **kwargs)
        self.layout().addRow(self.widget)

        # change input widget for new type if type in combobox changed
        self.typeComboBox.currentIndexChanged.connect(
            lambda i: self.replaceGroupBoxWidget(self.typeComboBox.itemData(i), **kwargs))

    def initTypeComboBox(self, defType=str):
        """Init func for ComboBox where desired Type of input data will be chosen"""
        self.typeComboBox = widgets.editWidgets.CompleterComboBox(self)
        for typ in self.objTypes:
            self.typeComboBox.addItem(getTypeName(typ), typ)
            self.typeComboBox.model().sort(0, Qt.SortOrder.AscendingOrder)
        if self.objVal:
            objValType = self.objVal.objType if isoftype(self.objVal, PreObject) else type(self.objVal)
            self.typeComboBox.setCurrentIndex(self.typeComboBox.findData(objValType))
        elif defType is not None and defType in self.objTypes:
            index = self.typeComboBox.findText(getTypeName(defType), Qt.MatchFlag.MatchExactly)
            if index > -1:
                self.typeComboBox.setCurrentIndex(index)
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
        from aas_editor.treeviews.treeview_pack import PackTreeView
        from aas_editor.dialogs import ChooseItemDialog

        tree = PackTreeView(editEnabled=False)
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
