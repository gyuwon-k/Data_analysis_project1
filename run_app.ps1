$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "C:\Users\Win11Pro\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

Set-Location $ProjectRoot
& $PythonExe -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
& $PythonExe -m streamlit run app.py --global.developmentMode=false --server.port 8502
