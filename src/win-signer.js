/**
 * WindowsCertSigner — firma PDF con certificados del almacen de Windows.
 *
 * Flujo:
 *   1. selectCertificate() — muestra el selector nativo, devuelve info del cert
 *   2. sign()              — firma con el cert ya seleccionado (sin segundo dialogo)
 *
 * NO requiere Autofirma. Solo Windows 10/11 con PowerShell.
 */

const { Signer } = require('@signpdf/utils');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

const TMP_DIR = path.join(os.tmpdir(), 'artesburho-firma');

// FIX BUG-07: escapar paths para PowerShell (comillas simples)
function psPath(str) {
  return str.replace(/\\/g, '\\\\').replace(/'/g, "''");
}

// FIX BUG-08: validar thumbprint (40 hex chars = SHA-1)
function isValidThumbprint(tp) {
  return typeof tp === 'string' && /^[0-9A-Fa-f]{40}$/.test(tp);
}

function ensureTmpDir() {
  if (!fs.existsSync(TMP_DIR)) fs.mkdirSync(TMP_DIR, { recursive: true });
}

class WindowsCertSigner extends Signer {
  constructor() {
    super();
    this.selectedThumbprint = null;
    this.certInfo = null;
  }

  async selectCertificate() {
    ensureTmpDir();
    const id = crypto.randomBytes(8).toString('hex');
    const certInfoFile = path.join(TMP_DIR, `certpick_${id}.json`);

    const psScript = `
Add-Type -AssemblyName System.Security
Add-Type -AssemblyName System.Windows.Forms

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("My", "CurrentUser")
$store.Open("ReadOnly")

$validCerts = $store.Certificates.Find("FindByTimeValid", [DateTime]::Now, $false)
$withKey = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2Collection
foreach ($c in $validCerts) {
  if ($c.HasPrivateKey) { $withKey.Add($c) | Out-Null }
}

if ($withKey.Count -eq 0) {
  Write-Error "NO_CERTS"
  exit 1
}

$selected = [System.Security.Cryptography.X509Certificates.X509Certificate2UI]::SelectFromCollection(
  $withKey,
  "ARTES BUHO - Firma Digital",
  "Selecciona el certificado para firmar:",
  "SingleSelection"
)

if ($selected.Count -eq 0) {
  Write-Error "CANCELLED"
  exit 2
}

$cert = $selected[0]
$cnMatch = [regex]::Match($cert.Subject, 'CN=([^,]+)')
$issuerMatch = [regex]::Match($cert.Issuer, 'CN=([^,]+)')

$info = @{
  subject = if ($cnMatch.Success) { $cnMatch.Groups[1].Value.Trim() } else { $cert.Subject.Substring(0, [Math]::Min(80, $cert.Subject.Length)) }
  issuer = if ($issuerMatch.Success) { $issuerMatch.Groups[1].Value.Trim() } else { $cert.Issuer.Substring(0, [Math]::Min(80, $cert.Issuer.Length)) }
  thumbprint = $cert.Thumbprint
  validUntil = $cert.NotAfter.ToString("dd/MM/yyyy")
  serialNumber = $cert.SerialNumber
} | ConvertTo-Json -Compress

[System.IO.File]::WriteAllText('${psPath(certInfoFile)}', $info)
$store.Close()
Write-Output "OK"
`;

    const psFile = path.join(TMP_DIR, `pick_${id}.ps1`);
    fs.writeFileSync(psFile, psScript, 'utf-8');

    return new Promise((resolve, reject) => {
      exec(
        `powershell.exe -STA -NoProfile -ExecutionPolicy Bypass -File "${psFile}"`,
        { encoding: 'utf-8', timeout: 180000, windowsHide: false }, // FIX: timeout a 3 min
        (err, stdout, stderr) => {
          try { fs.unlinkSync(psFile); } catch (e) {}

          if (err) {
            if ((stderr || '').includes('CANCELLED') || err.code === 2) {
              reject(new Error('Firma cancelada por el usuario'));
            } else if ((stderr || '').includes('NO_CERTS')) {
              reject(new Error('No hay certificados con clave privada instalados en Windows'));
            } else {
              reject(new Error(`Error al seleccionar certificado: ${stderr || err.message}`));
            }
            return;
          }

          if (!fs.existsSync(certInfoFile)) {
            reject(new Error('No se pudo leer la info del certificado'));
            return;
          }

          try {
            this.certInfo = JSON.parse(fs.readFileSync(certInfoFile, 'utf-8'));
            // FIX BUG-08: validar thumbprint
            if (!isValidThumbprint(this.certInfo.thumbprint)) {
              try { fs.unlinkSync(certInfoFile); } catch (e) {}
              reject(new Error('Thumbprint del certificado invalido'));
              return;
            }
            this.selectedThumbprint = this.certInfo.thumbprint;
            try { fs.unlinkSync(certInfoFile); } catch (e) {}
            console.log('[cert] Seleccionado:', this.certInfo.subject);
            resolve(this.certInfo);
          } catch (e) {
            try { fs.unlinkSync(certInfoFile); } catch (er) {}
            reject(new Error('Error al parsear info del certificado'));
          }
        }
      );
    });
  }

  async sign(pdfBuffer, signingTime = undefined) {
    if (!this.selectedThumbprint || !isValidThumbprint(this.selectedThumbprint)) {
      throw new Error('No se ha seleccionado certificado valido. Llama a selectCertificate() primero.');
    }

    ensureTmpDir();
    const id = crypto.randomBytes(8).toString('hex');
    const dataFile = path.join(TMP_DIR, `data_${id}.bin`);
    const sigFile = path.join(TMP_DIR, `sig_${id}.der`);

    try {
      fs.writeFileSync(dataFile, pdfBuffer);

      // FIX EDGE-10: fallback automatico a EndCertOnly si WholeChain falla
      const psScript = `
Add-Type -AssemblyName System.Security

$dataPath = '${psPath(dataFile)}'
$sigPath = '${psPath(sigFile)}'
$thumbprint = '${this.selectedThumbprint}'

$store = New-Object System.Security.Cryptography.X509Certificates.X509Store("My", "CurrentUser")
$store.Open("ReadOnly")
$certs = $store.Certificates.Find("FindByThumbprint", $thumbprint, $false)

if ($certs.Count -eq 0) {
  Write-Error "CERT_NOT_FOUND"
  exit 1
}

$cert = $certs[0]
$data = [System.IO.File]::ReadAllBytes($dataPath)

function Sign-WithMode([string]$mode) {
  $contentInfo = New-Object System.Security.Cryptography.Pkcs.ContentInfo(,$data)
  $signedCms = New-Object System.Security.Cryptography.Pkcs.SignedCms($contentInfo, $true)
  $cmsSigner = New-Object System.Security.Cryptography.Pkcs.CmsSigner($cert)
  $cmsSigner.DigestAlgorithm = New-Object System.Security.Cryptography.Oid("2.16.840.1.101.3.4.2.1")
  $cmsSigner.IncludeOption = $mode
  $signedCms.ComputeSignature($cmsSigner)
  return $signedCms.Encode()
}

try {
  $derBytes = Sign-WithMode "WholeChain"
} catch {
  try {
    $derBytes = Sign-WithMode "EndCertOnly"
    Write-Output "FALLBACK_ENDCERT"
  } catch {
    Write-Error "SIGN_ERROR: $_"
    exit 2
  }
}

[System.IO.File]::WriteAllBytes($sigPath, $derBytes)
$store.Close()
Write-Output "OK"
`;

      const psFile = path.join(TMP_DIR, `sign_${id}.ps1`);
      fs.writeFileSync(psFile, psScript, 'utf-8');

      const sigBuffer = await new Promise((resolve, reject) => {
        exec(
          `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${psFile}"`,
          { encoding: 'utf-8', timeout: 60000, windowsHide: true },
          (err, stdout, stderr) => {
            try { fs.unlinkSync(psFile); } catch (e) {}

            if (err) {
              reject(new Error(`Error al firmar: ${stderr || err.message}`));
              return;
            }

            if (!fs.existsSync(sigFile)) {
              reject(new Error('No se genero la firma'));
              return;
            }

            if ((stdout || '').includes('FALLBACK_ENDCERT')) {
              console.log('[sign] Aviso: firma sin cadena completa (EndCertOnly)');
            }

            const sig = fs.readFileSync(sigFile);
            try { fs.unlinkSync(sigFile); } catch (e) {}
            resolve(sig);
          }
        );
      });

      return sigBuffer;

    } finally {
      try { if (fs.existsSync(dataFile)) fs.unlinkSync(dataFile); } catch (e) {}
      try { if (fs.existsSync(sigFile)) fs.unlinkSync(sigFile); } catch (e) {}
    }
  }

  getCertInfo() {
    return this.certInfo || {
      subject: 'Certificado Digital',
      issuer: 'Autoridad Certificadora',
      thumbprint: null,
      validUntil: null,
      serialNumber: null
    };
  }

  reset() {
    this.selectedThumbprint = null;
    this.certInfo = null;
  }
}

// Listar certificados (para estado, sin GUI)
async function listCertificates() {
  return new Promise((resolve) => {
    const psCmd = `
      Get-ChildItem Cert:\\CurrentUser\\My -ErrorAction SilentlyContinue |
        Where-Object { $_.HasPrivateKey -and $_.NotAfter -gt (Get-Date) } |
        ForEach-Object {
          $cn = if ($_.Subject -match 'CN=([^,]+)') { $Matches[1].Trim() } else { $_.Subject }
          $iss = if ($_.Issuer -match 'CN=([^,]+)') { $Matches[1].Trim() } else { $_.Issuer }
          @{ subject=$cn; issuer=$iss; thumbprint=$_.Thumbprint; validUntil=$_.NotAfter.ToString('dd/MM/yyyy') }
        } | ConvertTo-Json -Compress
    `.replace(/\n/g, ' ');

    exec(
      `powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "${psCmd.replace(/"/g, '\\"')}"`,
      { encoding: 'utf-8', timeout: 8000, windowsHide: true },
      (err, stdout) => {
        if (err || !stdout.trim()) return resolve([]);
        try {
          let certs = JSON.parse(stdout.trim());
          if (!Array.isArray(certs)) certs = [certs];
          resolve(certs);
        } catch (e) {
          resolve([]);
        }
      }
    );
  });
}

module.exports = { WindowsCertSigner, listCertificates };
