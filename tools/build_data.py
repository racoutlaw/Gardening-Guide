"""Build the ZIP -> frost-date/zone lookup embedded in the garden planner page.

Sources:
  NOAA NCEI U.S. Climate Normals 1991-2020, annual/seasonal by station (frost probabilities)
  USDA 2023 Plant Hardiness Zone Map by ZIP (PRISM Group, Oregon State University)
  GeoNames US postal codes (place names + coordinates, CC-BY 4.0)
"""
import csv, glob, json, math, os, sys
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
csv.field_size_limit(10**9)

def doy(mmdd):
    mmdd = (mmdd or '').strip()
    if not mmdd or '/' not in mmdd:
        return None
    m, d = mmdd.split('/')
    m, d = int(m), int(d)
    if m < 1 or m > 12:
        return None
    cum = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    return cum[m - 1] + d  # non-leap day of year

COLS = {
    'lst50': 'ANN-TMIN-PRBLST-T32FP50',
    'lst10': 'ANN-TMIN-PRBLST-T32FP10',   # 10% chance of a frost after this date
    'fst50': 'ANN-TMIN-PRBFST-T32FP50',
    'fst10': 'ANN-TMIN-PRBFST-T32FP10',   # 10% chance of a frost before this date
}

# ---- stations ----
stations = []
files = glob.glob(os.path.join(D, '*.csv'))
for f in files:
    b = os.path.basename(f)
    if b.startswith('zone_'):
        continue
    with open(f, newline='', encoding='utf-8', errors='replace') as fh:
        r = csv.DictReader(fh)
        try:
            row = next(r)
        except StopIteration:
            continue
    if not all(c in row for c in COLS.values()):
        continue
    v = {k: doy(row[c]) for k, c in COLS.items()}
    if any(x is None for x in v.values()):
        # -9999 with ~zero nights at or below 32F = a frost-free station; keep it as 0s
        try:
            nights32 = float(row.get('ANN-TMIN-AVGNDS-LSTH032', ''))
        except ValueError:
            continue
        if nights32 > 0.5:
            continue
        v = {k: 0 for k in COLS}
    try:
        lat, lon = float(row['LATITUDE']), float(row['LONGITUDE'])
        elev_m = float(row['ELEVATION'])
    except ValueError:
        continue
    name = row['NAME'].strip()
    stations.append([name, round(lat, 3), round(lon, 3), round(elev_m * 3.28084),
                     v['lst50'], v['lst10'], v['fst50'], v['fst10']])
print('stations with frost normals:', len(stations), 'of', len(files))

# grid index for nearest search
grid = defaultdict(list)
for i, s in enumerate(stations):
    grid[(math.floor(s[1]), math.floor(s[2]))].append(i)

def km(a1, o1, a2, o2):
    p = math.pi / 180
    x = (o2 - o1) * p * math.cos((a1 + a2) / 2 * p)
    y = (a2 - a1) * p
    return 6371 * math.hypot(x, y)

def nearest(lat, lon):
    best, bd = None, 1e9
    for rad in range(0, 8):
        for gy in range(math.floor(lat) - rad, math.floor(lat) + rad + 1):
            for gx in range(math.floor(lon) - rad, math.floor(lon) + rad + 1):
                if max(abs(gy - math.floor(lat)), abs(gx - math.floor(lon))) != rad:
                    continue
                for i in grid.get((gy, gx), ()):
                    dd = km(lat, lon, stations[i][1], stations[i][2])
                    if dd < bd:
                        best, bd = i, dd
        if best is not None and bd < rad * 80:
            break
    return best, bd

# ---- zones ----
zones = {}
for f in glob.glob(os.path.join(D, 'zone_*.csv')):
    with open(f, newline='') as fh:
        for row in csv.DictReader(fh):
            zones[row['zipcode'].zfill(5)] = row['zone']
print('zones:', len(zones))

# ---- zips ----
zips = {}
with open(os.path.join(D, 'geonames', 'US.txt'), encoding='utf-8') as fh:
    for line in fh:
        p = line.rstrip('\n').split('\t')
        z, place, st, county = p[1], p[2], p[4], p[5]
        try:
            lat, lon = float(p[9]), float(p[10])
        except ValueError:
            continue
        i, dist = nearest(lat, lon)
        if i is None or dist > 250:
            continue
        zips[z] = [place, st, county, i, zones.get(z, ''), round(dist)]
print('zips mapped:', len(zips))

used = sorted({v[3] for v in zips.values()})
remap = {old: new for new, old in enumerate(used)}
out_st = [stations[i] for i in used]
for v in zips.values():
    v[3] = remap[v[3]]

# pack zips compactly: "zip|place|st|county|stationIdx|zone|km" joined with "\n"
packed = '\n'.join('|'.join([z] + [str(x) for x in v]) for z, v in sorted(zips.items()))
data = {'stations': out_st, 'zips': packed}
with open(os.path.join(D, 'frostdata.js'), 'w', encoding='utf-8') as fh:
    fh.write('window.FROST_DATA=' + json.dumps(data, separators=(',', ':')) + ';\n')
print('frostdata.js bytes:', os.path.getsize(os.path.join(D, 'frostdata.js')))

for z in sys.argv[1:]:
    v = zips.get(z)
    if v:
        s = out_st[v[3]]
        print(z, v[:3], 'zone', v[4], 'station', s[0], f'{v[5]} km', 'elev', s[3], 'ft',
              'lst50/10', s[4], s[5], 'fst10/50', s[7], s[6])
