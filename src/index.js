const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const os = require('os');
const crypto = require('crypto');
const { PDFDocument } = require('pdf-lib');
const { SignPdf } = require('@signpdf/signpdf');
const { pdflibAddPlaceholder } = require('@signpdf/placeholder-pdf-lib');
const { addVisibleSignature } = require('./signer');
const { WindowsCertSigner, listCertificates } = require('./win-signer');

const app = express();
const PORT = 3000;
const HOST = '127.0.0.1'; // FIX SEC-01: solo localhost, no expuesto a red

// Base directory (portable: junto al .exe)
const BASE_DIR = process.pkg ? path.dirname(process.execPath) : path.join(__dirname, '..');

const outputDir = path.join(BASE_DIR, 'output');
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

const uploadsDir = path.join(BASE_DIR, 'uploads');
if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

// FIX #7: Limpiar temporales huerfanos al arrancar
try {
  fs.readdirSync(outputDir)
    .filter(f => f.startsWith('_stamped_'))
    .forEach(f => { try { fs.unlinkSync(path.join(outputDir, f)); } catch (e) {} });
} catch (e) {}

// FIX SEC-07: Limpiar directorio temporal del sistema al arrancar
try {
  const TMP_FIRMA = path.join(os.tmpdir(), 'artesburho-firma');
  if (fs.existsSync(TMP_FIRMA)) {
    fs.readdirSync(TMP_FIRMA).forEach(f => {
      try { fs.unlinkSync(path.join(TMP_FIRMA, f)); } catch (e) {}
    });
  }
} catch (e) {}

// FIX #8: Sanitizar nombre de archivo
function sanitizeFilename(name) {
  return name
    .replace(/\.pdf$/i, '')
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, '_')  // caracteres ilegales Windows
    .replace(/[&;`$(){}[\]!#]/g, '_')          // caracteres peligrosos shell
    .substring(0, 100)                          // longitud maxima razonable
    || 'documento';
}

// Multer — FIX #9: limite reducido a 15MB
const upload = multer({
  dest: uploadsDir,
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') cb(null, true);
    else cb(new Error('Solo se permiten archivos PDF'));
  },
  limits: { fileSize: 15 * 1024 * 1024 }
});

// Static files — FIX: usar __dirname para compatibilidad con pkg snapshot
app.use(express.static(path.join(__dirname, '..', 'public')));
app.use(express.json({ limit: '100kb' })); // FIX: limite de JSON body

// FIX BUG-01: SignPdf se instancia por peticion en el handler

// Mutex atomico para firma (FIX BUG-02: usa Promise en vez de flag)
let signingLock = null;

// Rate limit simple (FIX SEC-02): max 30 req/min por IP
const rateLimits = new Map();
function rateLimit(req, res, next) {
  const ip = req.ip || req.connection?.remoteAddress || 'unknown';
  const now = Date.now();
  const WINDOW = 60 * 1000;
  const MAX = 30;
  const entry = rateLimits.get(ip) || { count: 0, reset: now + WINDOW };
  if (now > entry.reset) { entry.count = 0; entry.reset = now + WINDOW; }
  entry.count++;
  rateLimits.set(ip, entry);
  if (entry.count > MAX) {
    return res.status(429).json({ error: 'Demasiadas peticiones. Espera un momento.' });
  }
  next();
}
app.use('/api/', rateLimit);

// Limpieza periodica del rate limit map (evitar leak)
setInterval(() => {
  const now = Date.now();
  for (const [ip, entry] of rateLimits) {
    if (now > entry.reset) rateLimits.delete(ip);
  }
}, 5 * 60 * 1000);

// ─── API: Status ───
app.get('/api/status', async (req, res) => {
  try {
    const certs = await listCertificates();
    const first = certs[0] || null;
    res.json({
      ok: certs.length > 0,
      certificate: first ? {
        subject: first.subject,
        issuer: first.issuer,
        validUntil: first.validUntil,
        count: certs.length
      } : null,
      signing: !!signingLock
    });
  } catch (err) {
    res.json({ ok: false, certificate: null, error: err.message });
  }
});

// ─── API: List certs ─── FIX #10: try/catch
app.get('/api/certs', async (req, res) => {
  try {
    const certs = await listCertificates();
    res.json({ certs });
  } catch (err) {
    res.json({ certs: [], error: err.message });
  }
});

// ─── API: Sign PDF ───
app.post('/api/sign', upload.single('pdf'), async (req, res) => {
  // FIX BUG-02: mutex atomico con Promise
  if (signingLock) {
    if (req.file) { try { fs.unlinkSync(req.file.path); } catch (e) {} }
    return res.status(429).json({ error: 'Ya hay una firma en curso. Espera a que termine.' });
  }

  if (!req.file) return res.status(400).json({ error: 'No se ha proporcionado un PDF' });

  let lockResolve;
  signingLock = new Promise(r => { lockResolve = r; });

  const inputPath = path.resolve(req.file.path);

  // FIX BUG-03: usar random bytes en vez de Date.now()
  const randomId = crypto.randomBytes(6).toString('hex');
  const originalName = sanitizeFilename(req.file.originalname);
  const outputName = `${originalName}_FIRMADO_${randomId}.pdf`;
  const stampedPath = path.join(outputDir, `_stamped_${randomId}.pdf`);
  const outputPath = path.join(outputDir, outputName);

  // FIX BUG-01: instancias por peticion
  const signer = new WindowsCertSigner();
  const signPdf = new SignPdf();

  try {
    // PASO 1: Selector de certificado
    console.log('[sign] Paso 1: Seleccionar certificado...');
    const certInfo = await signer.selectCertificate();
    console.log('[sign] Certificado:', certInfo.subject);

    // PASO 2: Sello visible con info real del firmante
    console.log('[sign] Paso 2: Sello visible...');
    const stampInfo = await addVisibleSignature(inputPath, stampedPath, certInfo);
    console.log('[sign] Sello en pagina', stampInfo.page);

    // PASO 3: Placeholder PAdES
    console.log('[sign] Paso 3: Estructura PAdES...');
    const stampedBytes = fs.readFileSync(stampedPath);

    let pdfDoc;
    try {
      pdfDoc = await PDFDocument.load(stampedBytes, { ignoreEncryption: true });
    } catch (loadErr) {
      throw new Error('El PDF esta corrupto o no se puede procesar');
    }

    pdflibAddPlaceholder({
      pdfDoc,
      reason: 'Firma digital ARTES BUHO MANAGEMENT',
      contactInfo: 'booking@artesbuhomanagement.com',
      name: certInfo.subject,
      location: 'Madrid, Espana',
      signatureLength: 16384
    });

    const pdfWithPlaceholder = await pdfDoc.save();

    // PASO 4: Firma digital
    console.log('[sign] Paso 4: Firmando...');
    const signedPdf = await signPdf.sign(pdfWithPlaceholder, signer);

    fs.writeFileSync(outputPath, signedPdf);
    const stat = fs.statSync(outputPath);

    // Limpiar temporales
    try { if (fs.existsSync(inputPath)) fs.unlinkSync(inputPath); } catch (e) {}
    try { if (fs.existsSync(stampedPath)) fs.unlinkSync(stampedPath); } catch (e) {}

    console.log('[sign] OK — firmado por', certInfo.subject);

    res.json({
      ok: true,
      message: 'PDF firmado correctamente',
      signer: certInfo.subject,
      issuer: certInfo.issuer,
      format: 'PAdES (PDF Advanced Electronic Signatures)',
      algorithm: 'SHA-256',
      signDate: new Date().toLocaleString('es-ES'),
      warnings: stampInfo.warnings || [],
      output: {
        filename: outputName,
        path: `/api/download/${encodeURIComponent(outputName)}`,
        size: stat.size
      }
    });

  } catch (err) {
    try { if (fs.existsSync(inputPath)) fs.unlinkSync(inputPath); } catch (e) {}
    try { if (fs.existsSync(stampedPath)) fs.unlinkSync(stampedPath); } catch (e) {}
    console.error('[sign] Error:', err.message);
    res.status(500).json({ error: err.message || 'Error al firmar' });
  } finally {
    lockResolve();
    signingLock = null;
  }
});

// ─── API: Download ─── FIX #1: validacion path traversal antes de todo
app.get('/api/download/:filename', (req, res) => {
  const filename = decodeURIComponent(req.params.filename);

  // Rechazar si contiene path traversal
  if (/[\/\\]|\.\./.test(filename)) {
    return res.status(400).json({ error: 'Nombre de archivo invalido' });
  }

  // FIX: solo permitir .pdf
  if (!/\.pdf$/i.test(filename)) {
    return res.status(400).json({ error: 'Solo se pueden descargar PDFs' });
  }

  // FIX: bloquear temporales
  if (filename.startsWith('_stamped_')) {
    return res.status(403).json({ error: 'Acceso denegado' });
  }

  const filePath = path.join(outputDir, filename);

  // Doble check: ruta resuelta dentro de outputDir
  if (!path.resolve(filePath).startsWith(path.resolve(outputDir))) {
    return res.status(403).json({ error: 'Acceso denegado' });
  }

  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'Archivo no encontrado' });
  }

  res.download(filePath);
});

// ─── API: History ─── FIX: paginacion
app.get('/api/history', (req, res) => {
  if (!fs.existsSync(outputDir)) return res.json({ files: [] });
  try {
    const limit = Math.min(parseInt(req.query.limit) || 100, 500);
    const files = fs.readdirSync(outputDir)
      .filter(f => f.endsWith('.pdf') && !f.startsWith('_stamped_'))
      .map(f => {
        const stat = fs.statSync(path.join(outputDir, f));
        return {
          name: f,
          size: stat.size,
          date: stat.mtime,
          download: `/api/download/${encodeURIComponent(f)}`
        };
      })
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, limit);
    res.json({ files });
  } catch (err) {
    res.json({ files: [], error: err.message });
  }
});

// ─── API: Delete from history ─── NUEVO
app.delete('/api/history/:filename', (req, res) => {
  const filename = decodeURIComponent(req.params.filename);
  if (/[\/\\]|\.\./.test(filename) || !/\.pdf$/i.test(filename) || filename.startsWith('_stamped_')) {
    return res.status(400).json({ error: 'Nombre invalido' });
  }
  const filePath = path.join(outputDir, filename);
  if (!path.resolve(filePath).startsWith(path.resolve(outputDir))) {
    return res.status(403).json({ error: 'Acceso denegado' });
  }
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'No existe' });
  try {
    fs.unlinkSync(filePath);
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Error handler para multer (FIX: respuestas claras)
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(413).json({ error: 'El archivo supera los 15 MB' });
    }
    return res.status(400).json({ error: err.message });
  }
  if (err) return res.status(500).json({ error: err.message || 'Error interno' });
  next();
});

// FIX #6: Manejo de puerto ocupado
// FIX: Detectar si se lanza desde VBS (no abrir navegador duplicado)
const SKIP_BROWSER = process.env.ARTESBUHO_NO_BROWSER === '1';

const server = app.listen(PORT, HOST, () => {
  console.log('');
  console.log('  ╔══════════════════════════════════════════╗');
  console.log('  ║   ARTES BUHO — Firma Digital             ║');
  console.log('  ║   dev: RUBEN COTON                       ║');
  console.log('  ╠══════════════════════════════════════════╣');
  console.log('  ║   100% portatil — sin instalaciones      ║');
  console.log('  ║   Usa certificados de Windows            ║');
  console.log(`  ║   http://${HOST}:${PORT}              ║`);
  console.log('  ╚══════════════════════════════════════════╝');
  console.log('');
  if (!SKIP_BROWSER) {
    const { exec: run } = require('child_process');
    setTimeout(() => run(`start http://${HOST}:${PORT}`, { windowsHide: true }), 800);
  }
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`\n  [ERROR] El puerto ${PORT} ya esta en uso.`);
    console.error('  Cierra la otra instancia de ARTES BUHO o usa otro puerto.\n');
    process.exit(1);
  }
  throw err;
});

// FIX SEC-03: Manejo global — log y salida limpia
process.on('uncaughtException', (err) => {
  console.error('[FATAL]', err.stack || err.message);
  // No salir en uncaughtException de red (EPIPE, ECONNRESET)
  if (err.code === 'EPIPE' || err.code === 'ECONNRESET') return;
  setTimeout(() => process.exit(1), 500);
});
process.on('unhandledRejection', (err) => {
  console.error('[PROMISE]', err?.stack || err?.message || err);
});
