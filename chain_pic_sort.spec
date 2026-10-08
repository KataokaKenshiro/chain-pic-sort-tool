# PyInstaller 設定: uv run --group build pyinstaller chain_pic_sort.spec
# dist/ChainPicSort/ にフォルダ形式で出力する（1 ファイル形式より起動が速い）。
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ["src/chain_pic_sort/__main__.py"],
    pathex=["src"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ChainPicSort",
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="ChainPicSort")
