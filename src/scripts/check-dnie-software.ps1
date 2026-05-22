# Check if DNIe software/drivers are installed
$paths = @(
    "C:\Program Files\DNIe",
    "C:\Program Files (x86)\DNIe",
    "C:\Windows\System32\DNIe_P11_x64.dll",
    "C:\Windows\SysWOW64\DNIe_P11_x32.dll",
    "C:\Program Files\Autofirma",
    "C:\Program Files (x86)\Autofirma"
)

Write-Output "=== Software DNIe ==="
foreach ($p in $paths) {
    $exists = Test-Path $p
    $status = if ($exists) { "SI" } else { "NO" }
    Write-Output "$status : $p"
}

Write-Output ""
Write-Output "=== Apps instaladas con DNI/Firma/Autofirma ==="
$apps = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue
$apps += Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue
$filtered = $apps | Where-Object {
    $_.DisplayName -like '*DNI*' -or
    $_.DisplayName -like '*Autofirma*' -or
    $_.DisplayName -like '*firma*' -or
    $_.DisplayName -like '*certificado*'
}
if ($filtered) {
    foreach ($a in $filtered) {
        Write-Output "  $($a.DisplayName) | $($a.InstallLocation)"
    }
} else {
    Write-Output "  Ninguna encontrada"
}

Write-Output ""
Write-Output "=== Minidriver DNIe (driver tarjeta) ==="
$minidriver = Get-PnpDevice -Class SmartCardFilter -ErrorAction SilentlyContinue
if ($minidriver) {
    Write-Output "  $($minidriver.FriendlyName) - Status: $($minidriver.Status)"
} else {
    Write-Output "  No detectado"
}
