"""Open a file in the app's models, change it, save it, compare the result.

Each test changes a copy through the models (as the GUI does) and the
expected package directly through basyx, then compares both as JSON:
the saved file must contain the change and nothing else.
"""
import io
import json
from pathlib import Path
from typing import Callable, Optional, Tuple

import pytest
# QtWebEngineWidgets must be imported before the QApplication exists (qapp fixture)
from PyQt6 import QtWebEngineWidgets  # noqa: F401
from PyQt6.QtCore import QModelIndex, Qt

from aas_editor_test.conftest import TEST_FILES_DIR

SAMPLES = [
    "IDTA 02002-1-0_Template_ContactInformation.aasx",
    "IDTA 02002-1-0_Template_ContactInformation.json",
    "IDTA 02023 _Template_CarbonFootprint.aasx",
    "IDTA 02058-1-0_Template_AIDataset.json",
    "TestPackage.aasx",
]
FORMATS = ["json", "xml", "aasx"]


def sortUnordered(data):
    """basyx keeps value lists in a set: their order changes on every save."""
    if isinstance(data, dict):
        for key, value in data.items():
            sortUnordered(value)
            if key == "valueReferencePairs":
                value.sort(key=lambda pair: json.dumps(pair, sort_keys=True))
    elif isinstance(data, list):
        for value in data:
            sortUnordered(value)


def canonical(pack, withFiles: bool = True) -> dict:
    """Package content as comparable data: AAS JSON plus supplementary files."""
    from basyx.aas.adapter.json import write_aas_json_file

    buffer = io.StringIO()
    write_aas_json_file(buffer, pack.objStore, sort_keys=True)
    content = json.loads(buffer.getvalue())
    for objects in content.values():
        objects.sort(key=lambda obj: obj.get("id", ""))
    sortUnordered(content)
    if not withFiles:  # JSON and XML files cannot hold supplementary files
        return {"aas": content}
    files = {}
    for name in pack.fileStore:
        data = io.BytesIO()
        pack.fileStore.write_file(name, data)
        files[name] = data.getvalue()
    return {"aas": content, "files": files}


def saveAndReload(pack, tmpPath: Path, fmt: str):
    from aas_editor.package import Package

    out = tmpPath / f"out.{fmt}"
    pack.write(out)
    return Package(out)


def openInPackTree(file: Path) -> Tuple[object, QModelIndex]:
    """Open the file as the GUI does; return the pack tree model and pack index."""
    from aas_editor.package import Package
    from aas_editor_test.test_performance import newPackTreeView

    view = newPackTreeView()
    view.add_pack_to_tree(Package(file))
    model = view.sourceModel()
    model.keepView = view  # the view owns nothing we need, but keep it alive
    return model, model.index(0, 0)


def findIndex(model, predicate: Callable[[QModelIndex], bool]) -> QModelIndex:
    for index in model.iterItems():
        if predicate(index):
            return index
    raise LookupError("No matching item")


def topLevelStringProperty(pack) -> Optional[Tuple[str, str]]:
    """(submodel id, property id_short) of a string property directly in a submodel."""
    from basyx.aas import model

    for submodel in sorted(pack.submodels, key=lambda sm: sm.id):
        for element in sorted(submodel.submodel_element, key=lambda e: e.id_short):
            if isinstance(element, model.Property) \
                    and element.value_type is model.datatypes.String:
                return submodel.id, element.id_short
    return None


def expectedPackage(file: Path, change: Callable[[object], None], fmt: str):
    from aas_editor.package import Package

    pack = Package(file)
    change(pack)
    return canonical(pack, withFiles=fmt == "aasx")


def savedPackage(pack, fmt: str) -> dict:
    return canonical(pack, withFiles=fmt == "aasx")


@pytest.mark.parametrize("fmt", FORMATS)
@pytest.mark.parametrize("sample", SAMPLES)
def test_save_without_changes_keeps_content(qapp, tmp_path, sample, fmt) -> None:
    from aas_editor.settings.app_settings import PACKAGE_ROLE

    file = TEST_FILES_DIR / sample
    model, packIndex = openInPackTree(file)
    for _ in model.iterItems():  # build every tree item, as expandAll would
        pass
    saved = saveAndReload(packIndex.data(PACKAGE_ROLE), tmp_path, fmt)
    assert savedPackage(saved, fmt) == expectedPackage(file, lambda pack: None, fmt)


def samplesWithStringProperty():
    from aas_editor.package import Package

    return [s for s in SAMPLES if topLevelStringProperty(Package(TEST_FILES_DIR / s))]


@pytest.fixture(scope="module")
def editableSample(qapp) -> Path:
    samples = samplesWithStringProperty()
    assert samples, "No sample with a top-level string property"
    return TEST_FILES_DIR / samples[0]


def propertyFinder(pack):
    smId, idShort = topLevelStringProperty(pack)

    def find(p):
        return p.objStore.get_item(smId).get_referable(idShort)

    return smId, idShort, find


@pytest.mark.parametrize("fmt", FORMATS)
def test_edit_value_in_item_tab_is_saved(qapp, tmp_path, editableSample, fmt) -> None:
    from aas_editor.models import DetailedInfoTable
    from aas_editor.settings.app_settings import NAME_ROLE, OBJECT_ROLE, PACKAGE_ROLE

    model, packIndex = openInPackTree(editableSample)
    pack = packIndex.data(PACKAGE_ROLE)
    _, idShort, find = propertyFinder(pack)
    prop = find(pack)
    propIndex = findIndex(model, lambda i: i.data(OBJECT_ROLE) is prop)

    detailed = DetailedInfoTable(propIndex)  # the item tab's model
    valueIndex = findIndex(detailed, lambda i: i.data(NAME_ROLE) == "value")
    assert detailed.setData(valueIndex, "edited value", Qt.ItemDataRole.EditRole)

    def change(p):
        find(p).value = "edited value"

    saved = saveAndReload(pack, tmp_path, fmt)
    assert find(saved).value == "edited value"
    assert savedPackage(saved, fmt) == expectedPackage(editableSample, change, fmt)


def newProperty():
    from basyx.aas import model

    return model.Property("AddedByTest", model.datatypes.String, value="new")


@pytest.mark.parametrize("fmt", FORMATS)
def test_add_property_is_saved(qapp, tmp_path, editableSample, fmt) -> None:
    from aas_editor.settings.app_settings import OBJECT_ROLE, PACKAGE_ROLE

    model, packIndex = openInPackTree(editableSample)
    pack = packIndex.data(PACKAGE_ROLE)
    smId, _, _ = propertyFinder(pack)
    submodel = pack.objStore.get_item(smId)
    submodelIndex = findIndex(model, lambda i: i.data(OBJECT_ROLE) is submodel)
    model.addItem(newProperty(), submodelIndex)

    def change(p):
        p.objStore.get_item(smId).submodel_element.add(newProperty())

    saved = saveAndReload(pack, tmp_path, fmt)
    assert savedPackage(saved, fmt) == expectedPackage(editableSample, change, fmt)


@pytest.mark.parametrize("fmt", FORMATS)
def test_delete_property_is_saved(qapp, tmp_path, editableSample, fmt) -> None:
    from aas_editor.settings.app_settings import (CLEAR_ROW_ROLE, NOT_GIVEN, OBJECT_ROLE,
                                                  PACKAGE_ROLE)

    model, packIndex = openInPackTree(editableSample)
    pack = packIndex.data(PACKAGE_ROLE)
    smId, idShort, find = propertyFinder(pack)
    prop = find(pack)
    propIndex = findIndex(model, lambda i: i.data(OBJECT_ROLE) is prop)
    assert model.setData(propIndex, NOT_GIVEN, CLEAR_ROW_ROLE)

    def change(p):
        submodel = p.objStore.get_item(smId)
        submodel.submodel_element.remove(submodel.get_referable(idShort))

    saved = saveAndReload(pack, tmp_path, fmt)
    assert savedPackage(saved, fmt) == expectedPackage(editableSample, change, fmt)


def test_undo_edit_add_delete_restores_original(qapp, tmp_path, editableSample) -> None:
    from aas_editor.models import DetailedInfoTable
    from aas_editor.settings.app_settings import (CLEAR_ROW_ROLE, NAME_ROLE, NOT_GIVEN,
                                                  OBJECT_ROLE, PACKAGE_ROLE, UNDO_ROLE)

    model, packIndex = openInPackTree(editableSample)
    pack = packIndex.data(PACKAGE_ROLE)
    smId, idShort, find = propertyFinder(pack)
    prop = find(pack)
    submodel = pack.objStore.get_item(smId)

    detailed = DetailedInfoTable(findIndex(model, lambda i: i.data(OBJECT_ROLE) is prop))
    valueIndex = findIndex(detailed, lambda i: i.data(NAME_ROLE) == "value")
    assert detailed.setData(valueIndex, "edited value", Qt.ItemDataRole.EditRole)
    assert detailed.setData(QModelIndex(), NOT_GIVEN, UNDO_ROLE)

    submodelIndex = findIndex(model, lambda i: i.data(OBJECT_ROLE) is submodel)
    model.addItem(newProperty(), submodelIndex)
    assert model.setData(QModelIndex(), NOT_GIVEN, UNDO_ROLE)

    propIndex = findIndex(model, lambda i: i.data(OBJECT_ROLE) is prop)
    assert model.setData(propIndex, NOT_GIVEN, CLEAR_ROW_ROLE)
    assert model.setData(QModelIndex(), NOT_GIVEN, UNDO_ROLE)

    saved = saveAndReload(pack, tmp_path, "aasx")
    # Undo of a delete appends the element (see the xfail test below)
    assert sortedElements(savedPackage(saved, "aasx")) == \
        sortedElements(expectedPackage(editableSample, lambda p: None, "aasx"))


def sortedElements(content: dict) -> dict:
    for submodel in content["aas"].get("submodels", []):
        submodel.get("submodelElements", []).sort(key=lambda e: e["idShort"])
    return content


@pytest.mark.xfail(strict=True, reason="undo of delete re-adds the element at the end")
def test_undo_delete_keeps_element_position(qapp, tmp_path, editableSample) -> None:
    from aas_editor.settings.app_settings import (CLEAR_ROW_ROLE, NOT_GIVEN, OBJECT_ROLE,
                                                  PACKAGE_ROLE, UNDO_ROLE)

    model, packIndex = openInPackTree(editableSample)
    pack = packIndex.data(PACKAGE_ROLE)
    _, _, find = propertyFinder(pack)
    prop = find(pack)
    propIndex = findIndex(model, lambda i: i.data(OBJECT_ROLE) is prop)
    assert model.setData(propIndex, NOT_GIVEN, CLEAR_ROW_ROLE)
    assert model.setData(QModelIndex(), NOT_GIVEN, UNDO_ROLE)

    saved = saveAndReload(pack, tmp_path, "aasx")
    assert savedPackage(saved, "aasx") == expectedPackage(editableSample, lambda p: None, "aasx")
