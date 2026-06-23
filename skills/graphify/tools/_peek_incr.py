import json, re
from pathlib import Path
r=json.loads(Path('graphify-out/.graphify_incremental.json').read_text(encoding='utf-8'))
deleted=list(r.get('deleted_files',[]))
changed=[f for files in r.get('new_files',{}).values() for f in files]
def rel(p):
    s=str(p).replace(chr(92),'/'); i=s.find('/.claude/'); 
    return s[i+9:] if i!=-1 else s
# top-level dirs of deleted
from collections import Counter
c=Counter(rel(d).split('/')[0] for d in deleted)
print('DELETED top-level dirs:', dict(c))
print('--- sample deleted (5) ---')
for d in deleted[:5]: print('  ', rel(d))
print('--- CHANGED (16) ---')
for d in changed: print('  ', rel(d))
# how many deleted are structural (agents/skills/memory/blocks/chains/CLAUDE.md)
struct={'agents','skills','memory','blocks','chains'}
sd=[rel(d) for d in deleted if rel(d).split('/')[0] in struct or rel(d) in ('CLAUDE.md','mcp-manifest.json')]
print('structural deleted count:', len(sd))
for d in sd[:20]: print('  STRUCT-DEL:', d)
