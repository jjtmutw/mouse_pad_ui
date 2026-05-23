$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$patchDir = Join-Path $root "_pyinstaller_local_patch"
$cacheDir = Join-Path $root ".pyinstaller-cache"
$siteCustomize = Join-Path $patchDir "sitecustomize.py"

New-Item -ItemType Directory -Force $patchDir | Out-Null
New-Item -ItemType Directory -Force $cacheDir | Out-Null

@'
import sys
import types

fake_tcl_tk = types.ModuleType("PyInstaller.utils.hooks.tcl_tk")
fake_tcl_tk.TK_ROOTNAME = "tk"
fake_tcl_tk.TCL_ROOTNAME = "tcl"
fake_tcl_tk.tcl_dir = None
fake_tcl_tk.tcl_version = None
fake_tcl_tk.tk_version = None
fake_tcl_tk.tcl_threaded = False
fake_tcl_tk.find_tcl_tk_shared_libs = lambda tkinter_ext_file: [(None, None), (None, None)]
fake_tcl_tk.collect_tcl_tk_files = lambda tkinter_ext_file: []
sys.modules["PyInstaller.utils.hooks.tcl_tk"] = fake_tcl_tk
'@ | Set-Content -Encoding UTF8 $siteCustomize

$env:PYTHONPATH = $patchDir
$env:PYINSTALLER_CONFIG_DIR = $cacheDir

python -m PyInstaller (Join-Path $root "rotary_PC.spec") --noconfirm

Write-Host "Built dist\rotary_PC.exe"
