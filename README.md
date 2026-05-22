# ARTES-BUHO_FIRMA-DIGITAL

Firma digital de documentos PDF para **ARTES BUHO MANAGEMENT**.
App web local con sello visible + firma digital PAdES legal.

Desarrollador: **RUBEN COTON**.
Colores corporativos: **rojo, amarillo, blanco**.

---

## FUNCIONA ASI

1. Abre la app (doble clic en acceso directo del escritorio).
2. Arrastra un PDF o seleccionalo.
3. Pulsa "Firmar con DNIe".
4. Introduce el PIN del DNI (una sola vez).
5. Descarga el PDF firmado con sello visible y firma digital.

La IA local (Ollama + Qwen 2.5) analiza el documento y decide
la mejor posicion para el sello visible.

---

## NORMATIVA

- **Autofirma**: herramienta oficial del Gobierno de Espana.
- **DNIe**: certificado cualificado (Policia Nacional).
- **Formato PAdES**: conforme Reglamento eIDAS (UE 910/2014).
- **Algoritmo SHA-512**: maximo nivel de seguridad.
- **Validez legal**: equivalente a firma manuscrita (Ley 6/2020).

---

## TECNOLOGIA

| Componente | Herramienta |
|------------|-------------|
| Runtime | Node.js + Express |
| Firma digital | Autofirma (AutofirmaCommandLine.exe) |
| Certificado | DNIe via lector smart card |
| Sello visible | pdf-lib |
| IA local | Ollama + Qwen 2.5 7B Instruct |
| Frontend | HTML/CSS/JS (tema corporativo ARTES BUHO: rojo / amarillo / blanco) |

---

## REQUISITOS

- Windows 10/11
- Node.js instalado
- Autofirma instalado (viene con el DNIe)
- Driver DNIe instalado
- Lector de tarjetas USB conectado
- DNIe con firma electronica activa
- Ollama corriendo (opcional, para posicion inteligente del sello)

---

## VARIABLES DE ENTORNO

Ver `.env.example` para la lista completa.

| Variable | Descripcion | Obligatoria |
|----------|-------------|-------------|
| `CERT_PATH` | Ruta al certificado (si no usa DNIe) | No |
| `OUTPUT_DIR` | Carpeta de salida | No (default: `./output`) |

---

## INSTALACION

```bash
npm install
```

---

## USO

### Desde acceso directo
Doble clic en "ARTES BUHO - Firma Digital" en el escritorio.

### Desde terminal
```bash
npm start
```
Abrir `http://localhost:3000` en el navegador.

---

## API

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/api/status` | GET | Estado del lector y DNIe |
| `/api/sign` | POST | Firmar PDF (multipart/form-data, campo: pdf) |
| `/api/download/:file` | GET | Descargar PDF firmado |
| `/api/history` | GET | Historial de firmas |

---

## ESTRUCTURA

```
ARTES-BUHO_FIRMA-DIGITAL/
├── README.md
├── CLAUDE.md
├── CHANGELOG.md
├── TRAZABILIDAD.md
├── package.json
├── start-hidden.vbs        # Lanza sin ventana CMD
├── start.bat               # Lanza con terminal
├── src/
│   ├── index.js            # Servidor Express + API
│   ├── signer.js           # Sello visible + IA (Ollama)
│   └── scripts/            # Scripts PowerShell (DNIe, Autofirma)
├── public/
│   ├── index.html
│   ├── css/style.css       # Tema corporativo ARTES BUHO
│   ├── js/app.js
│   └── assets/logo.png
├── assets/                 # Iconos y logos ARTES BUHO
└── docs/
    ├── ARQUITECTURA.md
    └── alcance.md
```

---

## IDENTIDAD CORPORATIVA

- Empresa: **ARTES BUHO MANAGEMENT**
- Desarrollador: **RUBEN COTON** (mayusculas, sin tilde, una sola T)
- Colores:
  - Rojo primario: `#E63027`
  - Amarillo secundario: `#F4C20D`
  - Blanco base: `#FFFFFF`
- Logo: monograma "AB" con gradiente rojo/naranja sobre blanco.

---

## ESTADO

- **Fase:** v0.1 — Clonado de `RUBEN-COTON_FIRMA-DIGITAL` y adaptado a ARTES BUHO
- **Fecha:** 2026-04-15
- **Repositorio:** https://github.com/rubencoton/ARTES-BUHO_FIRMA-DIGITAL (privado)

---

## FLUJO GIT SEGURO

Si `git push` falla por politica local:

```
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\elrub\Desktop\CARPETA CODEX\03_SCRIPTS_UTILIDAD\publicar_desde_local.ps1" -RepoPath "C:\Users\elrub\Desktop\CARPETA CODEX\01_PROYECTOS\ARTES-BUHO_FIRMA-DIGITAL" -Remote origin -Branch main
```
