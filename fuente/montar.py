import re, sys
src, out, test, js = sys.argv[1:5]
h = open(src, encoding='utf-8').read()
i = h.index('</style>') + len('</style>')
cabeza, cuerpo = h[:i], h[i:]
reset = '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>'
doc = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
       '<meta name="robots" content="noindex,nofollow">\n' + reset + '\n' + cabeza + '\n</head>\n<body>' + cuerpo + '</body>\n</html>\n')
open(out, 'w', encoding='utf-8').write(doc)
sonda = "<script>addEventListener('load',function(){var d=document.documentElement;d.setAttribute('data-ow',d.scrollWidth+'/'+d.clientWidth+'/'+innerWidth+'/abiertas:'+document.querySelectorAll('details[open]').length)})</script>"
open(test, 'w', encoding='utf-8').write(doc.replace('</body>', sonda + '</body>'))
open(js, 'w', encoding='utf-8').write(re.search(r'<script>(.*?)</script>', h, re.S).group(1))
print('montado', len(doc), 'bytes · annie', len(re.findall(r'data-t="a"', cuerpo)) - 1, '· producto', len(re.findall(r'data-t="p"', cuerpo)), '· celdas', len(re.findall(r'data-m>', cuerpo)))
