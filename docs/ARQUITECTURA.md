# ARQUITECTURA — ARTES-BUHO_FIRMA-DIGITAL

## Componentes

1. **Lector de tarjetas** — Hardware USB para leer el DNIe
2. **Middleware PKCS#11** — Driver que conecta el lector con el sistema
3. **Firma PDF** — Logica Node.js para firmar documentos

## Decisiones tecnicas

> Pendiente: se documentaran aqui conforme avance el desarrollo.

## Flujo previsto

```
DNIe en lector → Middleware PKCS#11 → Certificado X.509 → Firma del PDF → PDF firmado
```
