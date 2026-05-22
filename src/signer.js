const { PDFDocument, PDFName, rgb, StandardFonts, degrees } = require('pdf-lib');
const fs = require('fs');

/**
 * Anade el sello visible de firma en la esquina inferior derecha
 * de la ultima pagina del documento.
 *
 * La info del sello viene del certificado real que va a firmar
 * (se pasa como parametro certInfo, ya extraido antes de llamar aqui).
 */
async function addVisibleSignature(inputPdfPath, outputPdfPath, certInfo) {
  const pdfBytes = fs.readFileSync(inputPdfPath);

  let pdfDoc;
  try {
    pdfDoc = await PDFDocument.load(pdfBytes, { ignoreEncryption: true });
  } catch (err) {
    throw new Error('El PDF esta corrupto o protegido y no se puede procesar');
  }

  const pages = pdfDoc.getPages();
  const warnings = [];

  if (pages.length === 0) {
    throw new Error('El PDF no tiene paginas');
  }

  // FIX EDGE-05: Detectar firmas previas en el PDF
  try {
    const acroForm = pdfDoc.catalog.lookup(PDFName.of('AcroForm'));
    if (acroForm) {
      const sigFlags = acroForm.lookup(PDFName.of('SigFlags'));
      if (sigFlags && sigFlags.asNumber && (sigFlags.asNumber() & 1) === 1) {
        warnings.push('El PDF ya contenia firmas digitales previas. Anadir una nueva podria invalidarlas.');
      }
    }
  } catch (e) {
    // Si falla la deteccion, no bloquear la firma
  }

  // Siempre ultima pagina
  const lastPage = pages[pages.length - 1];
  const rawSize = lastPage.getSize();
  const rotation = lastPage.getRotation().angle % 360;

  // FIX EDGE-04: Paginas rotadas — usar dimensiones efectivas
  let effW = rawSize.width;
  let effH = rawSize.height;
  if (rotation === 90 || rotation === 270) {
    effW = rawSize.height;
    effH = rawSize.width;
  }

  // FIX #11: si la pagina es demasiado pequena para el sello
  if (effW < 200 || effH < 150) {
    warnings.push('Pagina demasiado pequena para sello visible (se omite).');
    const unchanged = await pdfDoc.save();
    fs.writeFileSync(outputPdfPath, unchanged);
    return {
      page: pages.length,
      position: 'none',
      signer: certInfo.subject,
      issuer: certInfo.issuer,
      warnings
    };
  }

  const fontBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const fontNormal = await pdfDoc.embedFont(StandardFonts.Helvetica);

  const now = new Date();
  const dateStr = now.toLocaleDateString('es-ES', {
    day: '2-digit', month: '2-digit', year: 'numeric'
  });
  const timeStr = now.toLocaleTimeString('es-ES', {
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });

  // Sanitizar texto — solo Latin-1 (Helvetica standard) para evitar errores Unicode
  const toLatin1 = s => String(s || '').replace(/[^\x20-\xFF]/g, '?');
  const signerName = toLatin1(certInfo.subject || 'Firmante').substring(0, 42);
  const issuerName = toLatin1(certInfo.issuer || 'Autoridad Certificadora').substring(0, 48);
  const validUntil = toLatin1(certInfo.validUntil || '');
  const serial = certInfo.serialNumber ? toLatin1(certInfo.serialNumber).substring(0, 20) : '';

  const boxW = 280;
  const boxH = 105;
  const margin = 30;

  // FIX EDGE-04: posicion absoluta en coordenadas de pagina rotada
  // Sin rotacion: esquina inferior derecha clasica
  // Con rotacion, pdf-lib dibuja en coordenadas de pagina, no rotadas,
  // asi que el "abajo-derecha visual" cambia segun rotation.
  let x, y, drawRotation = 0;

  switch (rotation) {
    case 0:
      x = rawSize.width - boxW - margin;
      y = margin;
      break;
    case 90:
      // La pagina se ve girada 90° horario. Lo visual "abajo-derecha" es coordenadas (margin, margin).
      x = margin;
      y = margin;
      drawRotation = 90;
      break;
    case 180:
      x = margin;
      y = rawSize.height - boxH - margin;
      drawRotation = 180;
      break;
    case 270:
      x = rawSize.width - margin;
      y = rawSize.height - boxH - margin;
      drawRotation = 270;
      break;
    default:
      x = rawSize.width - boxW - margin;
      y = margin;
  }

  // FIX BUG-05: No usar caracter Unicode (no existe en Helvetica estandar)
  // Sustituimos "✓" por texto ASCII "OK" o simbolo Latin-1.
  const checkText = 'OK';

  // Usando rotate en drawRectangle/drawText (pdf-lib soporta rotate)
  const rot = drawRotation ? { rotate: degrees(drawRotation) } : {};

  // Para dibujar rotado correctamente, pdf-lib rota alrededor del punto (x,y).
  // Simplificamos: si la pagina esta rotada, no pintamos sello rotado (es complejo
  // calcular las traslaciones correctas). Avisamos y pintamos en coordenadas nativas.
  if (drawRotation !== 0) {
    warnings.push(`La pagina esta rotada ${rotation}°. El sello se ha colocado en coordenadas nativas.`);
    // Reseteamos a esquina nativa inferior-derecha
    x = rawSize.width - boxW - margin;
    y = margin;
  }

  // Sombra suave
  lastPage.drawRectangle({
    x: x + 2, y: y - 2,
    width: boxW, height: boxH,
    color: rgb(0.85, 0.85, 0.85),
    opacity: 0.4,
    borderWidth: 0,
  });
  // Fondo blanco
  lastPage.drawRectangle({
    x, y,
    width: boxW, height: boxH,
    borderColor: rgb(0.75, 0.75, 0.75),
    borderWidth: 1,
    color: rgb(1, 1, 1),
    opacity: 0.97,
  });

  // Barra roja
  lastPage.drawRectangle({
    x, y: y + boxH - 22,
    width: boxW, height: 22,
    color: rgb(0.9, 0.19, 0.15),
  });

  lastPage.drawText('FIRMADO DIGITALMENTE', {
    x: x + 10,
    y: y + boxH - 16,
    size: 9,
    font: fontBold,
    color: rgb(1, 1, 1),
  });

  lastPage.drawText(checkText, {
    x: x + boxW - 26,
    y: y + boxH - 16,
    size: 10,
    font: fontBold,
    color: rgb(0.96, 0.76, 0.05),
  });

  let cy = y + boxH - 36;

  lastPage.drawText(signerName, {
    x: x + 10, y: cy,
    size: 9,
    font: fontBold,
    color: rgb(0.1, 0.1, 0.1),
  });
  cy -= 13;

  lastPage.drawText(`Emisor: ${issuerName}`, {
    x: x + 10, y: cy,
    size: 7,
    font: fontNormal,
    color: rgb(0.35, 0.35, 0.35),
  });
  cy -= 11;

  if (serial) {
    lastPage.drawText(`N/S: ${serial}`, {
      x: x + 10, y: cy,
      size: 6.5,
      font: fontNormal,
      color: rgb(0.45, 0.45, 0.45),
    });
    cy -= 11;
  }

  lastPage.drawRectangle({
    x: x + 10, y: cy + 4,
    width: boxW - 20, height: 1.5,
    color: rgb(0.96, 0.76, 0.05),
  });
  cy -= 8;

  lastPage.drawText(`Fecha: ${dateStr}  -  Hora: ${timeStr}`, {
    x: x + 10, y: cy,
    size: 7.5,
    font: fontBold,
    color: rgb(0.2, 0.2, 0.2),
  });
  cy -= 11;

  if (validUntil) {
    lastPage.drawText(`Cert. valido hasta: ${validUntil}`, {
      x: x + 10, y: cy,
      size: 6.5,
      font: fontNormal,
      color: rgb(0.45, 0.45, 0.45),
    });
  }

  const stampedBytes = await pdfDoc.save();
  fs.writeFileSync(outputPdfPath, stampedBytes);

  return {
    page: pages.length,
    position: 'bottom-right',
    signer: certInfo.subject,
    issuer: certInfo.issuer,
    warnings
  };
}

module.exports = { addVisibleSignature };
