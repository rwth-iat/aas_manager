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
from openpyxl.worksheet.worksheet import Worksheet

from aas_editor.import_feature.import_settings import MAPPING_ATTR
from aas_editor.package import Package
from aas_editor.utils.util_type import isIterable

COLUMNS_PATTERN = re.compile(r"\$[A-Z][A-Z]?\$")


def colLettersInExcelSheet(sheet: Worksheet) -> List[str]:
    colLetters = []
    for columnNum in range(1, sheet.max_column + 1):
        colLetters.append(openpyxl.utils.cell.get_column_letter(columnNum))
    return colLetters


def importRowValueFromExcel(sourcefile, sheetname=None, row=2):
    excel_file = openpyxl.load_workbook(sourcefile, data_only=True)
    if not sheetname:
        sheetname = excel_file.sheetnames[0]
    sheet = excel_file[sheetname]

    rowValue: Dict = {}
    for colLetter in colLettersInExcelSheet(sheet):
        rowValue[colLetter] = str(sheet[f"{colLetter}{row}"].value)  # TODO Fixme
    return rowValue


def _mapping4referableIntoDict(obj, mapDict):
    mapping = getattr(obj, MAPPING_ATTR, {})
    if mapping:
        ref = AASReference.from_referable(obj)
        keys = ','.join(
            [f"Key(type_={i.type}, local={i.local}, id_type={i.id_type}, value='{i.value}')" for i in ref.key])
        target_type = repr(ref.type).lstrip("<class '").rstrip("'>")
        mapDict[f"AASReference(target_type={target_type}, key=({keys},))"] = mapping


def _mappingIntoDict(obj, mapDict):
    """Save all existing mappings in the obj into mapDict"""
    _mapping4referableIntoDict(obj, mapDict)
    if isIterable(obj):
        for i in obj:
            _mappingIntoDict(i, mapDict)


def getMapping(pack: Package):
    mapDict = dict()
    for obj in pack.objStore:
        _mappingIntoDict(obj, mapDict)
    return mapDict


def saveMapping(pack: Package, file: str) -> bool:
    mapDict = getMapping(pack)
    with open(file, 'w') as jsonFile:
        json.dump(mapDict, jsonFile)
        jsonFile.close()
    return True


def usedColumnsInMapping(mapDict) -> List[str]:
    mapping = str(mapDict)
    columns: List[str] = re.findall(COLUMNS_PATTERN, mapping)
    columns = list(set([col.strip("$") for col in columns]))
    columns.sort()
    columns.sort(key=len)
    return columns


def unusedColumnsInMapping(mapDict, sourcefile, sheetname: Worksheet) -> List[str]:
    excel_file = openpyxl.load_workbook(sourcefile, data_only=True)
    if not sheetname:
        sheetname = excel_file.sheetnames[0]
    sheet = excel_file[sheetname]

    usedColumns = usedColumnsInMapping(mapDict)
    columns = colLettersInExcelSheet(sheet)
    for col in usedColumns:
        columns.remove(col)
    columns.sort(key=len)
    return columns


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


def importValueFromExcelWB(value, workbook: openpyxl.Workbook, sheetname, row=2):
    sheet = workbook[sheetname]

    columns: List[str] = re.findall(COLUMNS_PATTERN, value)
    for col in columns:
        column = col.strip("$")
        importedVal = str(sheet[f"{column}{row}"].value)  # FIXME
        value = value.replace(f"${column}$", importedVal, -1)
    return value


def importValueFromExcel(value, sourcefile, sheetname, row=2):
    excel_file = openpyxl.load_workbook(sourcefile, data_only=True)
    return importValueFromExcelWB(value, excel_file, sheetname, row)


def importValueFromExampleRow(rawValue: str, row: Dict):
    value = rawValue
    columns: List[str] = re.findall(COLUMNS_PATTERN, rawValue)
    for col in columns:
        column = col.strip("$")
        importedVal = row[column]
        value = value.replace(f"${column}$", importedVal, -1)
    return value


def isValueToImport(value):
    if re.search(COLUMNS_PATTERN, value):
        return True
    return False
