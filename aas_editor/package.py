import io
from datetime import datetime
from pathlib import Path
from typing import Union, Type, Iterable

import pyecma376_2
from aas.adapter import aasx
from aas.adapter.aasx import DictSupplementaryFileContainer
from aas.model import AssetAdministrationShell, Asset, Submodel, ConceptDescription, \
    DictObjectStore, Key

from aas_editor.settings import ADD_ACT_AAS_TXT, ADD_TYPE, DEFAULT_COMPLETIONS


class Package:
    ATTRS_INFO = {
        "shells": {
            ADD_ACT_AAS_TXT: "Add shell",
            ADD_TYPE: AssetAdministrationShell,
        },
        "assets": {
            ADD_ACT_AAS_TXT: "Add asset",
            ADD_TYPE: Asset,
        },
        "submodels": {
            ADD_ACT_AAS_TXT: "Add submodel",
            ADD_TYPE: Submodel,
        },
        "concept_descriptions": {
            ADD_ACT_AAS_TXT: "Add concept description",
            ADD_TYPE: ConceptDescription,
        },
        "others": {
            ADD_ACT_AAS_TXT: "",
        },
        "fileStore": {
            ADD_ACT_AAS_TXT: "Add file",
        },
    }

    def __init__(self, file: Union[str, Path] = ""):
        """:raise TypeError if file has wrong file type"""
        self.objStore = DictObjectStore()
        self.fileStore = DictSupplementaryFileContainer()
        self.file = file
        if file:
            self._read()
        for obj in self.objStore:
            DEFAULT_COMPLETIONS[Key]["value"].append(obj.identification.id)
        self._changed = False

    @classmethod
    def packViewAttrs(cls):
        return tuple(cls.ATTRS_INFO.keys())

    @classmethod
    def addableAttrs(cls):
        return tuple(cls.ATTRS_INFO.keys())

    @classmethod
    def addActText(cls, attrName: str) -> str:
        return cls.ATTRS_INFO.get(attrName, {}).get(
            ADD_ACT_AAS_TXT, "")

    @classmethod
    def addType(cls, attrName: str) -> Type:
        return cls.ATTRS_INFO.get(attrName, {}).get(ADD_TYPE, None)

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        self._file = Path(file).absolute()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.file.as_posix()

    def _read(self):
        fileType = self.file.suffix.lower().strip()
        if fileType == ".xml":
            self.objStore = aasx.read_aas_xml_file(self.file.as_posix())
        elif fileType == ".json":
            with open(self.file, "r") as f:  # TODO change if aas changes
                self.objStore = aasx.read_aas_json_file(f)
        elif fileType == ".aasx":
            reader = aasx.AASXReader(self.file.as_posix())
            reader.read_into(self.objStore, self.fileStore)
        else:
            raise TypeError("Wrong file type:", self.file.suffix)

    def write(self, file: str = None):
        if file:
            self.file: Path = file

        fileType = self.file.suffix.lower().strip()
        if fileType == ".xml":
            aasx.write_aas_xml_file(self.file.as_posix(), self.objStore)
        elif fileType == ".json":
            aasx.write_aas_json_file(self.file.as_posix(), self.objStore)
        elif fileType == ".aasx":
            # todo ask user if save in xml, json or both
            #  writer.write_aas_objects("/aasx/data.json" if args.json else "/aasx/data.xml",
            #  [obj.identification for obj in self.objStore], self.objStore, self.fielSotre, write_json=args.json)
            with aasx.AASXWriter(self.file.as_posix()) as writer:
                writer.write_aas(self.objStore, self.fileStore) #FIXME
                # Create OPC/AASX core properties
                cp = pyecma376_2.OPCCoreProperties()
                cp.created = datetime.now()
                from aas_editor.settings.app_settings import AAS_CREATOR
                cp.creator = AAS_CREATOR
                writer.write_core_properties(cp)
        else:
            raise TypeError("Wrong file type:", self.file.suffix)

    @property
    def name(self):
        return self.file.name

    @name.setter
    def name(self, name):
        self.file = self.file.parent.joinpath(name)

    @property
    def shells(self) -> Iterable[AssetAdministrationShell]:
        for obj in self.objStore:
            if isinstance(obj, AssetAdministrationShell):
                yield obj

    @property
    def assets(self) -> Iterable[Asset]:
        for obj in self.objStore:
            if isinstance(obj, Asset):
                yield obj

    @property
    def submodels(self) -> Iterable[Submodel]:
        for obj in self.objStore:
            if isinstance(obj, Submodel):
                yield obj

    @property
    def concept_descriptions(self) -> Iterable[ConceptDescription]:
        for obj in self.objStore:
            if isinstance(obj, ConceptDescription):
                yield obj

    @property
    def others(self):
        for obj in self.objStore:
            if not isinstance(obj,
                              (AssetAdministrationShell, Asset, Submodel, ConceptDescription)):
                yield obj

    @property
    def files(self):
        for file in self.fileStore:
            yield file

    def add(self, obj):
        self.objStore.add(obj)

    def discard(self, obj):
        self.objStore.discard(obj)

    @property
    def numOfShells(self) -> int:
        return len(tuple(self.shells))

    @property
    def numOfAssets(self) -> int:
        return len(tuple(self.assets))

    @property
    def numOfSubmodels(self) -> int:
        return len(tuple(self.submodels))

    @property
    def numOfConceptDescriptions(self) -> int:
        return len(tuple(self.concept_descriptions))


class StoredFile:
    def __init__(self, name: str, fileStore: DictSupplementaryFileContainer):
        self._fileStore = fileStore
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def contentType(self) -> str:
        return self._fileStore.get_content_type(self.name)

    def fileContent(self) -> io.BytesIO:
        file_content = io.BytesIO()
        self._fileStore.write_file(self.name, file_content)
        return file_content
