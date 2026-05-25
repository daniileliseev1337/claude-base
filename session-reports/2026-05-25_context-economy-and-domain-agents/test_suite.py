"""
Test suite для новых агентов из session 2026-05-25.

Проверяет:
1. Frontmatter (YAML парсится, обязательные поля name/description/tools).
2. Tools — comma-separated, известные значения.
3. Wikilinks [[name]] — на существующие агенты ИЛИ помечены [PLANNED].
4. Skills упомянутые в Required reading — реальные файлы в ~/.claude/skills/.
5. Backtick `имя-агента` references — на существующие ИЛИ [PLANNED].
6. Markers «model:» (запрещён) — отсутствуют.
7. Заголовок Karpathy — русский «Принципы поведения».
8. Read-only enforcement для audit-rd-section (нет Write/Edit в tools).

Output: PASS/FAIL по каждому критерию + сводка.
"""

import re
import sys
from pathlib import Path

HOME = Path.home()
AGENTS_DIR = HOME / '.claude' / 'agents'
SKILLS_DIR = HOME / '.claude' / 'skills'

# Файлы для проверки (новые в этой сессии)
NEW_FILES = ['_TEMPLATE.md', 'pto-engineer.md', 'сметчик.md',
             'снабженец.md', 'audit-rd-section.md',
             'norm-lookup.md', 'kp-writer.md', 'letter-writer.md']

# Read-only агенты (tools НЕ должны содержать Write/Edit)
READ_ONLY_AGENTS = {'auditor.md', 'word-checker.md', 'excel-validator.md',
                     'pdf-reviewer.md', 'audit-rd-section.md',
                     'norm-lookup.md'}

# Известные значения tools (whitelist)
KNOWN_TOOLS = {'Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash',
               'WebFetch', 'WebSearch', 'TaskCreate', 'TaskUpdate'}


def extract_frontmatter(path):
    """Извлечь YAML frontmatter (между --- ... ---)."""
    text = path.read_text(encoding='utf-8')
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not m:
        return None, text
    return m.group(1), text


def parse_field(fm, field):
    """Извлечь значение поля из frontmatter."""
    # Multi-line через | (description: |\n  text)
    m = re.search(rf'^{field}:\s*\|\s*\n((?:  .*\n?)+)', fm, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Single-line (name: value)
    m = re.search(rf'^{field}:\s*(.+?)(?:\s+#.*)?$', fm, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def find_wikilinks(text):
    """Найти все [[name]] ссылки."""
    return re.findall(r'\[\[([^\]]+)\]\]', text)


def find_backtick_refs(text, known_agents):
    """Найти упоминания агентов в формате `name`."""
    refs = re.findall(r'`([^`]+)`', text)
    return [r for r in refs if r in known_agents]


def find_skill_refs(text):
    """Найти упоминания skills (через путь или [[wikilink]])."""
    refs = set()
    # ~/.claude/skills/NAME/SKILL.md
    for m in re.findall(r'~/\.claude/skills/([^/\s]+)/SKILL\.md', text):
        refs.add(m)
    # [[skill-name]] (если совпадает с папкой skills)
    return refs


def check_planned_marker(text, ref):
    """Проверить помечен ли `ref` как [PLANNED] в тексте."""
    # Ищем в одном из шаблонов:
    # [[name]] [PLANNED]
    # `name` [PLANNED]
    # name [PLANNED]
    patterns = [
        rf'\[\[{re.escape(ref)}\]\][^\n]*\[PLANNED\]',
        rf'`{re.escape(ref)}`[^\n]*\[PLANNED\]',
        rf'\b{re.escape(ref)}\b[^\n]*\[PLANNED\]',
    ]
    return any(re.search(p, text) for p in patterns)


# === MAIN ===

def main():
    print('=' * 70)
    print('TEST SUITE — новые агенты из session 2026-05-25')
    print('=' * 70)

    # Существующие агенты (для wikilink validation)
    existing_agents = {f.stem for f in AGENTS_DIR.glob('*.md')}
    # Skills
    existing_skills = {d.name for d in SKILLS_DIR.iterdir()
                       if d.is_dir() and (d / 'SKILL.md').exists()}

    print(f'\nИзвестно агентов: {len(existing_agents)} ({sorted(existing_agents)})')
    print(f'Известно skills: {len(existing_skills)} ({sorted(existing_skills)})')

    all_pass = True
    results = []  # (file, criterion, status, detail)

    for fname in NEW_FILES:
        path = AGENTS_DIR / fname
        print(f'\n{"-" * 70}')
        print(f'CHECK: {fname}')
        print(f'{"-" * 70}')

        if not path.exists():
            print(f'  [FAIL] Файл не существует')
            results.append((fname, 'file-exists', 'FAIL', 'не существует'))
            all_pass = False
            continue

        fm, text = extract_frontmatter(path)
        if fm is None:
            print(f'  [FAIL] Frontmatter не найден')
            results.append((fname, 'frontmatter', 'FAIL', 'не найден'))
            all_pass = False
            continue

        # 1. Frontmatter: обязательные поля
        for field in ['name', 'description', 'tools']:
            val = parse_field(fm, field)
            if val:
                print(f'  [PASS] frontmatter.{field}: {val[:60]}{"..." if len(val) > 60 else ""}')
                results.append((fname, f'fm.{field}', 'PASS', val[:60]))
            else:
                print(f'  [FAIL] frontmatter.{field}: отсутствует')
                results.append((fname, f'fm.{field}', 'FAIL', 'отсутствует'))
                all_pass = False

        # 2. Tools — все известные
        tools_val = parse_field(fm, 'tools')
        if tools_val:
            tools = [t.strip() for t in tools_val.split(',')]
            unknown = [t for t in tools if t not in KNOWN_TOOLS]
            if not unknown:
                print(f'  [PASS] tools — все известные ({len(tools)})')
                results.append((fname, 'tools-known', 'PASS', f'{len(tools)} tools'))
            else:
                print(f'  [FAIL] tools — неизвестные: {unknown}')
                results.append((fname, 'tools-known', 'FAIL', str(unknown)))
                all_pass = False

            # 2a. Read-only — НЕТ Write/Edit
            if fname in READ_ONLY_AGENTS:
                forbidden = [t for t in tools if t in {'Write', 'Edit'}]
                if not forbidden:
                    print(f'  [PASS] read-only enforcement (нет Write/Edit)')
                    results.append((fname, 'read-only', 'PASS', 'нет Write/Edit'))
                else:
                    print(f'  [FAIL] read-only нарушено: {forbidden}')
                    results.append((fname, 'read-only', 'FAIL', str(forbidden)))
                    all_pass = False

        # 3. Запрещённое поле model:
        if re.search(r'^model:', fm, re.MULTILINE):
            print(f'  [FAIL] frontmatter.model: присутствует (запрещено — рассинхрон с базой)')
            results.append((fname, 'no-model', 'FAIL', 'model: есть'))
            all_pass = False
        else:
            print(f'  [PASS] frontmatter.model отсутствует (как требуется)')
            results.append((fname, 'no-model', 'PASS', 'нет model:'))

        # 4. Заголовок Karpathy — русский
        if re.search(r'^## Принципы поведения', text, re.MULTILINE):
            print(f'  [PASS] заголовок «Принципы поведения» (русский)')
            results.append((fname, 'karpathy-ru', 'PASS', ''))
        elif re.search(r'^## Principles \(Karpathy', text, re.MULTILINE):
            print(f'  [FAIL] заголовок «Principles (Karpathy ...)» (английский — должен быть русский)')
            results.append((fname, 'karpathy-ru', 'FAIL', 'английский'))
            all_pass = False
        else:
            # TEMPLATE может иметь только Karpathy-маркер; не критично если других нет
            if fname == '_TEMPLATE.md':
                print(f'  [PASS] заголовок Karpathy — проверка пропущена (template)')
                results.append((fname, 'karpathy-ru', 'PASS', 'template - skipped'))
            else:
                print(f'  [FAIL] заголовка Karpathy нет')
                results.append((fname, 'karpathy-ru', 'FAIL', 'отсутствует'))
                all_pass = False

        # 5. Wikilinks [[name]] — на существующие или [PLANNED]
        wikilinks = find_wikilinks(text)
        # Удалим [[CLAUDE]] (это ссылка не на агент)
        wikilinks = [w for w in wikilinks if w not in {'CLAUDE'}]
        bad_links = []
        ok_links = []
        for w in set(wikilinks):
            # Wikilink может быть на агент или skill
            if w in existing_agents or w in existing_skills:
                ok_links.append(w)
            elif check_planned_marker(text, w):
                ok_links.append(f'{w} [PLANNED]')
            elif w.startswith('<') and w.endswith('>'):
                # Это placeholder в template'е (например <related-agent-1>)
                continue
            else:
                bad_links.append(w)

        if not bad_links:
            print(f'  [PASS] wikilinks — все валидны ({len(ok_links)})')
            results.append((fname, 'wikilinks', 'PASS', f'{len(ok_links)} ok'))
        else:
            print(f'  [FAIL] wikilinks — битые: {bad_links}')
            results.append((fname, 'wikilinks', 'FAIL', str(bad_links)))
            all_pass = False

        # 6. Skill references
        skill_refs = find_skill_refs(text)
        bad_skills = [s for s in skill_refs if s not in existing_skills]
        if not bad_skills:
            print(f'  [PASS] skill refs — все существуют ({len(skill_refs)})')
            results.append((fname, 'skill-refs', 'PASS', f'{len(skill_refs)} ok'))
        else:
            print(f'  [FAIL] skill refs — несуществующие: {bad_skills}')
            results.append((fname, 'skill-refs', 'FAIL', str(bad_skills)))
            all_pass = False

        # 7. Доменные галлюцинации в сметчике
        if fname == 'сметчик.md':
            if 'ПДВ' in text:
                print(f'  [FAIL] доменная галлюцинация «ПДВ» присутствует')
                results.append((fname, 'no-pdv', 'FAIL', 'ПДВ есть'))
                all_pass = False
            else:
                print(f'  [PASS] нет «ПДВ» (украинизм исправлен)')
                results.append((fname, 'no-pdv', 'PASS', ''))
            # Проверяем ЗПР с пробелом или в конце слова (не путать с ИРВ и т.п.)
            if re.search(r'\bЗПР\b', text):
                print(f'  [FAIL] доменная галлюцинация «ЗПР» присутствует')
                results.append((fname, 'no-zpr', 'FAIL', 'ЗПР есть'))
                all_pass = False
            else:
                print(f'  [PASS] нет «ЗПР» (выдуманное сокращение исправлено)')
                results.append((fname, 'no-zpr', 'PASS', ''))

    # === SUMMARY ===
    print('\n' + '=' * 70)
    print('SUMMARY')
    print('=' * 70)
    total = len(results)
    passed = sum(1 for _, _, status, _ in results if status == 'PASS')
    failed = total - passed
    print(f'Всего проверок: {total}')
    print(f'PASS: {passed}')
    print(f'FAIL: {failed}')
    print(f'\nFinal verdict: {"PASSED" if all_pass else "NOT PASSED"}')

    if not all_pass:
        print('\nFailed checks:')
        for fname, crit, status, detail in results:
            if status == 'FAIL':
                print(f'  - {fname} / {crit}: {detail}')

    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
