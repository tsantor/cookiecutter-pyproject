' Run the application with no visible window (in background)
Dim WShell
Set WShell = CreateObject("WScript.Shell")
userDir = WShell.ExpandEnvironmentStrings("%USERPROFILE%")
' This looks odd, but it allows the userDir to contain spaces
scriptPath = """" & userDir & "\.venvs\{{ cookiecutter.package_name }}\Scripts\{{ cookiecutter.package_name }}.exe"" --verbose"
WShell.Run scriptPath, 0
Set WShell = Nothing
