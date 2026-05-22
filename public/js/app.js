document.addEventListener('DOMContentLoaded', () => {
  const menuItems = document.querySelectorAll('.menu-item');
  const views = document.querySelectorAll('.view');
  const uploadZone = document.getElementById('uploadZone');
  const fileInput = document.getElementById('fileInput');
  const fileInfo = document.getElementById('fileInfo');
  const fileName = document.getElementById('fileName');
  const fileSize = document.getElementById('fileSize');
  const btnRemove = document.getElementById('btnRemove');
  const btnSign = document.getElementById('btnSign');
  const result = document.getElementById('result');
  const resultMessage = document.getElementById('resultMessage');
  const btnDownload = document.getElementById('btnDownload');
  const btnSignAnother = document.getElementById('btnSignAnother');
  const loading = document.getElementById('loading');
  const loadingStep = document.getElementById('loadingStep');
  const statusDot = document.getElementById('statusDot');
  const toastContainer = document.getElementById('toastContainer');

  const noCertModal = document.getElementById('noCertModal');
  const noCertClose = document.getElementById('noCertClose');
  let noCertShown = false;

  let selectedFile = null;
  let signing = false;

  // XSS sanitizer
  function esc(str) {
    const d = document.createElement('div');
    d.textContent = str == null ? '' : String(str);
    return d.innerHTML;
  }

  // Toast notifications (reemplaza alert())
  function toast(message, type = 'info', duration = 5000) {
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.innerHTML = `
      <span class="toast-msg">${esc(message)}</span>
      <button class="toast-close" aria-label="Cerrar">&times;</button>
    `;
    toastContainer.appendChild(el);
    const remove = () => { el.classList.add('toast-out'); setTimeout(() => el.remove(), 250); };
    el.querySelector('.toast-close').addEventListener('click', remove);
    setTimeout(remove, duration);
  }

  // Navigation
  menuItems.forEach(item => {
    item.addEventListener('click', () => {
      const view = item.dataset.view;
      menuItems.forEach(m => m.classList.remove('active'));
      views.forEach(v => v.classList.remove('active'));
      item.classList.add('active');
      document.getElementById(`view-${view}`).classList.add('active');
      if (view === 'history') loadHistory();
      if (view === 'status') loadStatus();
    });
  });

  // Upload zone
  uploadZone.addEventListener('click', () => fileInput.click());

  uploadZone.addEventListener('dragover', e => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });

  uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
  });

  uploadZone.addEventListener('drop', e => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 1) {
      toast('Solo se permite firmar un archivo a la vez. Se procesara el primero.', 'info');
    }
    const file = files[0];
    if (file && file.type === 'application/pdf') {
      selectFile(file);
    } else if (file) {
      toast('Solo se permiten archivos PDF', 'error');
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) selectFile(fileInput.files[0]);
  });

  function selectFile(file) {
    if (file.size > 15 * 1024 * 1024) {
      toast('El archivo supera los 15 MB. Reduce el tamano del PDF.', 'error');
      return;
    }
    if (file.size === 0) {
      toast('El archivo esta vacio', 'error');
      return;
    }
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatSize(file.size);
    uploadZone.classList.add('hidden');
    fileInfo.classList.remove('hidden');
    result.classList.add('hidden');
  }

  btnRemove.addEventListener('click', () => {
    if (signing) return;
    resetToUploadView();
  });

  function resetToUploadView() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    uploadZone.classList.remove('hidden');
    result.classList.add('hidden');
    loading.classList.add('hidden');
  }

  // FIX UX-01: Boton "Firmar otro documento"
  if (btnSignAnother) {
    btnSignAnother.addEventListener('click', resetToUploadView);
  }

  // Sign
  btnSign.addEventListener('click', async () => {
    if (!selectedFile || signing) return;

    signing = true;
    btnSign.disabled = true;
    btnSign.textContent = 'Firmando...';
    fileInfo.classList.add('hidden');
    loading.classList.remove('hidden');
    if (loadingStep) loadingStep.textContent = 'Esperando seleccion de certificado...';
    result.classList.add('hidden');

    const formData = new FormData();
    formData.append('pdf', selectedFile);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 240000); // 4 min (cert picker puede tardar)

    // Indicador de progreso aproximado
    let stepTimer = setTimeout(() => {
      if (loadingStep) loadingStep.textContent = 'Generando sello y estructura PAdES...';
    }, 4000);
    let stepTimer2 = setTimeout(() => {
      if (loadingStep) loadingStep.textContent = 'Aplicando firma digital...';
    }, 12000);

    try {
      const res = await fetch('/api/sign', {
        method: 'POST',
        body: formData,
        signal: controller.signal
      });

      clearTimeout(timeout);
      clearTimeout(stepTimer);
      clearTimeout(stepTimer2);

      let data;
      try {
        data = await res.json();
      } catch (parseErr) {
        throw new Error('Respuesta invalida del servidor');
      }

      loading.classList.add('hidden');

      if (data.ok) {
        resultMessage.textContent = `Firmado por ${data.signer || 'certificado digital'} | ${data.format || 'PAdES'} | ${data.signDate || ''}`;
        btnDownload.href = data.output.path;
        btnDownload.download = data.output.filename;
        result.classList.remove('hidden');
        selectedFile = null;
        fileInput.value = '';

        toast('Documento firmado correctamente', 'success');
        if (Array.isArray(data.warnings)) {
          data.warnings.forEach(w => toast(w, 'warn', 8000));
        }
      } else {
        toast(data.error || 'Error al firmar el documento', 'error', 7000);
        fileInfo.classList.remove('hidden');
      }
    } catch (err) {
      clearTimeout(timeout);
      clearTimeout(stepTimer);
      clearTimeout(stepTimer2);
      loading.classList.add('hidden');

      if (err.name === 'AbortError') {
        toast('Tiempo de espera agotado. ¿Se abrio el selector de certificados?', 'error', 8000);
      } else {
        toast(err.message || 'Error de conexion con el servidor', 'error', 7000);
      }
      fileInfo.classList.remove('hidden');
    } finally {
      signing = false;
      btnSign.disabled = false;
      btnSign.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        Firmar con certificado digital
      `;
    }
  });

  // History
  async function loadHistory() {
    const list = document.getElementById('historyList');
    try {
      const res = await fetch('/api/history');
      const data = await res.json();

      if (!data.files || !data.files.length) {
        list.innerHTML = '<p class="empty-state">No hay documentos firmados todavia</p>';
        return;
      }

      list.innerHTML = data.files.map(f => `
        <div class="history-item" data-name="${esc(f.name)}">
          <svg class="file-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <div class="file-info-inline">
            <span class="name">${esc(f.name)}</span>
            <span class="meta">${formatSize(f.size)} — ${new Date(f.date).toLocaleString('es-ES')}</span>
          </div>
          <a class="btn-dl" href="${esc(f.download)}" download="${esc(f.name)}">Descargar</a>
          <button class="btn-del" title="Eliminar del historial" data-del="${esc(f.name)}">&times;</button>
        </div>
      `).join('');

      // Wire up delete buttons
      list.querySelectorAll('.btn-del').forEach(btn => {
        btn.addEventListener('click', async () => {
          const name = btn.dataset.del;
          if (!confirm(`¿Eliminar "${name}" del historial?`)) return;
          try {
            const res = await fetch(`/api/history/${encodeURIComponent(name)}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.ok) {
              toast('Documento eliminado del historial', 'success');
              loadHistory();
            } else {
              toast(data.error || 'Error al eliminar', 'error');
            }
          } catch {
            toast('Error de conexion', 'error');
          }
        });
      });
    } catch {
      list.innerHTML = '<p class="empty-state">Error al cargar el historial</p>';
    }
  }

  // Status
  async function loadStatus() {
    const cards = document.getElementById('statusCards');
    try {
      const res = await fetch('/api/status');
      const data = await res.json();

      cards.innerHTML = `
        <div class="status-card">
          <h3>Certificado digital</h3>
          <div class="value ${data.certificate ? 'ok' : 'error'}">
            ${data.certificate ? 'Disponible' : 'No detectado'}
          </div>
          ${data.certificate?.subject ? `<div class="detail"><strong>${esc(data.certificate.subject)}</strong></div>` : ''}
          ${data.certificate?.issuer ? `<div class="detail">Emisor: ${esc(data.certificate.issuer)}</div>` : ''}
          ${data.certificate?.validUntil ? `<div class="detail">Valido hasta: ${esc(data.certificate.validUntil)}</div>` : ''}
          ${data.certificate?.count > 1 ? `<div class="detail">${data.certificate.count} certificados disponibles</div>` : ''}
          ${!data.certificate ? '<div class="detail">Instala un certificado digital (FNMT, DNIe, etc.) para poder firmar</div>' : ''}
        </div>
        <div class="status-card">
          <h3>Motor de firma</h3>
          <div class="value ok">Integrado</div>
          <div class="detail">Firma con almacen de certificados de Windows</div>
          <div class="detail">Formato: PAdES (eIDAS)</div>
          <div class="detail">Algoritmo: SHA-256</div>
        </div>
        <div class="status-card">
          <h3>Servidor</h3>
          <div class="value ok">Activo</div>
          <div class="detail">localhost:3000</div>
          <div class="detail">Solo accesible desde este equipo</div>
        </div>
      `;
    } catch {
      cards.innerHTML = '<p class="empty-state">Error al consultar el estado</p>';
    }
  }

  // Modal sin certificado
  noCertClose.addEventListener('click', () => noCertModal.classList.add('hidden'));
  noCertModal.addEventListener('click', (e) => {
    if (e.target === noCertModal) noCertModal.classList.add('hidden');
  });

  async function checkConnection() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      const dot = statusDot.querySelector('.dot');
      const text = statusDot.querySelector('.status-text');

      if (data.ok) {
        dot.className = 'dot connected';
        text.textContent = data.certificate?.subject
          ? data.certificate.subject.substring(0, 22)
          : 'Certificado OK';
        noCertModal.classList.add('hidden');
      } else {
        dot.className = 'dot disconnected';
        text.textContent = 'Sin certificado';
        if (!noCertShown) {
          noCertShown = true;
          noCertModal.classList.remove('hidden');
        }
      }
    } catch {
      const dot = statusDot.querySelector('.dot');
      const text = statusDot.querySelector('.status-text');
      dot.className = 'dot disconnected';
      text.textContent = 'Sin conexion';
    }
  }

  checkConnection();
  // FIX UX-04: polling cada 60s (antes 15s)
  setInterval(checkConnection, 60000);

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }
});
