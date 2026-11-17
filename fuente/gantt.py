# Monta la web del Gantt a partir de la web del plan: las tareas, sus marcas y sus tiempos se leen de
# plan-annie.html, para que las dos páginas digan siempre lo mismo. Aquí solo se decide en qué plan y en
# qué fila va cada tarea.
#   python3 -I gantt.py <plan-annie.html> <salida-artifact.html> <salida-para-archivo-suelto.html>
import re, sys, html, json

plan_src, out_art, out_suelto = sys.argv[1:4]
P = open(plan_src, encoding='utf-8').read()
URL_PLAN = 'https://claude.ai/artifact/FXUGxj46k1jdkndoNebfba'
ARCHIVO_PLAN = 'index.html'

def plano(s):
    return html.unescape(re.sub(r'\s+', ' ', s)).strip()

def esc(s):
    return html.escape(s, quote=True)

# --- Semanas
SEM = []
for m in re.finditer(r'<details class="semana" id="s(\d+)" data-ini="([^"]+)" data-fin="([^"]+)" data-fechas="([^"]+)"[^>]*>\s*<summary>.*?<span class="tit">(.*?)</span>', P, re.S):
    SEM.append(dict(n=int(m[1]), ini=m[2], fin=m[3], fechas=m[4], tit=plano(m[5])))
assert [s['n'] for s in SEM] == list(range(1, 14)), 'semanas'

# --- Tareas de Annie y de Néstor, tal como están en el plan
T = {}
for m in re.finditer(r'<input type="checkbox" id="(w(\d+)(?:c|h|r|x\d))" data-t="a"( data-clave)?><span><b class="(?:clave|marca)">([^<]*)</b>(.*?)<small class="dato">(.*?)</small></span>', P, re.S):
    marca = plano(m[4])
    tipo = 'imp' if m[3] else ('hab' if marca == 'Hábito' else 'sp')
    T[m[1]] = dict(tipo=tipo, marca=marca, texto=plano(m[5]), dato=plano(m[6]), s=int(m[2]), pueblo=(marca == 'Si estás en el pueblo'), de='a')
N_ANNIE, N_NESTOR = len(re.findall(r'data-t="a"[ >]', P)), len(re.findall(r'data-t="p">', P))
assert len(T) == N_ANNIE, (len(T), N_ANNIE)
for m in re.finditer(r'<input type="checkbox" id="(s(\d+)p\d)" data-t="p"><span>(.*?)</span>', P, re.S):
    T[m[1]] = dict(tipo='nes', marca='Lo hace Néstor', texto=plano(m[3]), dato='', s=int(m[2]), pueblo=False, de='p')
assert len(T) == N_ANNIE + N_NESTOR, (len(T), N_ANNIE + N_NESTOR)

def propio(tipo, marca, texto, dato=''):
    return dict(tipo=tipo, marca=marca, texto=texto, dato=dato, pueblo=False, de='x')

T['VIERNES'] = propio('rut', 'Cada viernes', 'Un audio o una llamada con Néstor: le cuentas los tres atascos que más has visto y él te dice qué ha cambiado en el juego.', 'Desde donde estés · 15 min')
T['ESPERA'] = propio('esp', 'Esperas respuesta', 'Esta semana no hay tarea aquí. Pediste un sí o un no antes de Carnaval, y cualquiera de los dos es una respuesta.')
T['OBRA'] = propio('nes', 'Lo hace Néstor', 'El segundo pueblo sigue en construcción, con las horas apuntadas por etapa.')
T['m2'] = propio('hito', 'Fecha señalada', '29 de noviembre: rellenas el marcador por primera vez. Nombres en tu lista, personas vistas jugar y jugadores.', 'Se rellena en la web del plan')
T['m5'] = propio('hito', 'Fecha señalada', '20 de diciembre: segundo marcador. Mensajes enviados, personas vistas jugar, jugadores, el primer dato de cuántos vuelven y la cita con fecha.', 'Se rellena en la web del plan')
T['m8'] = propio('hito', 'Fecha señalada', '10 de enero: tercer marcador, el de después de Navidad.', 'Se rellena en la web del plan')
T['m12'] = propio('hito', 'Fecha señalada', '9 de febrero: el marcador de Carnaval. Aquí se ve a qué altura ha llegado cada meta.', 'Se rellena en la web del plan')
T['h6'] = propio('hito', 'Fecha señalada', 'Tu tarde de «Guareña en la pantalla»: entre el 26 y el 30 de diciembre, el día que elijas.')
T['h7'] = propio('hito', 'Fecha señalada', 'La reunión en el Ayuntamiento: el día que te la den, del 21 al 23 o del 28 al 30 de diciembre.')
T['h12'] = propio('hito', 'Fecha señalada', 'Carnaval de Guareña: del sábado 6 al martes 9 de febrero.')
T['h13'] = propio('hito', 'Fecha señalada', '14 de febrero: decisión. Seguir creciendo, dar otra vuelta o cambiar de rumbo.')

# Lo que Néstor tiene que haber dejado listo para que una tarea de Annie se pueda hacer
ANTES = {
    'w3c': ['s2p2'], 'w4h': ['s2p2'], 'w5h': ['s2p2'], 'w9h': ['s2p2'], 'w10h': ['s2p2'], 'w11h': ['s2p2'],
    'w3x2': ['s3p4'], 'w5c': ['s5p4'], 'w5x1': ['s5p4'], 'w6c': ['s5p4'], 'w8x1': ['s1p2'], 'w9c': ['s8p3'],
    'w10c': ['s1p1'], 'w11c': ['s9p1', 's10p1'], 'w11x1': ['s10p3'], 'w12c': ['s9p1', 's12p1'],
    'w2r': ['s2p4'], **{'w%dr' % n: ['s3p4'] for n in range(3, 13)},
    'm2': ['s1p2'], 'm5': ['s1p2'], 'm8': ['s1p2'], 'm12': ['s1p2'],
}

todas = lambda ids: {n: list(ids) for n in range(1, 14)}
GRUPOS = [
    dict(id='p1', eti='Plan 1', nombre='Llegar a la gente', meta='Meta: 300 personas que han jugado', filas=[
        ('Tu lista de 30', {1: ['w1c']}),
        ('Mensajes uno a uno', {3: ['w3c'], 4: ['w4h'], 5: ['w5h'], 9: ['w9h'], 10: ['w10h'], 11: ['w11h']}),
        ('Cómplices en el pueblo', {2: ['w2x1'], 11: ['w11x1']}),
        ('Que corra la voz', {5: ['w5x1'], 6: ['w6x1'], 7: ['w7x1']}),
        ('La tarde de Navidad', {5: ['w5c'], 6: ['w6c']}),
        ('Carnaval dentro del juego', {9: ['w9x1'], 11: ['w11c'], 12: ['w12c', 'w12x1', 'w12x2']}),
        ('Dar las gracias', {13: ['w13x1']}),
    ]),
    dict(id='p2', eti='Plan 2', nombre='Escuchar y mejorar', meta='Meta: 15 de cada 100 vuelven a la semana', filas=[
        ('Mirar jugar', {2: ['w2c'], 3: ['w3x1'], 6: ['w6x2'], 10: ['w10x1']}),
        ('Los viernes con Néstor', todas(['VIERNES'])),
        ('Historias para las misiones', {2: ['w2x2']}),
        ('Encuesta de tres preguntas', {8: ['w8c']}),
        ('El marcador', {2: ['m2'], 5: ['m5'], 8: ['m8', 'w8x1'], 12: ['m12']}),
    ]),
    dict(id='p3', eti='Plan 3', nombre='El Ayuntamiento de Guareña', meta='Meta: un compromiso por escrito', filas=[
        ('Dominio y correo', {1: ['w1x2']}),
        ('Pedir la cita', {4: ['w4c']}),
        ('Quién factura', {4: ['w4x1']}),
        ('La reunión', {7: ['w7c']}),
        ('La propuesta', {9: ['w9c'], 10: ['ESPERA'], 11: ['ESPERA'], 12: ['ESPERA']}),
    ]),
    dict(id='p4', eti='Plan 4', nombre='El segundo pueblo', meta='Meta: dentro del juego, con sus primeros 20 vecinos', filas=[
        ('Elegir pueblo y persona', {10: ['w10c']}),
        ('Néstor lo construye', {8: ['s8p1'], 9: ['OBRA'], 10: ['OBRA'], 11: ['s11p1']}),
    ]),
    dict(id='p5', eti='Plan 5', nombre='Gente joven en redes', meta='Meta: 100 jugadores que llegan desde las redes', filas=[
        ('Aprender de quien lo hace bien', {1: ['w1x3']}),
        ('Las cuentas', {1: ['w1x1']}),
        ('Dos vídeos a la semana', {**{n: ['w%dr' % n] for n in range(2, 13)}, 13: ['w13x2']}),
        ('Creadores de la zona', {9: ['w9x2']}),
    ]),
    dict(id='fin', eti='Al final', nombre='Decidir', meta='El 14 de febrero se mira a qué altura ha llegado cada meta', filas=[
        ('Revisión y decisión', {13: ['w13c']}),
    ]),
    dict(id='nestor', eti='Producto', nombre='Lo que Néstor deja listo', meta='Lo que tiene que estar hecho en el juego y en la web para que tus tareas salgan', filas=[
        ('Medir y no perder datos', {1: ['s1p1', 's1p2'], 2: ['s2p1']}),
        ('Un motivo para volver', {2: ['s2p3'], 3: ['s3p1'], 4: ['s4p1', 's4p2', 's4p3'], 5: ['s5p3']}),
        ('Entrar bien desde el móvil', {2: ['s2p2'], 3: ['s3p2'], 6: ['s6p1'], 7: ['s7p1', 's7p2']}),
        ('Crecer de pueblo en pueblo', {5: ['s5p1', 's5p2'], 9: ['s9p1', 's9p2']}),
        ('Vender', {1: ['s1p3'], 3: ['s3p3'], 8: ['s8p2'], 10: ['s10p1', 's10p2']}),
        ('Lo que te prepara para enviar', {2: ['s2p4'], 3: ['s3p4'], 5: ['s5p4'], 8: ['s8p3'], 10: ['s10p3']}),
        ('Arreglos y guardia', {6: ['s6p2'], 11: ['s11p2'], 12: ['s12p1']}),
    ]),
]

# Cada tarea del plan aparece una vez, en la semana que le toca
vistas, casa = {}, {}
for g in GRUPOS:
    for rot, celdas in g['filas']:
        for n, ids in celdas.items():
            for i in ids:
                if T[i]['de'] in 'ap':
                    assert i not in vistas, 'repetida ' + i
                    assert T[i]['s'] == n, 'semana de ' + i
                    vistas[i] = 1
                    casa[i] = (g, rot)
faltan = [i for i in T if T[i]['de'] in 'ap' and i not in vistas]
assert not faltan, faltan

PUEBLO = {3: 'Puente', 6: 'Navidad', 7: '', 12: 'Carnaval'}
ORDEN = ['imp', 'hab', 'hito', 'sp', 'nes', 'rut', 'esp']
UNE = ('hab', 'nes', 'rut', 'esp')
ITEMS = []

def tipo_de(ids):
    return min((T[i]['tipo'] for i in ids), key=ORDEN.index)

def tramo(n, rot, g, ids, ruta=False, viene=False, sigue=False):
    tipo = tipo_de(ids)
    tareas = []
    for i in ids:
        t = T[i]
        d = dict(tipo=t['tipo'], marca=t['marca'], texto=t['texto'], dato=t['dato'], id=i if t['de'] in 'ap' else '')
        if i in ANTES:
            d['antes'] = [dict(t=T[a]['texto'], s=T[a]['s']) for a in ANTES[i]]
        tareas.append(d)
    ITEMS.append(dict(s=n, fila=rot, plan=(g['eti'] + ' · ' + g['nombre']) if g else '', meta=g['meta'] if g else '', tareas=tareas))
    cls = ['tramo', 't-' + tipo]
    if viene: cls.append('viene')
    if sigue: cls.append('sigue')
    if tipo == 'sp' and all(T[i]['pueblo'] for i in ids): cls.append('en-pueblo')
    cuantas = '' if len(ids) == 1 else ' · %d tareas' % len(ids)
    titulo = 'S%d · %s · %s%s' % (n, rot, T[ids[0]]['marca'] if len(ids) == 1 else T[min(ids, key=lambda i: ORDEN.index(T[i]['tipo']))]['marca'], cuantas)
    voz = 'Semana %d, %s. %s. ' % (n, SEM[n - 1]['fechas'], rot) + ' / '.join('%s: %s' % (T[i]['marca'], T[i]['texto']) for i in ids)
    num = str(len(ids)) if len(ids) > 1 and tipo != 'hito' else ''
    extra = (' data-ruta="%d"' % n if ruta else '')
    pids = [i for i in ids if T[i]['de'] in 'ap']
    if pids:
        extra += ' data-ids="%s"' % ','.join(pids)
    return '<button type="button" class="%s" data-i="%d"%s title="%s" aria-label="%s"><span class="b">%s</span></button>' % (' '.join(cls), len(ITEMS) - 1, extra, esc(titulo), esc(voz), num)

def td(n, dentro=''):
    return '<td data-s="%d"%s>%s</td>' % (n, ' class="pueblo"' if n in PUEBLO else '', dentro)

def fila(rot, celdas, g, cls='fila', ruta=False):
    out = ['<tr class="%s"><th scope="row" class="rot">%s</th>' % (cls, esc(rot))]
    for n in range(1, 14):
        if n in celdas:
            tp = tipo_de(celdas[n])
            viene = tp in UNE and (n - 1) in celdas and tipo_de(celdas[n - 1]) == tp
            sigue = tp in UNE and (n + 1) in celdas and tipo_de(celdas[n + 1]) == tp
            if ruta:
                gg, rr = casa[celdas[n][0]]
                out.append(td(n, tramo(n, rr, gg, celdas[n], ruta=True)))
            else:
                out.append(td(n, tramo(n, rot, g, celdas[n], viene=viene, sigue=sigue)))
        else:
            out.append(td(n))
    out.append('</tr>')
    return ''.join(out)

def mes_ini(f):
    a = f.split('–')[0]
    return a if ' ' in a else a + ' ' + f.split(' ')[-1]

# --- Tabla
t = ['<table class="gantt"><caption class="oculto">El plan de Annie por semanas: cada fila es una acción y cada columna, una semana, de la S1 (17 de noviembre) a la S13 (14 de febrero).</caption>',
     '<colgroup><col class="c-rot"><col span="13"></colgroup><thead>',
     '<tr class="fases"><th class="rot esquina" rowspan="2" scope="col"><span class="eti">Acción</span></th>'
     '<th colspan="2" scope="colgroup">Arrancar</th><th colspan="3" scope="colgroup">Los primeros jugadores</th><th colspan="3" scope="colgroup">Navidad</th><th colspan="3" scope="colgroup">La propuesta y el segundo pueblo</th><th colspan="2" scope="colgroup">Carnaval y decisión</th></tr>',
     '<tr class="semanas">' + ''.join('<th scope="col" data-s="%d"%s><b>S%d</b><span>%s</span></th>' % (s['n'], ' class="pueblo"' if s['n'] in PUEBLO else '', s['n'], esc(mes_ini(s['fechas']))) for s in SEM) + '</tr>',
     '</thead>']

# Las tres filas de arriba: dónde estás, lo importante de cada semana y las fechas señaladas
banda = ['<tr class="fila banda"><th scope="row" class="rot">Ya estás en Guareña</th>']
for n in range(1, 14):
    if n in PUEBLO:
        cls = 'franja' + (' viene' if (n - 1) in PUEBLO else '') + (' sigue' if (n + 1) in PUEBLO else '')
        banda.append(td(n, '<span class="%s"><i>%s</i></span>' % (cls, esc(PUEBLO[n]))))
    else:
        banda.append(td(n))
banda.append('</tr>')
t.append('<tbody id="g-vista">' + ''.join(banda))
t.append(fila('Lo importante de cada semana', {n: ['w%dc' % n] for n in range(1, 14)}, None, cls='fila ruta', ruta=True))
t.append(fila('Fechas señaladas', {6: ['h6'], 7: ['h7'], 12: ['h12'], 13: ['h13']}, dict(eti='De un vistazo', nombre='Fechas señaladas', meta='')))
t.append('</tbody>')

regla = '<tr class="regla" aria-hidden="true"><th class="rot"></th>' + ''.join('<td data-s="%d"%s>S%d</td>' % (n, ' class="pueblo"' if n in PUEBLO else '', n) for n in range(1, 14)) + '</tr>'
for g in GRUPOS:
    t.append('<tbody class="grupo" id="g-%s"><tr class="plan"><th colspan="14" scope="rowgroup"><div class="pegado"><div><span class="eti">%s</span><h3>%s</h3><p class="para">%s</p></div>'
             '<button type="button" class="plegar" aria-expanded="true">Plegar</button></div></th></tr>' % (g['id'], esc(g['eti']), esc(g['nombre']), esc(g['meta'])))
    t.append(regla)
    for rot, celdas in g['filas']:
        t.append(fila(rot, celdas, g))
    t.append('</tbody>')
t.append('</table>')
TABLA = '\n'.join(t)

# --- Panel «Esta semana»
SEMJS = []
for s in SEM:
    c = T['w%dc' % s['n']]
    mas = sum(1 for i in T if T[i]['de'] == 'a' and T[i]['s'] == s['n']) - 1
    SEMJS.append(dict(n=s['n'], ini=s['ini'], fin=s['fin'], fechas=s['fechas'], tit=s['tit'], texto=c['texto'], dato=c['dato'], mas=mas))
def frase_mas(m):
    return 'Y, si puedes, 1 cosa más esta semana.' if m == 1 else 'Y, si puedes, %d cosas más esta semana.' % m
S1 = SEMJS[0]

CSS = r'''
/* El diagrama es la página: una tabla con las trece semanas en columnas y, en filas, cada plan con sus
   acciones. La primera columna se queda fija al deslizar hacia los lados. Cada tipo de tarea tiene su
   forma además de su color, y al tocar una barra se abre abajo la ficha con lo que hay que hacer. */
:root {
  --fondo: #eef0ec;
  --papel: #f8f9f6;
  --banda: #e2e5df;
  --tinta: #0c1122;
  --tinta-2: #4f587a;
  --linea: rgba(12, 17, 34, 0.16);
  --anil: #34489c;
  --sodio: #ffa94d;
  --sobre-sodio: #1a1203;
  --filo: #0c1122;
  --gris: #7d86a6;
  --sobre-gris: #0c1122;
  --vega: #2f6f55;
  --tinte-pueblo: rgba(47, 111, 85, 0.11);
  --tinte-hoy: rgba(255, 169, 77, 0.34);
  --panel: #0c1122;
  --sobre-panel: #eef0ec;
  --f-display: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --f-serif: "Instrument Serif", "Iowan Old Style", Georgia, serif;
  --f-mono: "Geist Mono", ui-monospace, "SF Mono", Menlo, monospace;
  --rot: 8.75rem;
  --sem: 3rem;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --fondo: #070a14;
    --papel: #0d1326;
    --banda: #151d36;
    --tinta: #eef0ec;
    --tinta-2: #9ba4c8;
    --linea: rgba(186, 198, 255, 0.18);
    --anil: #8fa2ff;
    --sodio: #ffa94d;
    --sobre-sodio: #1a1203;
    --filo: #ffa94d;
    --gris: #5d678f;
    --sobre-gris: #eef0ec;
    --vega: #8fc7ab;
    --tinte-pueblo: rgba(143, 199, 171, 0.13);
    --tinte-hoy: rgba(255, 169, 77, 0.24);
    --panel: #151d36;
    --sobre-panel: #eef0ec;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --fondo: #070a14;
  --papel: #0d1326;
  --banda: #151d36;
  --tinta: #eef0ec;
  --tinta-2: #9ba4c8;
  --linea: rgba(186, 198, 255, 0.18);
  --anil: #8fa2ff;
  --sodio: #ffa94d;
  --sobre-sodio: #1a1203;
  --filo: #ffa94d;
  --gris: #5d678f;
  --sobre-gris: #eef0ec;
  --vega: #8fc7ab;
  --tinte-pueblo: rgba(143, 199, 171, 0.13);
  --tinte-hoy: rgba(255, 169, 77, 0.24);
  --panel: #151d36;
  --sobre-panel: #eef0ec;
  color-scheme: dark;
}

*, *::before, *::after { box-sizing: border-box; }
body {
  background: var(--fondo);
  color: var(--tinta);
  font: 400 1rem/1.55 var(--f-display);
  -webkit-text-size-adjust: 100%;
  padding-block: 1.5rem 4rem;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
}
.hoja { max-width: 72rem; margin-inline: auto; display: flex; flex-direction: column; gap: 2.75rem; }
h1, h2, h3, h4, p, ul, ol, dl, dd { margin: 0; }
ul, ol { padding: 0; list-style: none; }
h1, h2, h3 { text-wrap: balance; }
a { color: var(--anil); text-underline-offset: 0.18em; }
a:focus-visible, button:focus-visible, [tabindex]:focus-visible { outline: 2px solid var(--anil); outline-offset: 2px; }
.oculto { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.eti { font: 500 0.72rem/1.4 var(--f-mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--tinta-2); }

.cabecera { display: flex; flex-direction: column; gap: 0.9rem; }
h1 { font: 800 clamp(2.2rem, 10vw, 3.6rem)/1.02 var(--f-display); letter-spacing: -0.02em; }
h1 em { font: italic 400 1.06em/1 var(--f-serif); letter-spacing: 0; color: var(--anil); }
.entrada { max-width: 42rem; font-size: 1.05rem; }
.entrada-mas { max-width: 42rem; color: var(--tinta-2); font-size: 0.95rem; }
h2 { font: 700 1.5rem/1.15 var(--f-display); letter-spacing: -0.01em; }
.bloque { display: flex; flex-direction: column; gap: 1.1rem; }
.bloque > p { max-width: 42rem; }

/* Esta semana */
.hoy { background: var(--panel); color: var(--sobre-panel); padding: 1.25rem 1.15rem 1.35rem; display: flex; flex-direction: column; gap: 0.7rem; }
.hoy .eti { color: var(--sodio); }
.hoy h2 { font-size: 1.7rem; }
.hoy p { max-width: 44rem; }
.hoy-dato { font: 500 0.72rem/1.4 var(--f-mono); letter-spacing: 0.03em; }
.hoy-hecho { color: var(--sodio); font-weight: 700; }
.boton { align-self: flex-start; display: inline-flex; align-items: center; min-height: 2.9rem; padding: 0.6rem 1.1rem; background: var(--sodio); color: var(--sobre-sodio); font: 700 1rem/1.2 var(--f-display); border: 0; border-radius: 0; cursor: pointer; }
.boton:focus-visible { outline-color: var(--sobre-panel); }
.clave, .marca { display: inline-block; font: 500 0.64rem/1 var(--f-mono); letter-spacing: 0.08em; text-transform: uppercase; padding: 0.22rem 0.38rem; margin-right: 0.4rem; vertical-align: 0.12em; }
.clave { background: var(--sodio); color: var(--sobre-sodio); }
.marca { border: 1px solid var(--tinta-2); color: var(--tinta-2); padding: calc(0.22rem - 1px) calc(0.38rem - 1px); }

/* Objetivo y planes */
.alturas { display: grid; grid-template-columns: minmax(0, 1fr); gap: 1.75rem 2rem; }
.altura { display: flex; flex-direction: column; gap: 0.3rem; min-width: 0; padding-top: 0.8rem; border-top: 2px solid var(--tinta); }
.altura h3 { font: 700 1.15rem/1.25 var(--f-display); }
.altura h3 a { color: inherit; text-decoration-color: var(--linea); }
.altura h3 a:hover { color: var(--anil); }
.altura .d { font-size: 0.94rem; line-height: 1.45; }
.altura .mide { color: var(--tinta-2); font-size: 0.86rem; margin-top: 0.4rem; }
.altura dl { display: flex; flex-direction: column; }
.altura dl div { display: grid; grid-template-columns: 3.6rem minmax(0, 1fr); gap: 0.6rem; align-items: baseline; padding-block: 0.4rem; border-top: 1px solid var(--linea); }
.altura dt { font: 500 0.68rem/1.4 var(--f-mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--tinta-2); }
.altura dd { font-size: 0.94rem; line-height: 1.3; font-variant-numeric: tabular-nums; }
.altura .meta dt { color: var(--tinta); }
.altura .meta dd { font-weight: 700; font-size: 1.02rem; }
.altura .sueno dd { font: italic 400 1.15rem/1.2 var(--f-serif); color: var(--anil); }

/* Leyenda */
.leyenda { display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: 0.15rem 2rem; }
.leyenda li { display: grid; grid-template-columns: 2.6rem minmax(0, 1fr); gap: 0.75rem; align-items: center; padding-block: 0.4rem; font-size: 0.92rem; line-height: 1.35; }
.leyenda li span.txt b { font-weight: 600; }
.muestra { display: flex; align-items: center; justify-content: center; height: 1.6rem; }
.muestra.tinte { border: 1px solid var(--linea); }
.muestra.tinte.pueblo { background: var(--tinte-pueblo); }
.muestra.tinte.ahora { background: var(--tinte-hoy); }

/* El diagrama */
.pista-mov { font-size: 0.86rem; color: var(--tinta-2); }
.lienzo { overflow-x: auto; container-type: inline-size; border-block: 2px solid var(--tinta); }
.gantt { border-collapse: separate; border-spacing: 0; table-layout: fixed; width: max(100%, calc(var(--rot) + 13 * var(--sem))); }
.gantt col.c-rot { width: var(--rot); }
.gantt th, .gantt td { padding: 0; text-align: left; font-weight: 400; vertical-align: middle; }
.gantt td { height: 2.9rem; border-left: 1px solid var(--linea); border-top: 1px solid var(--linea); }
.gantt .rot { position: sticky; left: 0; z-index: 2; background: var(--fondo); padding: 0.4rem 0.6rem 0.4rem 0; border-top: 1px solid var(--linea); font: 500 0.82rem/1.25 var(--f-display); overflow-wrap: anywhere; }
.gantt .pueblo { background: var(--tinte-pueblo); }
.gantt .es-hoy { background: var(--tinte-hoy); }
.gantt thead th { border-left: 1px solid var(--linea); }
.gantt thead .esquina { border-left: 0; border-top: 0; vertical-align: bottom; padding-bottom: 0.5rem; }
.fases th { padding: 0.55rem 0.3rem 0.35rem 0.4rem; font: 600 0.74rem/1.2 var(--f-display); vertical-align: bottom; }
.semanas th { padding: 0.35rem 0 0.45rem; text-align: center; border-top: 1px solid var(--linea); }
.semanas th b { display: block; font: 800 0.95rem/1.1 var(--f-display); letter-spacing: -0.01em; }
.semanas th span { display: block; font: 500 0.58rem/1.3 var(--f-mono); color: var(--tinta-2); }
.semanas th.es-hoy span { color: var(--tinta); }
.ruta .rot { font-weight: 700; }
.plan th { padding: 0; border-top: 2px solid var(--tinta); background: var(--fondo); }
.pegado { position: sticky; left: 0; width: 100%; width: min(100%, 100cqw); display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 0.75rem; align-items: end; padding: 1.3rem 0 0.6rem; }
.pegado h3 { font: 700 1.2rem/1.2 var(--f-display); }
.pegado .para { color: var(--tinta-2); font-size: 0.88rem; line-height: 1.35; }
.plegar { min-height: 2.5rem; padding: 0.4rem 0.7rem; font: 500 0.66rem/1 var(--f-mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--tinta); background: transparent; border: 1px solid var(--tinta-2); border-radius: 0; cursor: pointer; }
.plegar:hover { background: var(--tinta); color: var(--fondo); }
.regla td { height: 1.35rem; border-top: 0; text-align: center; font: 500 0.58rem/1.35rem var(--f-mono); color: var(--tinta-2); }
.regla .rot { border-top: 0; padding: 0; }

.tramo { display: flex; align-items: center; width: 100%; height: 2.9rem; padding: 0 3px; margin: 0; border: 0; border-radius: 0; background: none; color: inherit; cursor: pointer; }
.tramo.viene { padding-left: 0; }
.tramo.sigue { padding-right: 0; }
.tramo:focus-visible { outline-offset: -2px; }
.b { display: flex; align-items: center; justify-content: center; width: 100%; height: 1.5rem; font: 500 0.72rem/1 var(--f-mono); }
.t-imp .b { background: var(--sodio); color: var(--sobre-sodio); box-shadow: inset 0 0 0 1.5px var(--filo); }
.t-hab .b { background: var(--anil); color: var(--fondo); }
.t-sp .b { background: var(--fondo); color: var(--anil); box-shadow: inset 0 0 0 1.5px var(--anil); }
.t-sp.en-pueblo .b::before { content: ""; width: 0.45rem; height: 0.45rem; border-radius: 50%; background: var(--anil); }
.t-nes .b { height: 1.05rem; background: var(--gris); color: var(--sobre-gris); }
.t-rut .b { height: 0.35rem; background: var(--tinta-2); }
.t-esp .b { height: 0; border-top: 2px dashed var(--tinta-2); }
.t-hito .b { width: 0.95rem; height: 0.95rem; margin-inline: auto; background: var(--tinta); transform: rotate(45deg); }
.tramo:hover .b, .tramo.sel .b { outline: 2px solid var(--tinta); outline-offset: 2px; }
.hecho > .b { opacity: 0.5; }
.hecho > .b::after { content: "\2713"; font: 700 0.85rem/1 var(--f-display); }
.t-hito.hecho > .b::after, .t-rut.hecho > .b::after, .t-esp.hecho > .b::after { content: none; }
.franja { display: block; height: 1.5rem; border-block: 1.5px solid var(--vega); border-inline: 1.5px solid var(--vega); padding-left: 0.4rem; font: 500 0.62rem/calc(1.5rem - 3px) var(--f-mono); letter-spacing: 0.06em; text-transform: uppercase; color: var(--vega); white-space: nowrap; }
.franja.viene { border-left: 0; }
.franja.sigue { border-right: 0; }
.franja i { display: none; font-style: normal; }

/* Ficha */
.ficha { position: fixed; inset: auto 0 0; z-index: 20; max-height: 62vh; overflow-y: auto; background: var(--papel); border-top: 2px solid var(--tinta); padding-block: 1rem calc(1.1rem + env(safe-area-inset-bottom, 0px)); padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.ficha-dentro { max-width: 46rem; margin-inline: auto; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 0.3rem 1rem; align-items: start; }
.ficha h2 { font-size: 1.3rem; grid-column: 1; }
.ficha .eti { grid-column: 1; }
.ficha-plan { grid-column: 1 / -1; color: var(--tinta-2); font-size: 0.88rem; line-height: 1.35; }
.cerrar { grid-column: 2; grid-row: 1 / span 2; min-height: 2.75rem; padding: 0.4rem 0.8rem; font: 500 0.68rem/1 var(--f-mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--tinta); background: transparent; border: 1px solid var(--tinta); border-radius: 0; cursor: pointer; }
.cerrar:hover { background: var(--tinta); color: var(--papel); }
.ficha ul { grid-column: 1 / -1; display: flex; flex-direction: column; margin-top: 0.5rem; }
.ficha li { padding-block: 0.7rem; border-top: 1px solid var(--linea); display: flex; flex-direction: column; gap: 0.3rem; }
.ficha .dato { font: 500 0.7rem/1.4 var(--f-mono); letter-spacing: 0.03em; color: var(--tinta-2); }
.ficha .antes { font-size: 0.88rem; line-height: 1.4; color: var(--tinta-2); padding-left: 0.7rem; border-left: 2px solid var(--gris); }
.marcar { display: inline-flex; align-items: center; gap: 0.55rem; align-self: flex-start; min-height: 2.75rem; font-weight: 600; cursor: pointer; }
.marcar input { width: 1.4rem; height: 1.4rem; margin: 0; accent-color: var(--anil); cursor: pointer; }
.ficha-pie { grid-column: 1 / -1; font-size: 0.86rem; color: var(--tinta-2); padding-top: 0.6rem; border-top: 1px solid var(--linea); }
body.con-ficha .hoja { padding-bottom: 62vh; }

.pie { color: var(--tinta-2); font-size: 0.86rem; display: flex; flex-direction: column; gap: 0.4rem; max-width: 46rem; padding-top: 1.25rem; border-top: 1px solid var(--linea); }

@media (min-width: 40rem) {
  .alturas { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .altura:last-child:nth-child(odd) { grid-column: 1 / -1; }
}
@media (min-width: 48rem) {
  :root { --rot: 15rem; --sem: 3.4rem; }
  body { padding-block: 2.5rem 4rem; }
  .hoja { gap: 3.25rem; }
  .hoy { padding: 1.75rem 1.75rem 1.9rem; }
  .pista-mov { display: none; }
  .gantt .rot { font-size: 0.9rem; padding-right: 0.9rem; }
  .fases th { font-size: 0.82rem; }
  .semanas th span { font-size: 0.64rem; }
  .regla td { font-size: 0.62rem; }
  .franja i { display: inline; }
}
@media (min-width: 66rem) {
  .alturas { grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 1.75rem 1.25rem; }
  .altura:last-child:nth-child(odd) { grid-column: auto; }
}
'''

JS = r'''
(function () {
  var ITEMS = @@ITEMS@@;
  var SEM = @@SEM@@;
  function el(id) { return document.getElementById(id); }
  var lienzo = el('lienzo'), ficha = el('ficha'), ultimo = null, actual = null;
  var calma = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  // Unido al plan: los dos leen y escriben las mismas marcas en el navegador
  var UNIDO = @@UNIDO@@, LS_T = '388plan:tareas', panel = null;
  function leerT() { try { var v = JSON.parse(localStorage.getItem(LS_T) || '{}'); return v && typeof v === 'object' ? v : {}; } catch (e) { return {}; } }
  function guardarT(v) { try { localStorage.setItem(LS_T, JSON.stringify(v)); } catch (e) {} }
  var hechas = UNIDO ? leerT() : {};

  // La semana en curso, según la fecha de quien mira
  (function () {
    var d = new Date();
    function p(n) { return (n < 10 ? '0' : '') + n; }
    var hoy = d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
    SEM.forEach(function (s) { if (hoy >= s.ini && hoy <= s.fin) actual = s; });
    var eti = el('ahora-eti'), s = actual;
    if (!s && hoy < SEM[0].ini) { s = SEM[0]; if (eti) eti.textContent = 'Empieza el 17 de noviembre · S1'; }
    else if (!s) { s = SEM[SEM.length - 1]; if (eti) eti.textContent = 'El plan terminó el 14 de febrero'; }
    else if (eti) eti.textContent = 'Esta semana · S' + s.n + ' · ' + s.fechas;
    panel = s;
    var tx = el('ahora-texto');
    if (tx) {
      tx.textContent = '';
      var m = document.createElement('b'); m.className = 'clave'; m.textContent = 'Lo importante';
      tx.appendChild(m); tx.appendChild(document.createTextNode(s.texto));
    }
    if (el('ahora-titulo')) el('ahora-titulo').textContent = s.tit;
    if (el('ahora-dato')) el('ahora-dato').textContent = s.dato;
    if (el('ahora-mas')) { el('ahora-mas').hidden = !s.mas; el('ahora-mas').textContent = s.mas === 1 ? 'Y, si puedes, 1 cosa más esta semana.' : 'Y, si puedes, ' + s.mas + ' cosas más esta semana.'; }
    var ver = el('ahora-ver');
    if (ver) ver.setAttribute('data-s', s.n);
    if (actual && lienzo) {
      Array.prototype.forEach.call(lienzo.querySelectorAll('[data-s="' + actual.n + '"]'), function (c) { c.classList.add('es-hoy'); });
      var th = lienzo.querySelector('thead th[data-s="' + actual.n + '"]'), rot = lienzo.querySelector('th.rot');
      if (th && rot && lienzo.scrollWidth > lienzo.clientWidth) lienzo.scrollLeft = Math.max(0, th.offsetLeft - rot.offsetWidth);
    }
  })();

  function nodo(tag, cls, txt) { var n = document.createElement(tag); if (cls) n.className = cls; if (txt !== undefined) n.textContent = txt; return n; }

  // Apaga las barras hechas; en las que juntan varias tareas, dice cuántas van
  function pintarHechas() {
    if (!UNIDO) return;
    if (lienzo) Array.prototype.forEach.call(lienzo.querySelectorAll('button.tramo[data-ids]'), function (b) {
      var ids = b.getAttribute('data-ids').split(','), n = 0;
      ids.forEach(function (i) { if (hechas[i]) n++; });
      var todo = n === ids.length, caja = b.querySelector('.b');
      b.classList.toggle('hecho', todo);
      if (caja && ids.length > 1 && !b.classList.contains('t-hito')) caja.textContent = todo ? '' : (n ? n + '/' + ids.length : String(ids.length));
    });
    var h = el('ahora-hecho');
    if (h && panel) h.hidden = !hechas['w' + panel.n + 'c'];
    if (ficha && !ficha.hidden) Array.prototype.forEach.call(ficha.querySelectorAll('input[data-id]'), function (c) { c.checked = !!hechas[c.getAttribute('data-id')]; });
  }

  function cerrar(devolver) {
    if (!ficha || ficha.hidden) return;
    ficha.hidden = true;
    document.body.classList.remove('con-ficha');
    if (ultimo) { ultimo.classList.remove('sel'); if (devolver) ultimo.focus(); }
    ultimo = null;
  }

  function abrir(b) {
    var it = ITEMS[Number(b.getAttribute('data-i'))];
    if (!it || !ficha) return;
    if (ultimo) ultimo.classList.remove('sel');
    ultimo = b; b.classList.add('sel');
    el('ficha-cuando').textContent = 'S' + it.s + ' · ' + SEM[it.s - 1].fechas;
    el('ficha-titulo').textContent = it.fila;
    el('ficha-plan').textContent = it.plan ? it.plan + (it.meta ? '. ' + it.meta + '.' : '') : '';
    var ul = el('ficha-tareas');
    ul.textContent = '';
    it.tareas.forEach(function (t) {
      var li = nodo('li'), p = nodo('p');
      p.appendChild(nodo('b', t.tipo === 'imp' ? 'clave' : 'marca', t.marca));
      p.appendChild(document.createTextNode(t.texto));
      li.appendChild(p);
      if (t.dato) li.appendChild(nodo('p', 'dato', t.dato));
      (t.antes || []).forEach(function (a) { li.appendChild(nodo('p', 'antes', 'Néstor lo deja listo en la S' + a.s + ': ' + a.t)); });
      if (UNIDO && t.id) {
        var lab = nodo('label', 'marcar'), cb = document.createElement('input');
        cb.type = 'checkbox'; cb.id = 'f-' + t.id; cb.setAttribute('data-id', t.id); cb.checked = !!hechas[t.id];
        lab.appendChild(cb); lab.appendChild(document.createTextNode('Hecho'));
        li.appendChild(lab);
      }
      ul.appendChild(li);
    });
    ficha.hidden = false;
    ficha.scrollTop = 0;
    document.body.classList.add('con-ficha');
    // Que la barra tocada no quede tapada por la ficha
    var r = b.getBoundingClientRect(), alto = ficha.getBoundingClientRect().height;
    var sobra = r.bottom + 14 - (window.innerHeight - alto);
    if (sobra > 0) window.scrollBy({ top: sobra, behavior: calma ? 'auto' : 'smooth' });
  }

  function plegar(btn, abierto) {
    var tb = btn.closest('tbody');
    if (!tb) return;
    if (abierto === undefined) abierto = btn.getAttribute('aria-expanded') !== 'true';
    Array.prototype.forEach.call(tb.querySelectorAll('tr.fila, tr.regla'), function (tr) { tr.hidden = !abierto; });
    btn.setAttribute('aria-expanded', String(abierto));
    btn.textContent = abierto ? 'Plegar' : 'Desplegar';
    if (!abierto && ultimo && tb.contains(ultimo)) cerrar(false);
  }

  if (lienzo) {
    lienzo.addEventListener('click', function (ev) {
      var t = ev.target && ev.target.closest ? ev.target : null;
      if (!t) return;
      var b = t.closest('button.tramo');
      if (b) { if (b === ultimo) cerrar(false); else abrir(b); return; }
      var pl = t.closest('button.plegar');
      if (pl) plegar(pl);
    });
    // Lo de Néstor llega plegado: el diagrama es, antes que nada, el de Annie
    var pn = lienzo.querySelector('#g-nestor .plegar');
    if (pn) plegar(pn, false);
  }
  if (UNIDO) {
    if (ficha) ficha.addEventListener('change', function (ev) {
      var c = ev.target, id = c && c.getAttribute ? c.getAttribute('data-id') : null;
      if (!id) return;
      var t = leerT();
      t[id] = c.checked;
      guardarT(t);
      for (var k in t) hechas[k] = t[k];
      hechas[id] = c.checked;
      pintarHechas();
    });
    // Si el plan marca algo en otra pestaña, o se vuelve atrás desde él, se repinta
    window.addEventListener('storage', function (ev) { if (ev.key === LS_T) { hechas = leerT(); pintarHechas(); } });
    window.addEventListener('pageshow', function (ev) { if (ev.persisted) { hechas = leerT(); pintarHechas(); } });
    pintarHechas();
  }
  if (el('ficha-cerrar')) el('ficha-cerrar').addEventListener('click', function () { cerrar(true); });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') cerrar(true); });

  // Los enlaces a un plan lo despliegan antes de saltar a él
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href^="#g-"]') : null;
    if (!a) return;
    var tb = el(a.getAttribute('href').slice(1)), pl = tb ? tb.querySelector('.plegar') : null;
    if (pl) plegar(pl, true);
  });

  var ver = el('ahora-ver');
  if (ver && lienzo) ver.addEventListener('click', function () {
    var b = lienzo.querySelector('button.tramo[data-ruta="' + ver.getAttribute('data-s') + '"]');
    lienzo.scrollIntoView({ block: 'start', behavior: calma ? 'auto' : 'smooth' });
    if (b) { abrir(b); try { b.focus({ preventScroll: true }); } catch (e) { b.focus(); } }
  });
})();
'''

def muestra(tipo, extra=''):
    return '<span class="muestra t-%s%s" aria-hidden="true"><span class="b"></span></span>' % (tipo, extra)

CUERPO = '''
<div class="hoja" lang="es">

<header class="cabecera">
  <p class="eti">388 Pueblos · Plan de validación · 17 nov 2026 – 14 feb 2027</p>
  <h1>El plan, <em>de un vistazo</em></h1>
  <p class="entrada">Annie: este es el mismo plan, dibujado. De izquierda a derecha, las trece semanas hasta Carnaval. De arriba abajo, los cinco planes y sus acciones. Toca una barra para ver qué hay que hacer, cuánto lleva y desde dónde.</p>
  <p class="entrada-mas">@@ENLACE_ARRIBA@@</p>
</header>

<section class="bloque" id="ahora" aria-labelledby="ahora-titulo">
  <div class="hoy">
    <p class="eti" id="ahora-eti">Esta semana · S1 · @@S1_FECHAS@@</p>
    <h2 id="ahora-titulo">@@S1_TIT@@</h2>
    <p id="ahora-texto"><b class="clave">Lo importante</b>@@S1_TEXTO@@</p>
    <p class="hoy-dato" id="ahora-dato">@@S1_DATO@@</p>
    <p id="ahora-mas">@@S1_MAS@@</p>
    <p class="hoy-hecho" id="ahora-hecho" hidden>✓ Hecho: esta semana ya está sellada.</p>
    <button type="button" class="boton" id="ahora-ver" data-s="1">Verla en el diagrama</button>
  </div>
</section>

<section class="bloque" id="objetivo" aria-labelledby="h-objetivo">
  <h2 id="h-objetivo">Un objetivo, cinco planes</h2>
  <p>El objetivo es saber, antes de Carnaval, si 388 Pueblos tiene futuro. Se sabrá por cuatro cosas, cada una con su plan, y un quinto plan lleva el juego a la gente joven. En cada plan, el <b>suelo</b> ya hace que haya merecido la pena, la <b>meta</b> es a por lo que vas y el <b>sueño</b> está para apuntar alto.</p>
  <ul class="alturas">
    <li class="altura">
      <span class="eti">Plan 1</span>
      <h3><a href="#g-p1">Llegar a la gente</a></h3>
      <p class="d">De uno en uno por WhatsApp, y dos fechas para juntar a mucha gente: Navidad y Carnaval.</p>
      <p class="mide">Se mide en personas que han jugado.</p>
      <dl>
        <div><dt>Suelo</dt><dd>100</dd></div>
        <div class="meta"><dt>Meta</dt><dd>300</dd></div>
        <div class="sueno"><dt>Sueño</dt><dd>1.000</dd></div>
      </dl>
    </li>
    <li class="altura">
      <span class="eti">Plan 2</span>
      <h3><a href="#g-p2">Escuchar y mejorar</a></h3>
      <p class="d">Mirar jugar, contarle a Néstor dónde se atasca la gente y darle un motivo para volver.</p>
      <p class="mide">Se mide en cuántos vuelven a la semana, de cada 100.</p>
      <dl>
        <div><dt>Suelo</dt><dd>10</dd></div>
        <div class="meta"><dt>Meta</dt><dd>15</dd></div>
        <div class="sueno"><dt>Sueño</dt><dd>20</dd></div>
      </dl>
    </li>
    <li class="altura">
      <span class="eti">Plan 3</span>
      <h3><a href="#g-p3">El Ayuntamiento de Guareña</a></h3>
      <p class="d">Una cita, una reunión y una propuesta de una página. Por ese orden.</p>
      <p class="mide">Se mide en lo que sale de sentarte con ellos.</p>
      <dl>
        <div><dt>Suelo</dt><dd>Reunión hecha y respuesta clara</dd></div>
        <div class="meta"><dt>Meta</dt><dd>Compromiso por escrito</dd></div>
        <div class="sueno"><dt>Sueño</dt><dd>Contrato firmado</dd></div>
      </dl>
    </li>
    <li class="altura">
      <span class="eti">Plan 4</span>
      <h3><a href="#g-p4">El segundo pueblo</a></h3>
      <p class="d">Los votos de la web dicen cuál es. Tú buscas a quien lo mueva allí y Néstor lo construye.</p>
      <p class="mide">Se mide en lo lejos que llega ese pueblo.</p>
      <dl>
        <div><dt>Suelo</dt><dd>Elegido, con una persona de allí</dd></div>
        <div class="meta"><dt>Meta</dt><dd>Dentro del juego, con sus primeros 20 vecinos</dd></div>
        <div class="sueno"><dt>Sueño</dt><dd>Su ayuntamiento pide reunión</dd></div>
      </dl>
    </li>
    <li class="altura">
      <span class="eti">Plan 5</span>
      <h3><a href="#g-p5">Gente joven en redes</a></h3>
      <p class="d">TikTok e Instagram, con memes y retos hechos con el juego: dos vídeos por semana.</p>
      <p class="mide">Se mide en vídeos publicados y en jugadores que llegan desde las redes.</p>
      <dl>
        <div><dt>Suelo</dt><dd>20 vídeos publicados</dd></div>
        <div class="meta"><dt>Meta</dt><dd>100 jugadores desde las redes</dd></div>
        <div class="sueno"><dt>Sueño</dt><dd>Un vídeo con 100.000 reproducciones</dd></div>
      </dl>
    </li>
  </ul>
</section>

<section class="bloque" id="leer" aria-labelledby="h-leer">
  <h2 id="h-leer">Cómo se lee</h2>
  <ul class="leyenda">
    <li>@@M_IMP@@<span class="txt"><b>Lo importante.</b> La única tarea que hace falta esa semana.</span></li>
    <li>@@M_HAB@@<span class="txt"><b>Hábito.</b> Lo que se repite cada semana: tus mensajes y tus vídeos.</span></li>
    <li>@@M_SP@@<span class="txt"><b>Si puedes.</b> Suma, pero no es obligatorio.</span></li>
    <li>@@M_SPP@@<span class="txt"><b>Si estás en el pueblo.</b> Solo si esa semana bajas a Guareña.</span></li>
    <li>@@M_RUT@@<span class="txt"><b>Cada viernes.</b> Quince minutos con Néstor.</span></li>
    <li>@@M_NES@@<span class="txt"><b>Lo hace Néstor.</b> El juego, la web y lo que te prepara.</span></li>
    <li>@@M_HITO@@<span class="txt"><b>Fecha señalada.</b> Un día concreto del calendario.</span></li>
    <li>@@M_ESP@@<span class="txt"><b>Esperas respuesta.</b> No hay tarea esa semana.</span></li>
    <li><span class="muestra tinte pueblo" aria-hidden="true"></span><span class="txt"><b>Ya estás en Guareña.</b> Puente de diciembre, Navidad y Carnaval.</span></li>
    <li><span class="muestra tinte ahora" aria-hidden="true"></span><span class="txt"><b>Esta semana.</b> La columna en la que estás hoy.</span></li>
    <li>@@M_NUM@@<span class="txt"><b>Un número.</b> Cuántas tareas hay dentro de esa barra.</span></li>
    @@LEY_HECHO@@
  </ul>
</section>

<section class="bloque" id="diagrama" aria-labelledby="h-diagrama">
  <h2 id="h-diagrama">El diagrama</h2>
  <p class="pista-mov">Desliza hacia los lados para ver las trece semanas. Toca una barra para abrir su ficha.</p>
  <div class="lienzo" id="lienzo" tabindex="0" role="region" aria-labelledby="h-diagrama">
@@TABLA@@
  </div>
</section>

<footer class="pie">
  <p>@@PIE_UNO@@</p>
  <p>Carnaval de 2027 según el calendario: del sábado 6 al martes 9 de febrero. Confirma el programa local con el Ayuntamiento.</p>
  <p>Los tiempos son una estimación. Si una tarea se alarga, déjala donde esté y sigue otro día.</p>
</footer>

</div>

<aside class="ficha" id="ficha" hidden aria-live="polite" aria-labelledby="ficha-titulo">
  <div class="ficha-dentro">
    <p class="eti" id="ficha-cuando"></p>
    <button type="button" class="cerrar" id="ficha-cerrar">Cerrar</button>
    <h2 id="ficha-titulo"></h2>
    <p class="ficha-plan" id="ficha-plan"></p>
    <ul id="ficha-tareas"></ul>
    <p class="ficha-pie">@@PIE_FICHA@@</p>
  </div>
</aside>
'''

def js_json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

cuerpo = CUERPO
for k, v in {
    '@@S1_FECHAS@@': esc(S1['fechas']), '@@S1_TIT@@': esc(S1['tit']), '@@S1_TEXTO@@': esc(S1['texto']), '@@S1_DATO@@': esc(S1['dato']), '@@S1_MAS@@': esc(frase_mas(S1['mas'])),
    '@@M_IMP@@': muestra('imp'), '@@M_HAB@@': muestra('hab'), '@@M_SP@@': muestra('sp'), '@@M_SPP@@': muestra('sp', ' en-pueblo'), '@@M_RUT@@': muestra('rut'),
    '@@M_NES@@': muestra('nes'), '@@M_HITO@@': muestra('hito'), '@@M_ESP@@': muestra('esp'), '@@TABLA@@': TABLA,
    '@@M_NUM@@': '<span class="muestra t-imp" aria-hidden="true"><span class="b">3</span></span>',
}.items():
    assert k in cuerpo, k
    cuerpo = cuerpo.replace(k, v)
js = JS.replace('@@ITEMS@@', js_json(ITEMS)).replace('@@SEM@@', js_json(SEMJS))

CABEZA = ('<title>Gantt de Annie hasta Carnaval</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
          '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=Geist+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap">\n'
          '<style>' + CSS + '</style>\n')
doc = CABEZA + cuerpo + '\n<script>' + js + '</script>\n'
HECHO_LI = '<li><span class="muestra t-imp hecho" aria-hidden="true"><span class="b"></span></span><span class="txt"><b>Hecho.</b> La barra se apaga y lleva una marca.</span></li>'
VARIANTES = [
    # En Claude: página aparte del plan, sin marcas
    (out_art, [
        ('@@ENLACE_ARRIBA@@', 'Las casillas para marcar lo hecho, el marcador y los guiones están en <a href="@@PLAN@@"@@DESTINO@@>el plan</a>.'),
        ('@@PIE_UNO@@', 'Las casillas para marcar lo hecho, el marcador y los guiones están en <a href="@@PLAN@@"@@DESTINO@@>el plan de Annie</a>. Este diagrama es el mismo plan, visto en el tiempo.'),
        ('@@PIE_FICHA@@', 'Para marcarla como hecha, abre <a href="@@PLAN@@"@@DESTINO@@>el plan de Annie</a>.'),
        ('@@LEY_HECHO@@', ''), ('@@UNIDO@@', 'false'),
        ('@@PLAN@@', URL_PLAN), ('@@DESTINO@@', ' target="_blank" rel="noopener"')]),
    # En la web abierta: misma dirección que el plan, así que comparten las marcas
    (out_suelto, [
        ('@@ENLACE_ARRIBA@@', 'Toca una barra y márcala como hecha: sale también en <a href="@@PLAN@@">el plan</a>, y lo que marques allí sale aquí. El plan tiene además el marcador y los guiones.'),
        ('@@PIE_UNO@@', 'Las marcas se guardan en el navegador de cada uno: lo que marques en tu móvil se ve en tu móvil, no en el de otra persona. El marcador y los guiones están en <a href="@@PLAN@@">el plan</a>.'),
        ('@@PIE_FICHA@@', 'Lo que marques aquí sale también en <a href="@@PLAN@@">el plan</a>, en este mismo dispositivo.'),
        ('@@LEY_HECHO@@', HECHO_LI), ('@@UNIDO@@', 'true'),
        ('@@PLAN@@', ARCHIVO_PLAN), ('@@DESTINO@@', '')]),
]
for salida, cambios in VARIANTES:
    d = doc
    for k, v in cambios:
        assert k in d or k in ('@@PLAN@@', '@@DESTINO@@'), k
        d = d.replace(k, v)
    assert '@@' not in d, 'marcas sin sustituir'
    open(salida, 'w', encoding='utf-8').write(d)
print('gantt:', len(doc), 'bytes ·', len(ITEMS), 'barras ·', sum(len(g['filas']) for g in GRUPOS) + 3, 'filas · tareas del plan colocadas:', len(vistas))
