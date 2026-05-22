# Propaga los certificados del DNIe al almacen personal de Windows
# Usa el Certificate Propagation Service de Windows

Write-Output "=== Propagando certificados del DNIe al almacen ==="

# 1. Asegurar que el servicio de propagacion esta activo
$svc = Get-Service -Name CertPropSvc -ErrorAction SilentlyContinue
if ($svc) {
    if ($svc.Status -ne 'Running') {
        Write-Output "Iniciando servicio de propagacion de certificados..."
        Start-Service CertPropSvc -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    Write-Output "Servicio CertPropSvc: $((Get-Service CertPropSvc).Status)"
} else {
    Write-Output "AVISO: Servicio CertPropSvc no encontrado"
}

# 2. Asegurar servicio de enumeracion activo
$svcEnum = Get-Service -Name ScDeviceEnum -ErrorAction SilentlyContinue
if ($svcEnum -and $svcEnum.Status -ne 'Running') {
    Write-Output "Iniciando servicio de enumeracion de tarjetas..."
    Start-Service ScDeviceEnum -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# 3. Verificar si ya hay certs del DNIe
$before = @(Get-ChildItem Cert:\CurrentUser\My | Where-Object {
    $_.Issuer -like '*DNIE*' -or $_.Issuer -like '*AC DNIE*' -or $_.Issuer -like '*POLICIA*'
})

Write-Output "Certificados DNIe antes: $($before.Count)"

# 4. Forzar propagacion - leer la tarjeta con el CSP
Write-Output "Leyendo tarjeta inteligente..."
try {
    # This triggers Windows to read and cache the cert
    $csp = New-Object System.Security.Cryptography.CspParameters(1, "Microsoft Base Smart Card Crypto Provider")
    $csp.KeyContainerName = "489c628c8285c6d1edb20cf22fbefe55"
    $csp.Flags = [System.Security.Cryptography.CspProviderFlags]::UseExistingKey
    $rsa = New-Object System.Security.Cryptography.RSACryptoServiceProvider($csp)
    Write-Output "  Clave RSA accedida correctamente"
    Write-Output "  KeySize: $($rsa.KeySize)"
    $rsa.Dispose()
} catch {
    Write-Output "  Nota: $($_.Exception.Message)"
}

# 5. Esperar propagacion
Start-Sleep -Seconds 3

# 6. Verificar despues
$after = @(Get-ChildItem Cert:\CurrentUser\My | Where-Object {
    $_.Issuer -like '*DNIE*' -or $_.Issuer -like '*AC DNIE*' -or $_.Issuer -like '*POLICIA*'
})

Write-Output ""
Write-Output "=== RESULTADO ==="
Write-Output "Certificados DNIe despues: $($after.Count)"

if ($after.Count -gt 0) {
    foreach ($c in $after) {
        Write-Output ""
        Write-Output "  Subject: $($c.Subject)"
        Write-Output "  Issuer: $($c.Issuer)"
        Write-Output "  Thumbprint: $($c.Thumbprint)"
        Write-Output "  HasPrivateKey: $($c.HasPrivateKey)"
        Write-Output "  NotAfter: $($c.NotAfter)"
    }
    Write-Output ""
    Write-Output "EXITO: Certificado(s) del DNIe disponible(s) en el almacen de Windows"
} else {
    Write-Output ""
    Write-Output "El certificado aun no aparece en el almacen personal."
    Write-Output "Esto es normal - el DNIe requiere que el PIN sea introducido"
    Write-Output "para propagar el certificado de firma."
    Write-Output ""
    Write-Output "Opciones:"
    Write-Output "  1. Abrir certutil manualmente y aceptar el PIN"
    Write-Output "  2. Instalar el software oficial del DNIe (dnielectronico.es)"
    Write-Output "  3. Usar la app para firmar directamente con el lector (sin almacen)"
}
