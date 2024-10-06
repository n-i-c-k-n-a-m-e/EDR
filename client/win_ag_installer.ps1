$pythonPath = Get-Command python -ErrorAction SilentlyContinue

if (-Not $pythonPath) {
    Write-Host "Downlaoding Python 3.11..."

    # URL для загрузки установочного файла Python 3.11 (64-bit)
    $pythonInstallerUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $installerPath = "$env:TEMP\python-3.11.8-amd64.exe"

    # Скачивание установочного файла
    Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $installerPath

    # Установка Python
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Includes_test=0" -Wait

    # Удаление установочного файла после завершения
    Remove-Item $installerPath -Force

    Write-Host "Python 3.11 successfully installed."
} else {
    Write-Host "Python is already downloaded: $pythonPath"
}


python windows_agent.py