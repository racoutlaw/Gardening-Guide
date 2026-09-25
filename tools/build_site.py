"""Build a standalone index.html (for GitHub Pages) from template.html + frostdata.js.

The artifact version gets its <!doctype>/<head> wrapper added at publish time; a plain
web host needs it written into the file.
"""
import os, sys
D = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(D, 'template.html'), encoding='utf-8').read()
data = open(os.path.join(D, 'frostdata.js'), encoding='utf-8').read().strip()
assert '/*__FROST_DATA__*/' in t
t = t.replace('/*__FROST_DATA__*/', data)

split = t.index('<div class="wrap">')
head, body = t[:split], t[split:]
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="description" content="Planting calendar for vegetables, herbs, fruits and nuts, timed from NOAA frost dates for your ZIP code.">\n'
        '<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>\n'
        + head + '</head>\n<body>\n' + body + '\n</body>\n</html>\n')

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'repo', 'index.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w', encoding='utf-8').write(page)
print(out, len(page.encode('utf-8')))
