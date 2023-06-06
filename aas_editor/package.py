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

import basyx
import pyecma376_2
from basyx.aas.adapter.aasx import DictSupplementaryFileContainer, AASXReader, AASXWriter
from basyx.aas.adapter.json import read_aas_json_file, write_aas_json_file
from basyx.aas.adapter.xml import read_aas_xml_file, write_aas_xml_file
from basyx.aas.model import AssetAdministrationShell, Asset, Submodel, ConceptDescription, \
    DictObjectStore, Key, AASReference, ConceptDictionary, AbstractObjectStore

from aas_editor.settings import DEFAULT_COMPLETIONS, AppSettings
from aas_editor.utils.util_classes import ClassesInfo

from abc import ABC, abstractmethod

class BasePackage(ABC):
    # objStore: AbstractObjectStore
    def __init__(self, source: Union[str, Path] = "", failsafe=False):
        """raise TypeError if file has wrong file type"""
        # self.objStore = DictObjectStore()
        # self.fileStore = DictSupplementaryFileContainer()
        self.source = source
        if source:
            self._read(failsafe)
        # for obj in self.objStore:
        #     DEFAULT_COMPLETIONS[Key]["value"].append(obj.identification.id)
        self._changed = False

    @classmethod
    def addableAttrs(cls):
        return ClassesInfo.packViewAttrs(cls)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = Path(source).absolute()

    @property
    def writeJsonInAasx(self):
        return AppSettings.WRITE_JSON_IN_AASX.value()

    @property
    def writePrettyJson(self):
        return AppSettings.WRITE_PRETTY_JSON.value()

    @property
    def submodelSplitParts(self):
        return AppSettings.SUBMODEL_SPLIT_PARTS.value()

    @property
    def allSubmodelRefsToAas(self):
        return AppSettings.ALL_SUBMODEL_REFS_TO_AAS.value()

    @property
    def allCDRefsToAas(self):
        return AppSettings.ALL_CD_REFS_TO_AAS.value()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.source.as_posix()

    @abstractmethod
    def _read(self, failsafe):
        pass

    @abstractmethod
    def _update_objstore(self):
        pass

    @abstractmethod
    def write(self, source: str = None):
        pass

    def all_submodels_to_aas(self):
        """Add references of all existing submodels to submodel attribute of existing AAS."""
        #TODO: fix if pyi40aas changes
        for shell in self.shells:
            for submodel in self.submodels:
                reference = AASReference.from_referable(submodel)
                if shell.submodel is None:
                    shell.submodel = set()
                shell.submodel.add(reference)
            break

    def all_concept_descriptions_to_aas(self):
        """Add references of all existing CD to concept dictionary in existing AAS."""
        #FIXME: save all concept descriptions to AASX or JSON or XML even if they are not referenced in ConceptDict
        for shell in self.shells:
            if shell.concept_dictionary and len(shell.concept_dictionary):
                for i in shell.concept_dictionary:
                    dictionary = i
                    break
            else:
                idshort = "AutomaticallyGeneratedCD"
                dictionary = ConceptDictionary(idshort)
                try:
                    shell.concept_dictionary.add(dictionary)
                except KeyError:
                    shell.concept_dictionary.discard(shell.concept_dictionary.get_referable(idshort))
                    shell.concept_dictionary.add(dictionary)

            for cd in self.concept_descriptions:
                reference = AASReference.from_referable(cd)
                dictionary.concept_description.add(reference)
            break

    @property
    def name(self):
        return self.source.name

    @name.setter
    def name(self, name):
        self.source = self.source.parent.joinpath(name)

    @property
    def shells(self) -> Iterable[AssetAdministrationShell]:
        return self._iter_objects(AssetAdministrationShell)

    @property
    def assets(self) -> Iterable[Asset]:
        return self._iter_objects(Asset)

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

    @abstractmethod
    def _iter_objects(self, objtype):
        pass

    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def discard(self, obj):
        pass

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


class LocalPackage(BasePackage):
    def __init__(self, source: Union[str, Path] = "", failsafe=False):
        self.objStore = DictObjectStore()
        self.fileStore = DictSupplementaryFileContainer()
        for obj in self.objStore:
            DEFAULT_COMPLETIONS[Key]["value"].append(obj.identification.id)
        super().__init__(source, failsafe)

    def _read(self, failsafe):
        fileType = self.source.suffix.lower().strip()
        if fileType == ".xml":
            self.objStore = read_aas_xml_file(self.source.as_posix(), failsafe=failsafe)
        elif fileType == ".json":
            with open(self.source, "r") as f:  # TODO change if aas changes
                self.objStore = read_aas_json_file(f, failsafe=failsafe)
        elif fileType == ".aasx":
            reader = AASXReader(self.source.as_posix())
            reader.read_into(self.objStore, self.fileStore)
        else:
            raise TypeError("Wrong file type:", self.source.suffix)

    def _update_objstore(self):
        old_identifiers = list(self.objStore._backend.keys())
        for i in old_identifiers:
            obj = self.objStore.get_identifiable(i)
            if i != obj.identification:
                self.objStore._backend[obj.identification] = obj
                del self.objStore._backend[i]

    def write(self, source: str = None):
        self._update_objstore()

        if self.allSubmodelRefsToAas:
            self.all_submodels_to_aas()
        if self.allCDRefsToAas:
            self.all_concept_descriptions_to_aas()
        if source:
            self.source: Path = source
            # TODO: Check if dir for file existing

        fileType = self.source.suffix.lower().strip()
        if fileType == ".xml":  # FIXME: if file in write_aas_xml_file() changes
            # with open(self.file.as_posix(), "w") as fileIO:
            write_aas_xml_file(self.source.as_posix(), self.objStore)
        elif fileType == ".json":  # FIXME: if file in write_aas_xml_file() changes
            with open(self.source.as_posix(), "w") as fileIO:
                indent = 2 if self.writePrettyJson else None
                write_aas_json_file(fileIO, self.objStore, indent=indent)

        elif fileType == ".aasx":
            with AASXWriter(self.source.as_posix()) as writer:
                aas_ids = []
                for obj in self.objStore:
                    if isinstance(obj, AssetAdministrationShell):
                        aas_ids.append(obj.identification)
                for aas_id in aas_ids:
                    writer.write_aas(aas_id, self.objStore, self.fileStore,
                                     write_json=self.writeJsonInAasx,
                                     submodel_split_parts=self.submodelSplitParts)
                # Create OPC/AASX core properties
                cp = pyecma376_2.OPCCoreProperties()
                cp.created = datetime.now()
                from aas_editor.settings.app_settings import AAS_CREATOR
                cp.creator = AAS_CREATOR
                writer.write_core_properties(cp)
        else:
            raise TypeError("Wrong file type:", self.source.suffix)

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


class WebPackage(BasePackage):
    def __init__(self, source: Union[str, Path] = "", url: str = "", database: str = "", failsafe=False):
        # TODO: By creating a WebPackage a server will be connected and objStore for managing oblects created.
        self.url = url
        self.database = database
        self.objStore = basyx.aas.backend.couchdb.CouchDBObjectStore(self.url, self.database)
        # for obj in self.objStore:
        #     DEFAULT_COMPLETIONS[Key]["value"].append(obj.identification.id)
        super().__init__(source, failsafe)

    def _read(self, failsafe):
        # This method will update object from server
        pass

    def _update_objstore(self):
        pass

    def write(self, source: str = None):
        # Commit all referable objects...?
        pass

    def _iter_objects(self, objtype):
        for obj in self.objStore:
            if isinstance(obj, objtype):
                yield obj

    def add(self, obj):
        # TODO: Think about it!
        self.objStore.add(obj)

    def discard(self, obj):
        # TODO: Think about it!
        self.objStore.discard(obj)


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
