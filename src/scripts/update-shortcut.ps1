$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\ARTES BUHO - Firma Digital.lnk")
$Shortcut.TargetPath = "$env:USERPROFILE\Desktop\CARPETA CODEX\01_PROYECTOS\ARTES-BUHO_FIRMA-DIGITAL\start-hidden.vbs"
$Shortcut.WorkingDirectory = "$env:USERPROFILE\Desktop\CARPETA CODEX\01_PROYECTOS\ARTES-BUHO_FIRMA-DIGITAL"
$Shortcut.IconLocation = "$env:USERPROFILE\Desktop\CARPETA CODEX\01_PROYECTOS\ARTES-BUHO_FIRMA-DIGITAL\assets\icon.ico,0"
$Shortcut.Description = "ARTES BUHO - Firma Digital de PDFs con DNIe (dev: RUBEN COTON)"
$Shortcut.Save()
Write-Output "Acceso directo actualizado (sin ventana CMD)"
