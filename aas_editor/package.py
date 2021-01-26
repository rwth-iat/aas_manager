import io
from datetime import datetime
from pathlib import Path
from typing import Union, Iterable, Optional
import mimetypes

import pyecma376_2
from aas.adapter import aasx
from aas.adapter.aasx import DictSupplementaryFileContainer
from aas.model import AssetAdministrationShell, Asset, Submodel, ConceptDescription, \
    DictObjectStore, Key

from aas_editor.settings import DEFAULT_COMPLETIONS
from aas_editor.utils.util_classes import ClassesInfo


class Package:
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
    def addableAttrs(cls):
        return ClassesInfo.packViewAttrs(cls)

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
                for obj in self.objStore:
                    if isinstance(obj, AssetAdministrationShell):
                        aas_id = obj.identification
                        break
                writer.write_aas(aas_id, self.objStore, self.fileStore) #FIXME
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
        if isinstance(obj, StoredFile):
            newName = self.fileStore.add_file(name=obj.name, file=obj.file(), content_type=obj.mime_type)
            obj.setFileStore(newName, self.fileStore)
        else:
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
    def __init__(self, name: Optional[str] = None, fileStore: Optional[DictSupplementaryFileContainer] = None,
                 filePath: Optional[str] = None):
        if filePath:
            self._filePath = Path(filePath).absolute()
        else:
            self._filePath = filePath

        self.setFileStore(name, fileStore)

    def savedInStore(self) -> bool:
        return True if isinstance(self._fileStore, DictSupplementaryFileContainer) else False

    @property
    def name(self):
        if self.savedInStore():
            return self._name
        else:
            return f"/{self._filePath.name}"

    @property
    def mime_type(self) -> str:
        if self.savedInStore():
            return self._fileStore.get_content_type(self.name)
        else:
            mimetypes.init()
            mime_type = mimetypes.guess_type(self._filePath)[0]
            if mime_type is None:
                mime_type = "application/octet-stream"
            return mime_type

    @property
    def value(self) -> bytes:
        return self.file().getvalue()

    def file(self) -> io.BytesIO:
        if self.savedInStore():
            file_content = io.BytesIO()
            self._fileStore.write_file(self.name, file_content)
        else:
            with open(self._filePath, "rb") as f:
                file_content = io.BytesIO(f.read())
        return file_content

    def setFileStore(self, name: str, fileStore: DictSupplementaryFileContainer):
        if name is None or isinstance(name, str):
            self._name = name
        else:
            raise TypeError("arg 1 must be of type str or None")

        if fileStore is None or isinstance(fileStore, DictSupplementaryFileContainer):
            self._fileStore = fileStore
        else:
            raise TypeError("arg 2 must be of type DictSupplementaryFileContainer or None")
