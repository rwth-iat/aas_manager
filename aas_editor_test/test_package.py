import io
from pathlib import Path

import pytest
from basyx.aas.adapter.aasx import DictSupplementaryFileContainer
from basyx.aas.model import AssetAdministrationShell, ConceptDescription, Submodel

from aas_editor.package import Package, StoredFile


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

class TestPackageLoad:
    def test_load_aasx(self, qapp: object, aasx_file: Path) -> None:
        pkg = Package(aasx_file)
        assert pkg.file == aasx_file.absolute()

    def test_load_json(self, qapp: object, json_file: Path) -> None:
        pkg = Package(json_file)
        assert pkg.file == json_file.absolute()

    def test_empty_package(self, qapp: object) -> None:
        pkg = Package()
        assert pkg.numOfShells == 0
        assert pkg.numOfSubmodels == 0
        assert pkg.numOfConceptDescriptions == 0

    def test_wrong_extension_raises(self, qapp: object, tmp_path: Path) -> None:
        dummy = tmp_path / "file.txt"
        dummy.write_text("not an aas file")
        with pytest.raises(TypeError):
            Package(dummy)

    def test_nonexistent_file_raises(self, qapp: object, tmp_path: Path) -> None:
        with pytest.raises(Exception):
            Package(tmp_path / "does_not_exist.aasx")


# ---------------------------------------------------------------------------
# Object-store access
# ---------------------------------------------------------------------------

class TestPackageContent:
    def test_shells_are_aas_type(self, qapp: object, aasx_file: Path) -> None:
        pkg = Package(aasx_file)
        for shell in pkg.shells:
            assert isinstance(shell, AssetAdministrationShell)

    def test_submodels_are_submodel_type(self, qapp: object, aasx_file: Path) -> None:
        pkg = Package(aasx_file)
        for submodel in pkg.submodels:
            assert isinstance(submodel, Submodel)

    def test_concept_descriptions_type(self, qapp: object, aasx_file: Path) -> None:
        pkg = Package(aasx_file)
        for cd in pkg.concept_descriptions:
            assert isinstance(cd, ConceptDescription)

    def test_count_properties_match_iteration(self, qapp: object, aasx_file: Path) -> None:
        pkg = Package(aasx_file)
        assert pkg.numOfShells == len(list(pkg.shells))
        assert pkg.numOfSubmodels == len(list(pkg.submodels))
        assert pkg.numOfConceptDescriptions == len(list(pkg.concept_descriptions))

    def test_name_matches_filename(self, qapp: object, aasx_file: Path) -> None:
        pkg = Package(aasx_file)
        assert pkg.name == aasx_file.name


# ---------------------------------------------------------------------------
# Modify (add / discard)
# ---------------------------------------------------------------------------

class TestPackageModify:
    def test_add_submodel(self, qapp: object) -> None:
        pkg = Package()
        submodel = Submodel(id_="https://example.com/test-submodel")
        pkg.add(submodel)
        assert pkg.numOfSubmodels == 1

    def test_discard_submodel(self, qapp: object, aasx_file: Path) -> None:
        pkg = Package(aasx_file)
        initial_count = pkg.numOfSubmodels
        submodels = list(pkg.submodels)
        if not submodels:
            pytest.skip("TestPackage.aasx contains no submodels")
        pkg.discard(submodels[0])
        assert pkg.numOfSubmodels == initial_count - 1


# ---------------------------------------------------------------------------
# Write round-trips
# ---------------------------------------------------------------------------

class TestPackageWrite:
    def _roundtrip(self, qapp: object, aasx_file: Path, tmp_path: Path, ext: str) -> None:
        src = Package(aasx_file)
        shells_count = src.numOfShells
        submodels_count = src.numOfSubmodels
        cds_count = src.numOfConceptDescriptions

        out_file = tmp_path / f"out.{ext}"
        src.write(out_file)

        reloaded = Package(out_file)
        assert reloaded.numOfShells == shells_count
        assert reloaded.numOfSubmodels == submodels_count
        assert reloaded.numOfConceptDescriptions == cds_count

    def test_write_json_roundtrip(self, qapp: object, aasx_file: Path, tmp_path: Path) -> None:
        self._roundtrip(qapp, aasx_file, tmp_path, "json")

    def test_write_xml_roundtrip(self, qapp: object, aasx_file: Path, tmp_path: Path) -> None:
        self._roundtrip(qapp, aasx_file, tmp_path, "xml")

    def test_write_aasx_roundtrip(self, qapp: object, aasx_file: Path, tmp_path: Path) -> None:
        self._roundtrip(qapp, aasx_file, tmp_path, "aasx")

    def test_write_wrong_extension_raises(self, qapp: object, aasx_file: Path, tmp_path: Path) -> None:
        pkg = Package(aasx_file)
        with pytest.raises(TypeError):
            pkg.write(tmp_path / "out.txt")


# ---------------------------------------------------------------------------
# StoredFile
# ---------------------------------------------------------------------------

class TestStoredFile:
    def test_not_saved_in_store_by_default(self, tmp_path: Path) -> None:
        dummy = tmp_path / "image.png"
        dummy.write_bytes(b"\x89PNG")
        sf = StoredFile(filePath=str(dummy))
        assert sf.savedInStore() is False

    def test_saved_in_store_with_filestore(self) -> None:
        store = DictSupplementaryFileContainer()
        store.add_file("/image.png", file=io.BytesIO(b"\x89PNG"), content_type="image/png")
        sf = StoredFile(name="/image.png", fileStore=store)
        assert sf.savedInStore() is True

    def test_mime_type_guessing_png(self, tmp_path: Path) -> None:
        dummy = tmp_path / "image.png"
        dummy.write_bytes(b"\x89PNG")
        sf = StoredFile(filePath=str(dummy))
        assert sf.mime_type == "image/png"

    def test_mime_type_unknown_fallback(self, tmp_path: Path) -> None:
        dummy = tmp_path / "file.unknownextension123"
        dummy.write_bytes(b"binary")
        sf = StoredFile(filePath=str(dummy))
        assert sf.mime_type == "application/octet-stream"

    def test_name_setter_rejects_empty_string(self, tmp_path: Path) -> None:
        dummy = tmp_path / "image.png"
        dummy.write_bytes(b"\x89PNG")
        sf = StoredFile(filePath=str(dummy))
        with pytest.raises(TypeError):
            sf.name = ""

    def test_setfilestore_rejects_wrong_type(self) -> None:
        with pytest.raises(TypeError):
            StoredFile(name="test", fileStore="not-a-filestore")
