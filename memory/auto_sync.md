# Auto-sync инфраструктура (информационно)

_Вынесено из CLAUDE.md 2026-05-26 (Phase 1 refactoring для экономии overhead токенов в каждой сессии). Загружается через Read только когда нужно._

---

## Auto-sync РёРЅС„СЂР°СЃС‚СЂСѓРєС‚СѓСЂР° (РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅРѕ)

`~/.claude/` СЃРєР»РѕРЅРёСЂРѕРІР°РЅР° С‡РµСЂРµР· git РёР· СЂРµРїРѕ
[claude-base](https://github.com/daniileliseev1337/claude-base). РњРµР¶РґСѓ
РџРљ СЃРёРЅС…СЂРѕРЅРёР·Р°С†РёСЏ **Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєР°СЏ** С‡РµСЂРµР· Claude Code hooks
(`~/.claude/settings.json`):

- **SessionStart hook** в†’ Р·Р°РїСѓСЃРєР°РµС‚ `~/.claude/scripts/auto-pull.ps1`
  в†’ `git pull --rebase --autostash` (Р°РєС‚СѓР°Р»РёР·РёСЂСѓРµС‚ Р±Р°Р·Сѓ РѕС‚ РґСЂСѓРіРёС… РџРљ).
- **SessionEnd hook** в†’ Р·Р°РїСѓСЃРєР°РµС‚ `~/.claude/scripts/auto-push.ps1`
  в†’ РµСЃР»Рё РµСЃС‚СЊ РёР·РјРµРЅРµРЅРёСЏ РІ whitelist managed paths (agents/, skills/,
  memory/, session-reports/, harvested/, CLAUDE.md) в†’ `git add` +
  `git commit` + `git push origin main`. Personal files (credentials,
  history, plugins, projects) **РЅРёРєРѕРіРґР°** РЅРµ РєРѕРјРјРёС‚СЏС‚СЃСЏ.

Р›РѕРі auto-sync: `~/.claude/auto-sync.log`.

**Р’Р°Р¶РЅРѕ РґР»СЏ РїРѕРЅРёРјР°РЅРёСЏ:**
- Р­С‚Рѕ **РЅРµ РїСЂР°РІРёР»Рѕ РІ CLAUDE.md**, РєРѕС‚РѕСЂРѕРјСѓ СЏ СЃР»РµРґСѓСЋ РєР°Рє РјРѕРґРµР»СЊ вЂ” СЌС‚Рѕ
  СЃРёСЃС‚РµРјРЅС‹Рµ hooks, СЃСЂР°Р±Р°С‚С‹РІР°СЋС‚ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё Р±РµР· РјРѕРµРіРѕ СѓС‡Р°СЃС‚РёСЏ.
- РЎРёСЃС‚РµРјРЅРѕРµ РїСЂР°РІРёР»Рѕ Claude Code В«РЅРµ РїСѓС€РёС‚СЊ Р±РµР· СЏРІРЅРѕР№ РїСЂРѕСЃСЊР±С‹ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏВ»
  РєР°СЃР°РµС‚СЃСЏ **РјРѕРёС…** СЂСѓС‡РЅС‹С… `git push` С‡РµСЂРµР· Bash tool вЂ” РѕРЅРѕ **РЅРµ**
  РѕС‚РјРµРЅСЏРµС‚ auto-sync hooks.
- РџРѕРґСЂРѕР±РЅРѕСЃС‚Рё Рё РёСЃС‚РѕСЂРёСЏ Р»РѕРІСѓС€РµРє РЅР°СЃС‚СЂРѕР№РєРё вЂ” РІ `memory/2026-05-09_hooks-debugging.md`.

---
