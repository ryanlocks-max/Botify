#!/usr/bin/env python3
import json, os, sys
here=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(here,'csuite.src.html')).read()
data=json.dumps(json.load(open(os.path.join(here,'csuite.json'))),separators=(',',':'))
out=src.replace('/*__DATA__*/null',data,1); assert '/*__DATA__*/' not in out
dst=sys.argv[1] if len(sys.argv)>1 else os.path.join(here,'..','What-Walmart-Is-Asking-For.html')
open(dst,'w').write(out); print(dst,len(out))
