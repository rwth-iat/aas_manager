from aas_editor.models import Package, StandardTable
from aas_editor.settings import PACKAGE_ROLE, NAME_ROLE


class PacksTable(StandardTable):
    def openedPacks(self):
        packs = set()
        for i in range(self.rowCount()):
            item = self.index(row=i)
            pack: Package = item.data(PACKAGE_ROLE)
            try:
                packs.add(pack)
            except AttributeError:
                continue
        return packs

    def openedFiles(self):
        files = set([pack.file for pack in self.openedPacks()])
        return files
        # for i in range(self.rowCount()):
        #     item = self.index(row=i)
        #     pack: Package = item.data(PACKAGE_ROLE)
        #     try:
        #         files.add(pack.file)
        #     except AttributeError:
        #         continue
        # return files
