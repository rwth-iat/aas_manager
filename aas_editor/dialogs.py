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

from basyx.aas.model.base import *

from enum import Enum, unique
from inspect import isabstract
from typing import Union, List, Dict, Optional

from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPaintEvent, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QDialogButtonBox, \
    QGroupBox, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QScrollArea, QFrame, QFormLayout

from aas_editor.editWidgets import StandardInputWidget, SpecialInputWidget
from aas_editor.settings import DEFAULTS, DEFAULT_COMPLETIONS, ATTRIBUTE_COLUMN, OBJECT_ROLE, \
    APPLICATION_NAME, CONTRIBUTORS, CONTACT, COPYRIGHT_YEAR, VERSION, DEFAULT_INHERITOR
from aas_editor.delegates import ColorDelegate
from aas_editor.utils.util import inheritors, getReqParams4init, getParams4init, getDefaultVal, \
    getAttrDoc, delAASParents
from aas_editor.utils.util_type import getTypeName, issubtype, isoftype, isSimpleIterableType, \
    isIterableType, isIterable
from aas_editor.utils.util_classes import DictItem, ClassesInfo
from aas_editor.widgets import *
from aas_editor import widgets


class AboutDialog(QMessageBox):
    def __init__(self, parent=None):  # <1>
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setText(
            f"{APPLICATION_NAME}\n"
            f"Version: {VERSION}\n"
            f"Contributors: {CONTRIBUTORS}\n"
            f"Contact: {CONTACT}\n"
            f"Copyright (C) {COPYRIGHT_YEAR}"
        )
        self.setIconPixmap(QPixmap("aas_editor/icons/logo.svg"))


class AddDialog(QDialog):
    """Base abstract class for custom dialogs for adding data"""

    def __init__(self, parent=None, title=""):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonCancel = self.buttonBox.button(QDialogButtonBox.Cancel)
        self.buttonCancel.released.connect(self.reject)
        self.buttonOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.buttonOk.released.connect(self.accept)
        self.buttonOk.setDisabled(True)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 300, 600))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.setMinimumWidth(480)
        self.setMaximumHeight(900)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayoutScroll = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayoutScroll.setContentsMargins(0,0,0,0)

    def adjustSize(self) -> None:
        layoutSize = self.layout().sizeHint()
        buttonsSize = self.buttonBox.sizeHint()
        result = QSize(max(layoutSize.width(), buttonsSize.width()), layoutSize.height() + buttonsSize.height() + 10)
        self.resize(result)

    def layout(self) -> 'QLayout':
        return self.verticalLayoutScroll

    def getObj2add(self):
        pass


def checkIfAccepted(func):
    """Decorator for checking if user clicked ok"""

    def wrap(addDialog):
        if addDialog.result() == QDialog.Accepted:
            return func(addDialog)
        else:
            raise ValueError("Adding was cancelled")

    return wrap


def getInputWidget(objType, rmDefParams=True, title="", paramsToHide: dict = None,
                   parent=None, objVal=None, paramsToAttrs=None, includeInheritedTyps=True, **kwargs) -> QWidget:
    print(objType, objType.__str__, objType.__repr__, objType.__class__)

    if objVal and not isoftype(objVal, objType):
        print("Given object type does not match to real object type:", objType, objVal)
        objVal = None

    paramsToHide = paramsToHide if paramsToHide else ClassesInfo.default_params_to_hide(objType)
    paramsToAttrs = paramsToAttrs if paramsToAttrs else ClassesInfo.params_to_attrs(objType)
    kwargs = {
        "rmDefParams": rmDefParams,
        "title": title,
        "paramsToHide": paramsToHide,
        "paramsToAttrs": paramsToAttrs,
        "parent": parent,
        "objVal": objVal,
        **kwargs
    }

    # if obj is given and rmDefParams = True, save all not mandatory init params of obj with val in paramsToHide
    # if obj is given and rmDefParams = False, save all hidden init params of obj with val in paramsToHide
    # and show user only required params to set
    params, defaults = getParams4init(objType)
    if defaults:
        prms = list(params.keys())[len(params)-len(defaults):]
        paramsDefaults = dict(zip(prms, defaults))
    else:
        paramsDefaults = dict()
    reqParams = getReqParams4init(objType, rmDefParams=True)
    hiddenAttrs = ClassesInfo.hiddenAttrs(objType)

    for param in params.keys():
        attr = paramsToAttrs.get(param, param)

        if rmDefParams and objVal:
            if param in reqParams:
                continue
            else:
                try:
                    paramsToHide[param] = getattr(objVal, attr.rstrip("_"))  # TODO fix if aas changes
                except AttributeError:
                    paramsToHide[param] = getattr(objVal, attr)
        elif attr in hiddenAttrs and param not in paramsToHide:
            if objVal:
                paramsToHide[param] = getattr(objVal, attr)
            elif param in paramsDefaults:
                paramsToHide[param] = paramsDefaults[param]

    if isabstract(objType) and not isIterableType(objType):
        objTypes = inheritors(objType)
        kwargs["defType"] = DEFAULT_INHERITOR.get(objType, None)
        widget = TypeOptionObjGroupBox(objTypes, **kwargs)
    elif isSimpleIterableType(objType):
        widget = IterableGroupBox(objType, **kwargs)
    elif issubtype(objType, Union):
        objTypes = objType.__args__
        widget = TypeOptionObjGroupBox(objTypes, **kwargs)
    elif issubtype(objType, AASReference):
        widget = AASReferenceGroupBox(objType, **kwargs)
    elif issubtype(objType, SpecialInputWidget.types):
        widget = SpecialInputWidget(objType, **kwargs)
    elif issubtype(objType, StandardInputWidget.types):
        widget = StandardInputWidget(objType, **kwargs)
    elif includeInheritedTyps and inheritors(objType):
        objTypes = list(inheritors(objType))
        objTypes.append(objType)
        kwargs["defType"] = DEFAULT_INHERITOR.get(objType, None)
        widget = TypeOptionObjGroupBox(objTypes, **kwargs)
    else:
        widget = ObjGroupBox(objType, **kwargs)
    return widget


class AddObjDialog(AddDialog):
    def __init__(self, objType, parent: 'TreeView', title="", rmDefParams=True, objVal=None):
        title = title if title else f"Add {getTypeName(objType)}"
        AddDialog.__init__(self, parent, title=title)
        self.buttonOk.setEnabled(True)

        objVal = copy.deepcopy(objVal)
        delAASParents(objVal)

        kwargs = {
            "rmDefParams": rmDefParams,
            "objVal": objVal,
            "parent": self,
        }

        self.inputWidget = getInputWidget(objType, **kwargs)
        self.inputWidget.setObjectName("mainBox")
        self.inputWidget.setStyleSheet("#mainBox{border:0;}") #FIXME
        self.layout().addWidget(self.inputWidget)
        self.adjustSize()

    def getInputWidget(self):
        pass

    @checkIfAccepted
    def getObj2add(self):
        return self.inputWidget.getObj2add()


@unique
class GroupBoxType(Enum):
    SIMPLE = 0
    CLOSABLE = 1
    ADDABLE = 2


class GroupBox(QGroupBox):
    """Groupbox which also can be closable groupbox"""
    def __init__(self, objType, parent=None, title="", paramsToHide: dict = None, rmDefParams=True,
                 objVal=None, paramsToAttrs=None, **kwargs):
        super().__init__(parent)
        if title:
            self.setTitle(title)

        self.objType = objType
        self.paramsToHide = paramsToHide if paramsToHide else ClassesInfo.default_params_to_hide(objType)
        self.paramsToAttrs = paramsToAttrs if paramsToAttrs else ClassesInfo.params_to_attrs(objType)
        self.rmDefParams = rmDefParams
        self.objVal = objVal

        self.setAlignment(Qt.AlignLeft)
        self.setLayout(QFormLayout(self))
        self.type = GroupBoxType.SIMPLE

    def paintEvent(self, a0: QPaintEvent) -> None:
        super(GroupBox, self).paintEvent(a0)
        if self.isCheckable():
            self.setStyleSheet(
                "GroupBox::indicator:checked"
                "{"
                "    border-image: url(aas_editor/icons/close-hover.svg);"
                "}"
                "GroupBox::indicator:checked:hover,"
                "GroupBox::indicator:checked:focus,"
                "GroupBox::indicator:checked:pressed"
                "{"
                "    border-image: url(aas_editor/icons/close-pressed.svg);"
                "}"
            )

    def setClosable(self, b: bool) -> None:
        self.type = GroupBoxType.CLOSABLE if b else GroupBoxType.SIMPLE
        self.setCheckable(b)

    def isClosable(self) -> bool:
        return self.isCheckable() and self.type is GroupBoxType.CLOSABLE

    def setAddable(self, b: bool) -> None:
        self.type = GroupBoxType.ADDABLE if b else GroupBoxType.SIMPLE
        self.setCheckable(b)

    def isAddable(self) -> bool:
        return self.isCheckable() and self.type is GroupBoxType.ADDABLE

    def setVal(self, val):
        pass


class ObjGroupBox(GroupBox):
    def __init__(self, objType, parent=None, paramsToHide: dict = None, objVal=None, paramsToAttrs: dict = None, **kwargs):
        super().__init__(objType, objVal=objVal, parent=parent, paramsToHide=paramsToHide, paramsToAttrs=paramsToAttrs, **kwargs)

        self.inputWidgets: List[QWidget] = []
        self.paramWidgetDict: Dict[str, QWidget] = {}

        self.reqParamsDict = getReqParams4init(self.objType, self.rmDefParams, self.paramsToHide)
        self.kwargs = kwargs.copy() if kwargs else {}
        self.initLayout()

    def initLayout(self):
        if self.reqParamsDict:
            for param, paramType in self.reqParamsDict.items():
                # TODO delete when right _ will be deleted in aas models
                attr = self.paramsToAttrs.get(param, param)
                val = getattr(self.objVal, attr.rstrip("_"),
                              DEFAULTS.get(self.objType, {}).get(attr, getDefaultVal(self.objType, param, None)))
                self.kwargs["completions"] = DEFAULT_COMPLETIONS.get(self.objType, {}).get(param, [])
                self.getInputWidget(param, paramType, val, **self.kwargs)
        # else: # TODO check if it works ok
        #     inputWidget = self.getInputWidget(objName, objType, rmDefParams, objVal)
        #     self.layout().addWidget(inputWidget)

    def getInputWidget(self, param: str, paramType, val, **kwargs) -> QHBoxLayout:
        print(f"Getting widget for param: {param} of type: {paramType}")
        widget = getInputWidget(paramType, objVal=val, **kwargs)
        self.paramWidgetDict[param] = widget

        if isinstance(widget, QGroupBox):
            widget.setTitle(param)
            self.layout().addRow(widget)
        else:
            self.layout().addRow(param, widget)
        self.inputWidgets.append(widget)

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        paramValueDict = {}
        for param, widget in self.paramWidgetDict.items():
            paramValueDict[param] = widget.getObj2add()
        for param, value in self.paramsToHide.items():
            paramValueDict[param] = value
        try:
            obj = self.objType(**paramValueDict)
        except TypeError:
            for key in ClassesInfo.default_params_to_hide(object):
                try:
                    paramValueDict.pop(key)
                except KeyError:
                    continue
            obj = self.objType(**paramValueDict)
        return obj

    def delInputWidget(self, widget: QWidget):
        self.layout().removeWidget(widget)
        widget.close()
        self.inputWidgets.remove(widget)

        self.adjustSize()
        self.window().adjustSize()

    def setVal4param(self, param: str, val):
        paramWidget = self.paramWidgetDict[param]
        paramWidget.setVal(val)

    def setVal(self, val):
        if val and isoftype(val, self.objType):
            self.objVal = val
            for widget in reversed(self.inputWidgets):
                self.delInputWidget(widget)
            self.initLayout()
        else:
            print("Value does not fit to req obj type", type(val), self.objType)


class SingleWidgetGroupBox(GroupBox):
    def __init__(self, widget: Union[StandardInputWidget, SpecialInputWidget], parent=None):
        super(SingleWidgetGroupBox, self).__init__(widget.objType, parent)
        self.inputWidget = widget
        self.layout().addWidget(widget)

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        return self.inputWidget.getObj2add()

    def setVal(self, val):
        self.inputWidget.setVal(val)


class IterableGroupBox(GroupBox):
    def __init__(self, objType, **kwargs):
        super().__init__(objType, **kwargs)
        self.argTypes = list(self.objType.__args__)
        self.kwargs = kwargs.copy() if kwargs else {}
        plusButton = QPushButton(f"+ Element", self,
                                 toolTip="Add element",
                                 clicked=self._addInputWidget)
        self.layout().addWidget(plusButton)
        self.inputWidgets = []
        self.setVal(self.objVal)

    def _addInputWidget(self, objVal=None):
        if ... in self.argTypes:
            self.argTypes.remove(...)

        if not issubtype(self.objType, dict):
            if len(self.argTypes) == 1:
                argType = self.argTypes[0]
            else:
                raise TypeError(f"expected 1 argument, got {len(self.argTypes)}", self.argTypes)
        else: #  if parentType = dict
            if len(self.argTypes) == 2:
                DictItem._field_types["key"] = self.argTypes[0]
                DictItem._field_types["value"] = self.argTypes[1]
                argType = DictItem
            else:
                raise TypeError(f"expected 2 arguments, got {len(self.argTypes)}", self.argTypes)

        self.kwargs.update({
            "objType": argType,
            "title": f"{getTypeName(argType)} {len(self.inputWidgets)+1}",
            "rmDefParams": self.rmDefParams,
            "objVal": objVal
        })
        widget = getInputWidget(**self.kwargs)
        if not isinstance(widget, GroupBox):
            widget = SingleWidgetGroupBox(widget)
        widget.setClosable(True)
        widget.setFlat(True)
        widget.toggled.connect(lambda: self.delInputWidget(widget))
        self.inputWidgets.append(widget)
        self.layout().addWidget(widget)

    def delInputWidget(self, widget: QWidget):
        self.layout().removeWidget(widget)
        widget.close()
        self.inputWidgets.remove(widget)
        for i, widget in enumerate(self.inputWidgets):
            res: str = widget.title().rstrip("0123456789")
            widget.setTitle(f"{res}{i+1}")
        self.adjustSize()
        self.window().adjustSize()

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        listObj = []
        for widget in self.inputWidgets:
            listObj.append(widget.getObj2add())
        if issubtype(self.objType, tuple):
            obj = tuple(listObj)
        elif issubtype(self.objType, list):
            obj = list(listObj)
        elif issubtype(self.objType, set):
            obj = set(listObj)
        elif issubtype(self.objType, dict):
            obj = dict(listObj)
        else:
            obj = list(listObj)
        return obj

    def setVal(self, val):
        if isinstance(val, dict):
            val = [DictItem(key, value) for key, value in val.items()]

        if val and isIterable(val):
            for widget in reversed(self.inputWidgets):
                self.delInputWidget(widget)
            self.objVal = val
            for val in self.objVal:
                self._addInputWidget(val)
        else:
            print("Value is not iterable")
            for widget in reversed(self.inputWidgets):
                self.delInputWidget(widget)


class TypeOptionObjGroupBox(GroupBox):
    """GroupBox with option to choose widget for which type will be generated"""
    def __init__(self, objTypes: List, defType=None, **kwargs):
        objTypes = list(objTypes)
        super(TypeOptionObjGroupBox, self).__init__(objTypes[0], **kwargs)

        self.objTypes = objTypes
        # remove abstract types
        for typ in list(self.objTypes):
            if isabstract(typ):
                self.objTypes.remove(typ)

        self.initTypeComboBox()
        if defType is not None and defType in objTypes:
            index = self.typeComboBox.findText(getTypeName(defType), Qt.MatchExactly)
            if index > -1:
                self.typeComboBox.setCurrentIndex(index)
        currObjType = self.typeComboBox.currentData()

        kwargs["parent"] = self
        kwargs["title"] = ""
        self.widget = QWidget()
        self.replaceGroupBoxWidget(currObjType, **kwargs)
        self.layout().addWidget(self.widget)

        # change input widget for new type if type in combobox changed
        self.typeComboBox.currentIndexChanged.connect(
            lambda i: self.replaceGroupBoxWidget(self.typeComboBox.itemData(i), **kwargs))

    def initTypeComboBox(self):
        """Init func for ComboBox where desired Type of input data will be chosen"""
        self.typeComboBox = CompleterComboBox(self)
        for typ in self.objTypes:
            self.typeComboBox.addItem(getTypeName(typ), typ)
            self.typeComboBox.model().sort(0, Qt.AscendingOrder)
        if self.objVal:
            self.typeComboBox.setCurrentIndex(self.typeComboBox.findData(type(self.objVal)))
        else:
            self.typeComboBox.setCurrentIndex(0)
        self.layout().addWidget(self.typeComboBox)

    def replaceGroupBoxWidget(self, objType, **kwargs):
        """Changes input GroupBox due to objType structure"""
        kwargs["objVal"] = self.objVal
        includeInheritedTyps = False if inheritors(objType) else False
        newWidget = getInputWidget(objType, includeInheritedTyps=includeInheritedTyps, **kwargs)
        self.layout().replaceWidget(self.widget, newWidget)
        self.widget.close()
        newWidget.showMinimized()
        self.widget = newWidget
        if isinstance(self.widget, QGroupBox):
            self.widget.setFlat(True)
        if isinstance(self.widget, (ObjGroupBox, IterableGroupBox)) and not self.widget.inputWidgets:
            self.widget.hide()
        self.window().adjustSize()

    def getObj2add(self):
        """Return resulting obj due to user input data"""
        return self.widget.getObj2add()

    def setVal(self, val):
        if val and type(val) in self.objTypes:
            self.objVal = val
            self.typeComboBox.setCurrentIndex(self.typeComboBox.findData(type(self.objVal)))


class ChooseItemDialog(AddDialog):
    def __init__(self, view: 'TreeView', columnsToShow=[ATTRIBUTE_COLUMN],
                 validator=lambda chosenIndex: chosenIndex.isValid(),
                 parent: Optional[QWidget] = None, title: str = ""):
        super(ChooseItemDialog, self).__init__(parent, title)
        self.setFixedHeight(500)
        self.validator = validator
        self.view = view
        self.view.setParent(self)
        self.view.setItemDelegate(ColorDelegate(view))
        self.view.setModelWithProxy(self.view.sourceModel())
        self.view.expandAll()
        self.view.setHeaderHidden(True)

        for column in range(self.view.model().columnCount()):
            if column not in columnsToShow:
                self.view.hideColumn(column)

        self.searchBar = SearchBar(self.view, parent=self, filterColumns=columnsToShow)
        self.toolBar = ToolBar(self)
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


class AASReferenceGroupBox(ObjGroupBox):
    # use CHOOSE_FRM_VIEW if no chooseFrmView is given
    # can be changed outside of class
    CHOOSE_FRM_VIEW = None

    def __init__(self, objType, chooseFrmView=None, **kwargs):
        super(AASReferenceGroupBox, self).__init__(objType, **kwargs)
        self.chooseFrmView: 'TreeView' = chooseFrmView if chooseFrmView else self.CHOOSE_FRM_VIEW
        if self.chooseFrmView:
            plusButton = QPushButton(f"Choose from local", self,
                                     toolTip="Choose element for reference",
                                     clicked=self.chooseFromLocal)
            self.layout().addWidget(plusButton)

    def chooseFromLocal(self):
        tree = widgets.PackTreeView()
        sourceModel = self.chooseFrmView.sourceModel()
        tree.setModel(sourceModel)

        dialog = ChooseItemDialog(
            view=tree, parent=self, title="Choose item for reference",
            validator=lambda chosenIndex: isinstance(chosenIndex.data(OBJECT_ROLE), Referable))

        if dialog.exec_() == QDialog.Accepted:
            print("Item adding accepted")
            item = dialog.getChosenItem()
            referable = item.data(OBJECT_ROLE)
            reference = AASReference.from_referable(referable)
            self.setVal(reference)
        else:
            print("Item adding cancelled")
        dialog.deleteLater()
