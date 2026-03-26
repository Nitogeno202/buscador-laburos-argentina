# 🔍 Buscador de Empleos — Argentina

Script de Python que scrapeá ofertas laborales de **LinkedIn** e **Indeed** y genera un informe en PDF listo para guardar o compartir.

---

## ¿Qué hace?

1. Te pregunta el puesto, la ubicación y cuántos resultados querés.
2. Scrapeá LinkedIn e Indeed en simultáneo usando `jobspy`.
3. Limpia y filtra los resultados (elimina entradas vacías o corruptas).
4. Genera un PDF prolijo con título, empresa, ubicación, fecha y link directo a cada oferta.

---

## Requisitos

- Python 3.8+
- Las siguientes librerías:

```bash
pip install python-jobspy reportlab
```

---

## Uso

```bash
python buscador_empleos.py
```

El script te va a pedir:

| Campo | Ejemplo | Default |
|---|---|---|
| Puesto | `administrador de sistemas` | — |
| Ubicación | `Buenos Aires` | `Argentina` |
| Resultados por fuente | `20` | `15` |

Al terminar, genera un archivo PDF en el mismo directorio con el nombre:

```
empleos_<puesto>_<fecha_hora>.pdf
```

---

## Estructura del PDF generado

- **Encabezado** con puesto, ubicación y fecha de generación
- **Resumen** con el total de resultados y desglose por fuente (LinkedIn / Indeed)
- **Listado de empleos** con:
  - Título del puesto
  - Empresa
  - Ubicación
  - Fecha de publicación
  - Link clickeable a la oferta original

---

## Ejemplo de salida

```
========================================
   BUSCADOR DE EMPLEOS - Argentina
========================================

¿Qué puesto estás buscando?: desarrollador backend
¿En qué ciudad/provincia?: Buenos Aires
¿Cuántos resultados querés por fuente?: 10

🔍 Buscando 'desarrollador backend' en Buenos Aires...

✅ Se encontraron 18 empleos válidos.
📄 Generando informe PDF...

✅ ¡Listo! El informe fue guardado en:
   /home/usuario/empleos_desarrollador_backend_20250326_1430.pdf
```

---

## Notas

- Las búsquedas se limitan a publicaciones de las últimas **72 horas** por defecto.
- Los links a las ofertas pueden expirar con el tiempo.
- Indeed puede devolver menos resultados que LinkedIn dependiendo del puesto y ubicación.
- Si no se encuentra ningún resultado, el PDF igual se genera con un mensaje informativo.

---

## Dependencias

| Librería | Uso |
|---|---|
| [`python-jobspy`](https://github.com/Bunsly/JobSpy) | Scraping de LinkedIn e Indeed |
| [`reportlab`](https://www.reportlab.com/) | Generación del PDF |
