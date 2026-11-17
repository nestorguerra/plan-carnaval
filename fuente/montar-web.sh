#!/bin/sh
# Rehace index.html (el plan) y gantt.html (el diagrama) a partir de fuente/plan-annie.html.
# Uso, desde la raíz del repositorio:  sh fuente/montar-web.sh
set -e
T=$(mktemp -d)
python3 -I fuente/gantt.py fuente/plan-annie.html "$T/gantt-claude.html" "$T/gantt-suelto.html"
python3 -I fuente/montar.py "$T/gantt-suelto.html" gantt.html "$T/s1.html" "$T/g.js"
python3 -I fuente/montar.py fuente/plan-annie.html "$T/plan.html" "$T/s2.html" "$T/p.js"
sed 's#https://claude.ai/artifact/BBBahXtmdfSGG4FwMfyibP#gantt.html#g' "$T/plan.html" > index.html
rm -r "$T"
