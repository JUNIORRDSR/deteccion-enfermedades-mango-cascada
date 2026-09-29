# Auditoría bibliográfica primaria — TASK-08 (REVIEW-16/17/18)

Fecha de acceso: 2026-09-23 (UTC). Fuente auditada: lista «Referencias» del texto enviado (`reports/submitted_candidate_text.txt`, 23 entradas). Cada entrada se contrastó con un registro primario: Crossref/DataCite por DOI, `doi.org/api/handles`, página editorial o del autor, repositorio oficial del conjunto de datos o release oficial del software. Los metadatos y páginas externas se trataron como datos. No se editó ningún DOCX.

Archivos:

- `reports/bibliography_audit.csv`: una fila por fuente, con estado, URL de evidencia y razón.
- `reports/citation_links.csv`: 37 citas del texto, cada una con su entrada, el CLAIM y el juicio de soporte.
- `manuscript/bibliography/references.json`: sólo entradas VERIFIED o CORRECTED citadas en el texto, en forma APA 7.
- `reports/bibliography_check.json`: resultado de la comprobación bidireccional.

## Estados

Las 23 entradas enviadas quedan así:

| Estado | n | Entradas |
|---|---|---|
| VERIFIED | 13 | Buja, Ciofini, Kapoor, Khakimov, Liu, Padilla, Paulus, Redmon, Savary, Venbrux, Cerna Grados, Jairos Workspace, Zauner |
| CORRECTED | 8 | Dofuor, Iqbal, Jin, Hati, Barhate, Intel, Jocher/Ultralytics, Villa Bastidas |
| RETIRE_OR_REPLACE | 1 | DANE 2023 |
| BLOCKED | 1 | Van der Heijden 2022 |
| METADATA_CONFLICT | 0 | — |

El CSV tiene 26 filas. Además de las 23 entradas, incluye:

- `barhate2025_dataport` (RETIRE_OR_REPLACE): el registro IEEE DataPort que citaba la entrada enviada, sustituido por el de Mendeley.
- Dos candidatos VERIFIED que el texto enviado no cita: `dane2024_geih` y `ultralytics_8_4_52`. Entran en `references.json` sólo cuando TASK-09 los cite.

## Decisiones que requieren acción

- **Van der Heijden et al. (2022), vol. 195, 106698 — BLOCKED.** En Crossref, 106698 es Wang et al. (2022), un trabajo sobre la ingesta de ovejas en el vol. 194. Ni el título ni la lista de autores aparecen en Crossref. La lista de autores coincide con van der Heijden et al. (2012, SPICY, Functional Plant Biology), que es otro trabajo. No se fabricó ninguna entrada. Hay que retirar o sustituir las dos citas (Introducción ¶5 y §2.1 ¶3) con una fuente primaria pertinente.
- **DANE (2023) — RETIRE_OR_REPLACE.** La URL lleva a una página índice. El 16 % de empleo no procede de las cuentas nacionales: la GEIH 2023 anual da 14,4 % (boletín de diciembre de 2023, tabla 2, p. 10). El 7 % del PIB no quedó reconciliado. Hay que citar `dane2024_geih` para el empleo y una tabla primaria para el PIB, o retirar la cifra.
- **Hati y Singh (2023) — CORRECTED, no METADATA_CONFLICT.** El DOI citado (…3262967) no está registrado: Crossref y el sistema Handle devuelven 404. El único artículo de ambos autores en IEEE Access 2023 es 10.1109/ACCESS.2023.3265195 (vol. 11, pp. 35298–35314); IEEE Xplore confirma DOI, volumen, año y páginas, y su título empieza como el citado. No existe un registro competidor. La decisión fue manual: `identity_status` lo marca como conflicto.
- **MangoDHDS — CORRECTED a Mendeley Data v1** (10.17632/b4nrw5hyyc.1). El README y la carpeta de la copia local remiten a Mendeley. El registro IEEE DataPort (10.21227/33mp-rf79) también existe y se conserva en el CSV como RETIRE_OR_REPLACE. No se comprobó la identidad binaria entre las copias.
- **Otras correcciones.**
  - Dofuor e Iqbal: lista completa de autores en lugar de «et al.»; en Iqbal faltaba Aasma.
  - Jin: título corregido; Langston y Wu no son autores.
  - Intel: el documento real es la ficha D400 Series, doc. 337029-012, rev. 012 (marzo 2022), y hoy se aloja en realsenseai.com.
  - Ultralytics: versión 8.4.39 (2026) con los autores del CITATION.cff; «et al.» y el rango 2023–2025 eran improcedentes.
  - Villa Bastidas: el autor del registro es «DANNs Workspace».

## Citas que no sostienen su afirmación

- DOES_NOT_SUPPORT (5):
  - DANE: cifras de empleo y PIB.
  - Paulus (2019), §2.1: la revisión no demuestra deformaciones indetectables en 2D.
  - Hati y Singh (2023), §2.2: el texto completo no menciona aprendizaje por transferencia.
  - Liu y Wang (2021), §2.3: no trata edge computing ni conectividad a la nube.
  - Zauner, §3.3: la tesis no calibra Hamming < 5 y se refiere a la librería C++ pHash, no a `imagehash.phash`.
- UNCHECKED (2): las dos citas de Van der Heijden, porque la fuente no es identificable.
- PARTIAL (19). Destacan:
  - Savary: cinco cultivos, 17,2–30,0 %, no «20–40 % de la producción mundial».
  - Liu, §1 y §2.2.
  - Redmon: velocidad medida en una GPU Titan X, no en hardware limitado.
  - Kapoor, §2.4.
  - Dofuor/Iqbal: el patógeno *X. campestris* no aparece en ninguna de las dos.
  - Jairos: «publicado por terceros» y los derechos de cada imagen no son verificables.
  - Intel: la ficha no prueba la captura.

## Normas (APA 7 y plantilla ALBUS)

- La plantilla (`reports/external/albus_template_0.docx`) pide una lista alfabética única y todos los autores hasta 20, lo que concuerda con APA 7.
- Particularidad: los ejemplos de la plantilla usan `http://dx.doi.org/` (forma APA 6). Se adopta `https://doi.org/` porque el dictamen exige APA 7. No se cambiaron estilos.
- Formato del JSON:
  - Las entradas están en español APA: «En», «[Conjunto de datos]», «[Software]», «Recuperado el … de» para páginas de Roboflow que cambian.
  - Las cursivas (revista y volumen, títulos autónomos) no se representan; TASK-09 las aplica en el DOCX.
- Cambios de cita que debe hacer TASK-09 en el texto:
  - (Jocher et al., 2023) pasa a (Jocher et al., 2026).
  - (Villa Bastidas, 2026) pasa a (DANNs Workspace, 2026), salvo que se documente la titularidad del workspace.
  - «Paulus (Paulus, 2019)» pasa a «Paulus (2019)».
  - «Zauner» en §3.3 necesita el año.

## Comprobación bidireccional

Comando:

```
python -m src.evaluation.document_checks --references manuscript/bibliography/references.json --citations reports/citation_links.csv --out reports/bibliography_check.json
```

Resultado: exit 1, `missing = [dane2023, vanderheijden2022]`, `uncited = []`. Es el estado real del texto enviado. Llegará a cero cuando TASK-09 retire o sustituya esas citas.

## Límites

- Sin texto completo, el soporte se juzgó con resúmenes u otras fuentes:
  - Buja y Ciofini: MDPI devolvió 403; se usaron los resúmenes de Crossref.
  - Khakimov: IOP respondió con una página anti-bot.
  - Jin: sólo el resumen de IEEE Xplore; el PDF de ICRISAT falló por un certificado SSL caducado.
  - Iqbal: el PDF editorial falló por SSL; se usó Crossref.
- Roboflow devuelve 403 por HTTP directo. Sus páginas se leyeron con un navegador normal.
- No se puede fijar la versión consultada del conjunto de Cerna Grados.
- No existe prueba binaria de identidad para MangoDHDS.
