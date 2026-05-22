$reader = Get-PnpDevice -Class SmartCardReader -ErrorAction SilentlyContinue | Select-Object -First 1
$svc = Get-Service SCardSvr -ErrorAction SilentlyContinue
$cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Issuer -like '*DNIE*' -or $_.Issuer -like '*AC DNIE*' } | Select-Object -First 1

$result = @{
  readerName = if ($reader) { $reader.FriendlyName } else { $null }
  readerStatus = if ($reader) { $reader.Status } else { $null }
  serviceRunning = if ($svc) { $svc.Status -eq 'Running' } else { $false }
  certThumbprint = if ($cert) { $cert.Thumbprint } else { $null }
  certSubject = if ($cert) { $cert.Subject } else { $null }
  certIssuer = if ($cert) { $cert.Issuer } else { $null }
  certValidUntil = if ($cert) { $cert.NotAfter.ToString('dd/MM/yyyy') } else { $null }
}

$result | ConvertTo-Json -Compress
