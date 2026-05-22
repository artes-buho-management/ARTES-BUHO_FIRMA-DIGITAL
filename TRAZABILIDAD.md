# TRAZABILIDAD — ARTES-BUHO_FIRMA-DIGITAL

Historial de decisiones y cambios relevantes del proyecto.

---

## 2026-04-15 — Rebranding ARTES BUHO

**Decision:** Adaptar UI, textos y marca del proyecto clonado a ARTES BUHO MANAGEMENT.

**Cambios:**
- `package.json` renombrado a `artes-buho-firma-digital`.
- `README.md` adaptado: empresa ARTES BUHO, desarrollador RUBEN COTON (mayusculas, sin tilde, una T).
- `public/index.html`: titulo "ARTES BUHO - Firma Digital", sidebar con marca dual (ARTES BUHO + FIRMA DIGITAL).
- `public/css/style.css`: paleta corporativa rojo (#E63027) + amarillo (#F4C20D) + blanco.
- Tema visual: sidebar rojo con acentos amarillos, contenido blanco / rosa muy claro.

**Pendiente:** sustituir `assets/icon.*` y `public/assets/icon.png` por el logo oficial "AB" facilitado por el cliente.

---

## 2026-04-15 — Clonado desde RUBEN-COTON_FIRMA-DIGITAL

**Decision:** Usar como base el proyecto personal de firma digital (DNIe + Autofirma + pdf-lib) y adaptarlo al uso de ARTES BUHO MANAGEMENT.

**Razon:** motor de firma ya probado y legalmente valido (PAdES / eIDAS). Evita reimplementar.

**Archivos copiados:** `src/`, `public/`, `assets/`, `docs/ARQUITECTURA.md`, `package.json`, `package-lock.json`, `start.bat`, `start-hidden.vbs`, `README.md`, `.env.example`, `TRAZABILIDAD.md`.

**No copiado:** `.git`, `node_modules`, `uploads/`, `output/`.

---

## 2026-04-15 — Creacion del repositorio

**Decision:** Crear proyecto `ARTES-BUHO_FIRMA-DIGITAL` para firma digital de contratos y documentacion legal de ARTES BUHO MANAGEMENT.

**Contexto:** agencia de booking / management de artistas necesita firma electronica legal (eIDAS) para contratos, riders, cesiones.

**Repositorio:** https://github.com/rubencoton/ARTES-BUHO_FIRMA-DIGITAL (privado)

---

<!-- Anadir nuevas entradas arriba de esta linea -->
