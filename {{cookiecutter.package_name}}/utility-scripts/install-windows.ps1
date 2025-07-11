# Run using elevated permissions (eg - Run as Admininstrator)
# This script is idempotent and safe to run multiple times.

# ------------------------------------------------------------------------------
# Create virtual environment and install the package
# ------------------------------------------------------------------------------

Write-Output "Create virtual environment and install the package ..."

# Install python requirements (assuming we have Python 3.x installed already)
Set-Location $env:USERPROFILE

$package="{{ cookiecutter.package_dir }}-{{ cookiecutter.version }}-py3-none-any.whl"
$venvPath="$env:USERPROFILE\.venvs\{{ cookiecutter.package_name }}"

if (-Not (Test-Path $venvPath)) {
  python -m venv $venvPath
}

.\.venvs\{{ cookiecutter.package_name }}\Scripts\Activate

# Install package
python -m pip install -U pip setuptools build wheel
python -m pip install "https://xstudios-pypi.s3.amazonaws.com/$package" --force-reinstall

# CD back into the location we are running script from
Set-Location $PSScriptRoot

# ------------------------------------------------------------------------------
# Create a startup task
# ------------------------------------------------------------------------------

Write-Output "Create a startup task ..."

$taskName = "Start {{ cookiecutter.package_name }}"

$exists = Get-ScheduledTask | Where-Object {$_.TaskName -like $taskName}
if ($exists) {
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute ($venvPath + "\Lib\site-packages\{{ cookiecutter.package_dir }}\data\run-hidden.vbs")
# $action = New-ScheduledTaskAction -Execute ($venvPath + "\Scripts\pythonw.exe") -Argument ($venvPath + "\Scripts\{{ cookiecutter.package_name }}.exe --verbose")
$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = 'PT30S'
$principal = New-ScheduledTaskPrincipal -GroupId "BUILTIN\Administrators" -RunLevel Highest
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName $taskName -Description $taskName -Principal $principal
