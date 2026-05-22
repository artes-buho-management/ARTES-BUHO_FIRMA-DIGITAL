# Alcance funcional — ARTES-BUHO_FIRMA-DIGITAL

## Casos de uso

1. Firma de contrato de booking artista-promotor.
2. Firma de rider tecnico.
3. Firma de contrato de representacion artista-ARTES BUHO.
4. Firma de cesion de derechos (imagen, grabacion).
5. Firma de conformidades y justificantes.

## Flujo estandar

1. Entrada del PDF (subida manual o desde Drive).
2. Analisis del documento (opcional IA local para posicion del sello).
3. Sello visible con logo ARTES BUHO.
4. Firma PAdES con certificado (DNIe o representante juridico).
5. Guardado en Drive via `ARTES-BUHO_API-GOOGLE`.
6. Traza en CRM central por artista / evento.

## Fuera de alcance (de momento)

- Firma masiva no supervisada.
- Firma biometrica / grafometrica.
- Portal externo para que terceros firmen (fase 2).
