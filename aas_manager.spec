# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['main.py'],
             binaries=[],
             datas=[
                ('LICENSE', '.'),
                ('pyproject.toml', '.'),
                ('aas_editor/settings/settings.ini', 'aas_editor/settings'),
                ('aas_editor/custom_column_lists.json', 'aas_editor'),
                ('aas_editor/icons', 'aas_editor/icons'),
                ('aas_editor/themes/grey', 'aas_editor/themes/grey'),
                ('aas_editor/themes/dark', 'aas_editor/themes/dark'),
                ('aas_editor/themes/dark.qss', 'aas_editor/themes'),
                ('aas_editor/themes/light', 'aas_editor/themes/light'),
                ('aas_editor/themes/light.qss', 'aas_editor/themes'),
                ('aas_editor/themes/grey.qss', 'aas_editor/themes'),
                ('aas_editor/submodel_templates', 'aas_editor/submodel_templates'),
                ('aas_test_engines', 'aas_test_engines'),
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='AAS_Manager',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='aas_editor\\icons\\logo.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='AAS_Manager')
