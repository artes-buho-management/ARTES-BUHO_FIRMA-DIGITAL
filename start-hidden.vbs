' Arranque silencioso de ARTES BUHO Firma Digital (dev mode)
' El propio index.js abre el navegador, no abrirlo aqui (evita doble pestana)
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Environment("PROCESS")("ARTESBUHO_NO_BROWSER") = "0"
WshShell.Run "node src/index.js", 0, False
