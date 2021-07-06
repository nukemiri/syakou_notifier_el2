Set FSO = CreateObject("Scripting.FileSystemObject")
Set objWShell = CreateObject("Wscript.Shell")
objWShell.CurrentDirectory = FSO.getParentFolderName(WScript.ScriptFullName)
objWShell.run "cmd /c python syakou_yoyaku.py", vbHide 