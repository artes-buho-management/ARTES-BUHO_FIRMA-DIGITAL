Write-Output "=== CERTIFICADOS EN ALMACEN PERSONAL ==="
$certs = Get-ChildItem Cert:\CurrentUser\My
foreach ($c in $certs) {
    Write-Output "Thumbprint: $($c.Thumbprint)"
    Write-Output "Subject: $($c.Subject)"
    Write-Output "Issuer: $($c.Issuer)"
    Write-Output "NotAfter: $($c.NotAfter)"
    Write-Output "HasPrivateKey: $($c.HasPrivateKey)"
    Write-Output "---"
}
Write-Output ""
Write-Output "=== TOTAL: $($certs.Count) certificados ==="
