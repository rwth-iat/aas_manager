from datetime import datetime
from os import PathLike
from typing import NamedTuple, Any, Union, IO

import pyecma376_2
from aas.adapter import aasx
from aas.adapter.aasx import DictSupplementaryFileContainer
from aas.model import DictObjectStore, AssetAdministrationShell, Asset, Submodel, \
    ConceptDescription
from pathlib import Path

from aas_editor.settings import AAS_CREATOR


class Package:
    def __init__(self, file: str):
        self.file = Path(file).absolute()
        self.objStore = DictObjectStore()
        self.fileStore = DictSupplementaryFileContainer()
        fileType = self.file.suffix.lower().strip()
        if fileType == ".xml":
            self.objStore = aasx.read_aas_xml_file(self.file.as_posix())
        elif fileType == ".json":
            with open(file, "r") as f:  # TODO change if aas changes
                self.objStore = aasx.read_aas_json_file(f)
        elif fileType == ".aasx":
            reader = aasx.AASXReader(self.file.as_posix())
            reader.read_into(self.objStore, self.fileStore)
        else:
            raise TypeError("File type is not supportable:", self.file.suffix)

    def write(self, file=None):
        if file is None:
            file = self.file
            fileType = self.file.suffix.lower().strip()
            if fileType == ".xml":
                aasx.write_aas_xml_file(file.as_posix(), self.objStore)
            elif fileType == ".json":
                aasx.write_aas_json_file(file.as_posix(), self.objStore)
            elif fileType == ".aasx":
                with aasx.AASXWriter(file.as_posix()) as writer:
                    writer.write_aas(self.objStore, self.fileStore) #FIXME
                    # Create OPC/AASX core properties
                    cp = pyecma376_2.OPCCoreProperties()
                    cp.created = datetime.now()
                    cp.creator = AAS_CREATOR
                    writer.write_core_properties(cp)

    @property
    def name(self):
        return self.file.name

    @name.setter
    def name(self, name):
        self.file = self.file.parent.joinpath(name)

    @property
    def shells(self):
        for obj in self.objStore:
            if isinstance(obj, AssetAdministrationShell):
                yield obj

    @property
    def assets(self):
        for obj in self.objStore:
            if isinstance(obj, Asset):
                yield obj

    @property
    def submodels(self):
        for obj in self.objStore:
            if isinstance(obj, Submodel):
                yield obj

    @property
    def concept_descriptions(self):
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

    @property
    def numOfShells(self):
        return len(tuple(self.shells))

    @property
    def numOfAssets(self):
        return len(tuple(self.assets))

    @property
    def numOfSubmodels(self):
        return len(tuple(self.submodels))

    @property
    def numOfConceptDescriptions(self):
        return len(tuple(self.concept_descriptions))


DictItem = NamedTuple("DictItem", key=Any, value=Any)
