# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graph_update_win as gw

BS = chr(92)  # backslash, avoid literal-escape headaches

# trap #1 native_root
assert gw.native_root('/c/Users/Даниил/.claude') == 'C:/Users/Даниил/.claude'
assert gw.native_root('C:/Users/X/.claude') == 'C:/Users/X/.claude'
assert gw.native_root('/d/proj') == 'D:/proj'
print('native_root OK')

# relativize
assert gw.relativize('C:/Users/X/.claude/skills/g/SKILL.md') == 'skills/g/SKILL.md'
assert gw.relativize('/c/Users/Даниил/.claude/agents/a.md') == 'agents/a.md'
assert gw.relativize('skills/g/SKILL.md') == 'skills/g/SKILL.md'
backslash_path = 'C:' + BS + 'Users' + BS + 'X' + BS + '.claude' + BS + 'memory' + BS + 'm.md'
assert gw.relativize(backslash_path) == 'memory/m.md', gw.relativize(backslash_path)
assert gw.relativize('./skills/x.md') == 'skills/x.md'
print('relativize OK')

# normalize_extraction: trap #3 + trap #4
data = {
  'nodes': [
    {'id':'a','source_file':None,'source_location':'agents/auditor.md'},
    {'id':'b','source_file':None,'source_location':'L42'},
    {'id':'c','source_file':'C:/Users/X/.claude/skills/s/SKILL.md','source_location':'L5'},
    {'id':'d','source_file':'memory/x.md','source_location':None},
    {'id':'e','source_file':None,'source_location':None},
  ],
  'edges':[{'source':'a','target':'c','source_file':'/c/Users/Даниил/.claude/CLAUDE.md'}],
}
stats = gw.normalize_extraction(data)
n = {x['id']:x for x in data['nodes']}
assert n['a']['source_file']=='agents/auditor.md' and n['a']['source_location'] is None, n['a']
assert n['b']['source_file'] is None and n['b']['source_location']=='L42', n['b']
assert n['c']['source_file']=='skills/s/SKILL.md', n['c']
assert n['d']['source_file']=='memory/x.md', n['d']
assert n['e']['source_file'] is None, n['e']
assert data['edges'][0]['source_file']=='CLAUDE.md', data['edges'][0]
assert stats['recovered']==1 and stats['relativized']>=2, stats
print('normalize_extraction OK', stats)
print('ALL PURE-FN TESTS PASSED')
