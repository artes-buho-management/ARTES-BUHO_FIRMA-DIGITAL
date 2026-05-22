# CLAUDE.md — ARTES-BUHO_FIRMA-DIGITAL

## Objetivo

Firma digital legal (PAdES / eIDAS) de documentos de ARTES BUHO MANAGEMENT:
contratos de booking, riders, cesiones, acuerdos con artistas.

## Reglas especificas

1. NO commitear certificados, claves privadas ni PINs.
2. NO loggear PINs ni contenido sensible de contratos.
3. Todo PDF firmado debe quedar trazado: quien, cuando, hash del original y del firmado.
4. Usar Autofirma o motor equivalente validado. No inventar criptografia propia.
5. Algoritmo minimo: SHA-256. Preferente: SHA-512.
6. Sello visible obligatorio en contratos externos.
7. Guardado final en Drive via `ARTES-BUHO_API-GOOGLE` (cuenta `booking@artesbuhomanagement.com`).

## Firmantes previstos

| Firmante | Certificado | Uso |
|----------|-------------|-----|
| Ruben Coton (representante legal) | DNIe | Firma en nombre de ARTES BUHO |
| ARTES BUHO MANAGEMENT | Cert. representante persona juridica | Cuando este emitido |

## Estructura

- `src/` — servidor + logica de firma
- `public/` — UI
- `scripts/` — utilidades
- `config/` — plantillas de sello y posicionamiento
- `docs/` — doc tecnica y legal
- `tests/` — pruebas
- `assets/` — logos, sellos
- `uploads/` / `output/` — ignorados en git

## Dependencias

- `ARTES-BUHO_API-GOOGLE` — Drive / Gmail como canal de entrada y salida.
- `APP_ARTES-BUHO_CRM-CENTRAL` — trazabilidad del documento por artista / evento.

## Seguridad

- `.env` para variables locales, ignorado en git.
- Script Properties si hay parte Apps Script.
- Nunca pegar el PIN en logs, issues ni commits.
