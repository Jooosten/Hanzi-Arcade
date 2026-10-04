#!/usr/bin/env python3
"""Assemble www/index.html from src/app.template.html + data/level1..N.json (whichever exist, in order)."""
import os, re, glob, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = sorted(glob.glob(os.path.join(root, 'data', 'level*.json')), key=lambda p: int(re.findall(r'(\d+)', os.path.basename(p))[0]))
nums = [int(re.findall(r'(\d+)', os.path.basename(p))[0]) for p in files]
if nums != list(range(1, len(nums) + 1)): sys.exit(f'levels must be consecutive from 1, found {nums}')
data = 'const LEVELS = [' + ',\n'.join(open(p, encoding='utf-8').read().replace('</', '<\\/') for p in files) + '];\nLEVELS.forEach((l,k)=>l.forEach(w=>{w.lv=k+1}));\nconst WORDS = LEVELS.flat();'
tpl = open(os.path.join(root, 'src', 'app.template.html'), encoding='utf-8').read()
import json
cfgp = os.path.join(root, 'sync.config.json')
cfg = json.load(open(cfgp)) if os.path.exists(cfgp) else {}
cfg = {'url': (cfg.get('url') or '').rstrip('/'), 'anonKey': cfg.get('anonKey') or ''}
out = tpl.replace('/*__LEVEL_DATA__*/', data).replace('/*__SYNC_CFG__*/', json.dumps(cfg))
print('cloud sync:', 'ON' if cfg['url'] and cfg['anonKey'] else 'off (sync.config.json empty)')
os.makedirs(os.path.join(root, 'www'), exist_ok=True)
open(os.path.join(root, 'www', 'index.html'), 'w', encoding='utf-8').write(out)
print(f'www/index.html: levels {nums}, {os.path.getsize(os.path.join(root, "www", "index.html"))/1e6:.1f} MB')
