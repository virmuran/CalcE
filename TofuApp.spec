# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('modules', 'modules'), ('resource_helper.py', '.'), ('data_manager.py', '.'), ('theme_manager.py', '.'), ('module_loader.py', '.'), ('base_module.py', '.')],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'matplotlib.backends.backend_qt5agg', 'matplotlib.figure', 'numpy', 'scipy', 'scipy.optimize', 'scipy.integrate', 'scipy.special', 'scipy.constants', 'scipy.interpolate', 'datetime', 'json', 'os', 'sys', 'math', 'random', 'reportlab', 'reportlab.pdfgen', 'reportlab.pdfgen.canvas', 'reportlab.lib', 'reportlab.lib.pagesizes', 'reportlab.lib.styles', 'reportlab.lib.units', 'reportlab.pdfbase', 'reportlab.pdfbase.ttfonts', 'reportlab.platypus', 'reportlab.platypus.paragraph', 'reportlab.platypus.doctemplate', 'threading', 'time', 're', 'pathlib', 'shutil', 'pyperclip', 'pandas', 'pandas._libs', 'pandas._libs.tslibs', 'pandas.core.dtypes.common', 'pandas.io.formats.format', 'pandas.plotting._matplotlib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtGui'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TofuApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['tofuapp.ico'],
)
