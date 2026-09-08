#!/usr/bin/env python3
"""Assemble Walmart-Pilot-Rebase.html from src/part1.html, part2.js, part3.js and payload.json."""
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', 'Walmart-Pilot-Rebase.html')
payload = json.dumps(json.load(open(os.path.join(here, 'payload.json'))), separators=(',', ':'))
p1 = open(os.path.join(here, 'part1.html')).read()
p2 = open(os.path.join(here, 'part2.js')).read().replace('/*__PAYLOAD__*/null', payload, 1)
p3 = open(os.path.join(here, 'part3.js')).read()
assert '/*__PAYLOAD__*/' not in p2
html = p1 + '\n<script>\n' + p2 + '\n' + p3 + '\n</script>\n'
open(out, 'w').write(html)
open(os.path.join(here, '_combined.js'), 'w').write(p2 + '\n' + p3)
print(out, len(html), 'bytes')
