#!/usr/bin/env python3
"""Convert a SuperChinese/HSK-style Anki .apkg into the app's level JSON.
usage: apkg_to_level.py LevelN.apkg data/levelN.json   (needs ffmpeg for small audio)"""
import sys, os, re, json, sqlite3, zipfile, tempfile, base64, subprocess, shutil, html
from concurrent.futures import ThreadPoolExecutor

def clean(s):
    s = re.sub(r'<br\s*/?>', ' ', s); s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', html.unescape(s).replace('\xa0', ' ')).strip()

def sound(s):
    m = re.search(r'\[sound:([^\]]+)\]', s); return m.group(1) if m else None

def tokens(sh, spy, spn):
    """split sentence into pinyin-word tokens -> (hanzi tokens, lowercase pinyin tokens) or None"""
    pw, nw = spy.split(), spn.split()
    if len(pw) != len(nw) or len(pw) < 2: return None
    def syl(t):  # tone digits + a trailing/standalone neutral-tone syllable that has no digit
        t = re.sub(r'[^a-zA-ZüÜ1-5]', '', t); n = len(re.findall(r'[1-5]', t))
        return n + (1 if re.search(r'[a-zA-ZüÜ]$', t) else 0)
    cnt = [syl(t) for t in nw]
    chars = list(sh.replace(' ', '')); out = []; k = 0
    for c in cnt:
        tok = ''
        while k < len(chars) and chars[k] in '“‘（(': tok += chars[k]; k += 1
        got = 0
        while got < c and k < len(chars):
            if re.match(r'[\u3400-\u9fff]', chars[k]): got += 1
            tok += chars[k]; k += 1
        if got != c: return None
        while k < len(chars) and chars[k] in '，。！？、；：,.!?;:”’）)…—': tok += chars[k]; k += 1
        out.append(tok)
    if k < len(chars):
        if all(not re.match(r'[\u3400-\u9fff\w]', x) for x in chars[k:]): out[-1] += ''.join(chars[k:])
        else: return None
    return out, [re.sub(r"[^\wüÜ]", '', t.lower()) for t in pw]

def main(apkg, out):
    tmp = tempfile.mkdtemp(); zipfile.ZipFile(apkg).extractall(tmp)
    mp = json.load(open(os.path.join(tmp, 'media'), encoding='utf-8')); fn2id = {v: k for k, v in mp.items()}
    db = sqlite3.connect(os.path.join(tmp, 'collection.anki21'))
    rows = []
    for (flds,) in db.execute('select flds from notes'):
        f = flds.split('\x1f'); rows.append(f)
    rows.sort(key=lambda f: int(f[0]) if f[0].strip().isdigit() else 10**9)
    ffmpeg = shutil.which('ffmpeg')
    def audio(name):
        if not name or name not in fn2id: return ''
        p = os.path.join(tmp, fn2id[name])
        if ffmpeg:
            r = subprocess.run([ffmpeg, '-v', 'error', '-i', p, '-ar', '24000', '-ac', '1', '-b:a', '24k', '-f', 'mp3', '-'], capture_output=True)
            if r.returncode == 0 and r.stdout: return base64.b64encode(r.stdout).decode()
        return base64.b64encode(open(p, 'rb').read()).decode()
    words = []
    for f in rows:
        w = dict(h=clean(f[1]), py=clean(f[3]), pn=clean(f[4]).lower(), en=clean(f[5]), pos=clean(f[6]),
                 sh=clean(f[10]), spy=clean(f[14]), sen=clean(f[16]), cloze=clean(f[12]))
        w['_a'], w['_sa'] = sound(f[7]), sound(f[17])
        t = tokens(w['sh'], w['spy'], clean(f[15]))
        if t: w['ch'], w['chp'] = t
        words.append(w)
    with ThreadPoolExecutor(8) as ex:
        A = list(ex.map(audio, [w.pop('_a') for w in words])); S = list(ex.map(audio, [w.pop('_sa') for w in words]))
    res = []
    for w, a, s in zip(words, A, S):
        d = {k: w[k] for k in ('h','py','pn','en','pos','sh','spy','sen','cloze')}; d['a'], d['sa'] = a, s
        if 'ch' in w: d['ch'], d['chp'] = w['ch'], w['chp']
        res.append(d)
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'{out}: {len(res)} words, {os.path.getsize(out)/1e6:.1f} MB, order data for {sum("ch" in d for d in res)}, no-audio {sum(not d["a"] or not d["sa"] for d in res)}')
    shutil.rmtree(tmp)

if __name__ == '__main__': main(*sys.argv[1:3])
