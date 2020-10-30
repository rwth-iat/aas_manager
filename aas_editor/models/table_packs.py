from aas_editor.models import Package, StandardTable
from aas_editor.settings import PACKAGE_ROLE, NAME_ROLE


class PacksTable(StandardTable):
    def openedFiles(self):
        files = set()
        for i in range(self.rowCount()):
            item = self.index(row=i)
            pack: Package = item.data(PACKAGE_ROLE)
            try:
                files.add(pack.file)
            except AttributeError:
                continue
        return files
