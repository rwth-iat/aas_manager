#  Copyright (C) 2025  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from inspect import isabstract
from typing import Union

from PyQt6.QtWidgets import QWidget
from basyx.aas.model import LangStringSet, ModelReference

import widgets.editWidgets
import widgets.groupBoxes
from settings import DEFAULT_INHERITOR
from utils.util import getParamsAndTypehints4init, getReqParams4init, inheritors
from utils.util_classes import ClassesInfo
from utils.util_type import removeOptional, isOptional, isValOk4Typehint, isIterableType, issubtype, \
    isSimpleIterableType, isUnion


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
            widget = widgets.groupBoxes.TypeOptionObjGroupBox(objTypes, **kwargs)
        elif issubtype(objTypeHint, LangStringSet):
            widget = widgets.groupBoxes.LangStringSetGroupBox(objTypeHint, **kwargs)
        elif isSimpleIterableType(objTypeHint):
            widget = widgets.groupBoxes.IterableGroupBox(objTypeHint, **kwargs)
        elif isUnion(objTypeHint):
            objTypes = objTypeHint.__args__
            widget = widgets.groupBoxes.TypeOptionObjGroupBox(objTypes, **kwargs)
        elif issubtype(objTypeHint, ModelReference):
            widget = widgets.groupBoxes.ModelReferenceGroupBox(objTypeHint, **kwargs)
        elif issubtype(objTypeHint, widgets.editWidgets.SpecialInputWidget.types):
            widget = widgets.editWidgets.SpecialInputWidget(objTypeHint, **kwargs)
        elif issubtype(objTypeHint, widgets.editWidgets.StandardInputWidget.types):
            widget = widgets.editWidgets.StandardInputWidget(objTypeHint, **kwargs)
        elif includeInheritedTyps and inheritors(objTypeHint):
            objTypes = list(inheritors(objTypeHint))
            objTypes.append(objTypeHint)
            kwargs["defType"] = DEFAULT_INHERITOR.get(objTypeHint, None)
            widget = widgets.groupBoxes.TypeOptionObjGroupBox(objTypes, **kwargs)
        else:
            widget = widgets.groupBoxes.ObjGroupBox(objTypeHint, **kwargs)
        return widget
