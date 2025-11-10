#  Copyright (C) 2021  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/

import io
from datetime import datetime
from pathlib import Path
from typing import Union, Iterable, Optional
import mimetypes

import pyecma376_2
from basyx.aas.adapter.aasx import DictSupplementaryFileContainer, AASXReader, AASXWriter
from basyx.aas.adapter.json import read_aas_json_file, write_aas_json_file
from basyx.aas.adapter.xml import read_aas_xml_file, write_aas_xml_file
from basyx.aas.model import AssetAdministrationShell, Submodel, ConceptDescription, \
    SetObjectStore, Key, ModelReference

from aas_editor.settings import DEFAULT_COMPLETIONS, AppSettings
from aas_editor.utils.util_classes import ClassesInfo


class Package:
    def __init__(self, file: Union[str, Path] = "", failsafe=False):
        """:raise TypeError if file has wrong file type"""
        self.objStore = SetObjectStore()
        self.fileStore = DictSupplementaryFileContainer()
        self.file = file
        if file:
            self._read(failsafe)
        for obj in self.objStore:
            DEFAULT_COMPLETIONS[Key]["value"].append(obj.id)
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

    @property
    def writeJsonInAasx(self):
        return AppSettings.WRITE_JSON_IN_AASX.value()

    @property
    def writePrettyJson(self):
        return AppSettings.WRITE_PRETTY_JSON.value()

    @property
    def allSubmodelRefsToAas(self):
        return AppSettings.ALL_SUBMODEL_REFS_TO_AAS.value()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.file.as_posix()

    def _read(self, failsafe):
        fileType = self.file.suffix.lower().strip()
        if fileType == ".xml":
            # The file must be opened in binary mode! The XML writer will handle
            # character encoding internally.
            with open(self.file, 'rb') as xml_file:
                self.objStore = read_aas_xml_file(xml_file, failsafe=failsafe)
        elif fileType == ".json":
            # Using 'utf-8-sig' is recommended to handle unicode Byte Order
            # Marks (BOM) correctly.
            with open(self.file, "r", encoding='utf-8-sig') as f:
                self.objStore = read_aas_json_file(f, failsafe=failsafe)
        elif fileType == ".aasx":
            reader = AASXReader(self.file.as_posix())
            reader.read_into(self.objStore, self.fileStore, failsafe=failsafe)
        else:
            raise TypeError("Wrong file type:", self.file.suffix)

    def write(self, file: str = None):
        if self.allSubmodelRefsToAas:
            self.all_submodels_to_aas()
        if file:
            self.file: Path = file

        fileType = self.file.suffix.lower().strip()
        if fileType == ".xml":
            # The file must be opened in binary mode! The XML writer will handle
            # character encoding internally.
            with open(self.file.as_posix(), 'wb') as xml_file:
                write_aas_xml_file(xml_file, self.objStore)
        elif fileType == ".json":
            with open(self.file.as_posix(), "w", encoding='utf-8') as fileIO:
                indent = 2 if self.writePrettyJson else None
                write_aas_json_file(fileIO, self.objStore, indent=indent)

        elif fileType == ".aasx":
            with AASXWriter(self.file.as_posix()) as writer:
                writer.write_all_aas_objects("/aasx/data.{}".format("json" if self.writeJsonInAasx else "xml"),
                                             self.objStore, self.fileStore, self.writeJsonInAasx)
        else:
            raise TypeError("Wrong file type:", self.file.suffix)

    def all_submodels_to_aas(self):
        """Add references of all existing submodels to submodel attribute of existing AAS."""
        #TODO: fix if pyi40aas changes
        for shell in self.shells:
            for submodel in self.submodels:
                reference = ModelReference.from_referable(submodel)
                if shell.submodel is None:
                    shell.submodel = set()
                shell.submodel.add(reference)
            break

    @property
    def name(self):
        return self.file.name

    @name.setter
    def name(self, name):
        self.file = self.file.parent.joinpath(name)

    @property
    def shells(self) -> Iterable[AssetAdministrationShell]:
        return self._iter_objects(AssetAdministrationShell)

    @property
    def submodels(self) -> Iterable[Submodel]:
        return self._iter_objects(Submodel)

    @property
    def concept_descriptions(self) -> Iterable[ConceptDescription]:
        return self._iter_objects(ConceptDescription)

    # @property
    # def others(self):
    #     for obj in self.objStore:
    #         if not isinstance(obj,
    #                           (AssetAdministrationShell, Asset, Submodel, ConceptDescription)):
    #             yield obj

    def _iter_objects(self, objtype):
        for obj in self.objStore:
            if isinstance(obj, objtype):
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

    @name.setter
    def name(self, new_name: str):
        if not isinstance(new_name, str) or new_name.strip() == "":
            raise TypeError("new name must be a non-empty string")

        if self.savedInStore():
            new_stored_name = self._fileStore.rename_file(self.name, new_name)
            self._name = new_stored_name
        else:
            if self._filePath is None:
                raise ValueError("No local file path available to rename")
            new_path = self._filePath.parent.joinpath(new_name)
            if new_path.exists():
                raise FileExistsError(f"Target file already exists: {new_path}")
            self._filePath.rename(new_path)
            self._filePath = new_path

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
