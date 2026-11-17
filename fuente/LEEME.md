# Fuentes

- `plan-annie.html`: el plan de validación, semana a semana, con las casillas, el marcador y los guiones.
- `gantt.py`: monta el diagrama leyendo las tareas del plan, para que las dos páginas digan siempre lo mismo.
- `montar.py`: envuelve cada página en un documento HTML completo.
- `montar-web.sh`: rehace `index.html` y `gantt.html` en la raíz.

Las marcas se guardan en el navegador de cada persona (`localStorage`), y el plan y el diagrama las comparten porque están en la misma dirección.
