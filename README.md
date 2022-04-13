<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/zrgt/pygui40aas">
    <img src="aas_editor/icons/full_logo.svg" alt="Logo" width="240" height="80">
  </a>
  <p align="center">
    AAS Manager is a free, open source, cross-platform visual viewer/editor based on <a href="https://www.riverbankcomputing.com/software/pyqt/"><strong>PyQt</strong></a> Framework and <a href="https://git.rwth-aachen.de/acplt/pyi40aas"><strong>PyI40AAS</strong></a> SDK.
    <br />
    <br />
    <a href="https://github.com/zrgt/pygui40aas/releases">Download</a>
    ·
    <a href="https://github.com/zrgt/pygui40aas/issues">Report Bug</a>
    ·
    <a href="https://github.com/zrgt/pygui40aas/issues">Request Feature</a>
  </p>
</p>



|                                                      Screenshots                                                      |                                                                                                                   |
| :--------------------------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------------------------------------: |
|   ![](https://github.com/zrgt/pygui40aas/raw/master/screenshots/dark_theme.PNG) Grey theme        |        ![](https://github.com/zrgt/pygui40aas/raw/master/screenshots/light_theme.png) Light theme        |
|   ![](https://github.com/zrgt/pygui40aas/raw/master/screenshots/add_dialog.PNG) Dialog for creating objects   |   ![](https://github.com/zrgt/pygui40aas/raw/master/screenshots/edit_in_dialog.png) Dialog for value editing   |
|   ![](https://github.com/zrgt/pygui40aas/raw/master/screenshots/edit_in_cell.PNG) Edit value in the treetable cell   |   ![](https://github.com/zrgt/pygui40aas/raw/master/screenshots/columns_management.png) Columns management in the treetable   |
|   ![](https://github.com/zrgt/pygui40aas/raw/master/screenshots/context_menu.PNG) Context menu of object in the treetable  |  |


For further information about the Asset Administration Shell, see the publication "Details of the Asset Administration Shell" [(Version 3.0RC01) ](
https://www.plattform-i40.de/PI40/Redaktion/EN/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part1_V3.html
) or [(Version 2.0.1)](
https://www.plattform-i40.de/PI40/Redaktion/EN/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part1_V2.html
) by Plattform Industrie 4.0.

## Installation
### User version
You can find binaries of the editor for Windows or Linux systems in [the releases](https://github.com/zrgt/pygui40aas/releases).

### Development version
1. Clone the repo
   ```sh
   git clone https://github.com/zrgt/pygui40aas.git
   ```
2. Install requirements
   ```sh
   pip install -r requirements.txt
   ```
3. Freeze an application into stand-alone executable
   ```sh
   pyinstaller aas_manager.spec
   ```
4. Run the executable in ``dist`` folder

## License
GPLv3. See [LICENSE](LICENSE).

## Contact
If you have any questions, please contact [Igor Garmaev](https://github.com/zrgt): [i.garmaev@plt.rwth-aachen.de](mailto:i.garmaev@plt.rwth-aachen.de)