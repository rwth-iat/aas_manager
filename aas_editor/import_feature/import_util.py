#  Copyright (C) 2022  Igor Garmaev, garmaev@gmx.net
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
import json
import re
from typing import List, Dict

import basyx
import openpyxl
from basyx.aas import model
from basyx.aas.model import AASReference, Key

from aas_editor.import_feature.import_settings import MAPPING_ATTR
from aas_editor.package import Package
from aas_editor.utils.util_type import isIterable

COLUMNS_PATTERN = re.compile(r"\$[A-Z][A-Z]?\$")


def _saveMapping4referable(obj, mapDict):
    mapping = getattr(obj, MAPPING_ATTR, {})
    if mapping:
        ref = AASReference.from_referable(obj)
        keys = ','.join([f"Key(type_={i.type}, local={i.local}, id_type={i.id_type}, value='{i.value}')" for i in ref.key])
        target_type = repr(ref.type).lstrip("<class '").rstrip("'>")
        mapDict[f"AASReference(target_type={target_type}, key=({keys},))"] = mapping


def _saveMapping(obj, mapDict):
    _saveMapping4referable(obj, mapDict)
    if isIterable(obj):
        for i in obj:
            _saveMapping(i, mapDict)


def saveMapping(pack: Package, file: str) -> bool:
    mapDict = dict()
    for obj in pack.objStore:
        _saveMapping(obj, mapDict)
    with open(file, 'w') as jsonFile:
        json.dump(mapDict, jsonFile)
        jsonFile.close()
    return True


def setMappingFromFile(pack: Package, mappingFile: str):
    with open(mappingFile, 'r') as jsonFile:
        mapDict = json.load(jsonFile)

    for refRepr in mapDict:
        aasref: AASReference = eval(refRepr, {
            "KeyElements": model.KeyElements,
            "KeyType": model.KeyType,
            "Key": Key,
            "AASReference": AASReference,
            "basyx": basyx,
        })
        refObj = aasref.resolve(pack.objStore)
        mapping = mapDict[refRepr]
        setattr(refObj, MAPPING_ATTR, mapping)


def importValue(value, sourcefile, row=2):
    excel_file = openpyxl.load_workbook(sourcefile, data_only=True)
    sheetname = excel_file.sheetnames[0]
    sheet = excel_file[sheetname]

    columns: List[str] = re.findall(COLUMNS_PATTERN, value)
    for col in columns:
        column = col.strip("$")
        importedVal = sheet[f"{column}{row}"].value
        value = value.replace(f"${column}$", importedVal, -1)
    return value


def importValueFromExampleRow(rawValue: str, row:Dict):
    value = rawValue
    columns: List[str] = re.findall(COLUMNS_PATTERN, rawValue)
    for col in columns:
        column = col.strip("$")
        importedVal = row[column]
        value = rawValue.replace(f"${column}$", importedVal, -1)
    return value


def isValueToImport(value):
    if re.search(COLUMNS_PATTERN, value):
        return True
    return False


def importRowValue(sourcefile, row=2):
    excel_file = openpyxl.load_workbook(sourcefile, data_only=True)
    sheetname = excel_file.sheetnames[0]
    sheet = excel_file[sheetname]

    rowValue: Dict = {}
    for columnNum in range(1,sheet.max_column+1):
        column = openpyxl.utils.cell.get_column_letter(columnNum)
        rowValue[column] = sheet[f"{column}{row}"].value
    return rowValue
