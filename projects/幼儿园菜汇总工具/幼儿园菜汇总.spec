# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['./src', '<Python安装目录>/Library/bin'],
    binaries=[('<Python安装目录>/Library/bin/LIBBZ2.dll', '.'), ('<Python安装目录>/Library/bin/ffi.dll', '.'), ('<Python安装目录>/Library/bin/libcrypto-3-x64.dll', '.'), ('<Python安装目录>/Library/bin/libexpat.dll', '.'), ('<Python安装目录>/Library/bin/liblzma.dll', '.'), ('<Python安装目录>/Library/bin/libssl-3-x64.dll', '.'), ('<Python安装目录>/Library/bin/sqlite3.dll', '.')],
    datas=[('config', 'config')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='幼儿园菜汇总',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='幼儿园菜汇总',
)
