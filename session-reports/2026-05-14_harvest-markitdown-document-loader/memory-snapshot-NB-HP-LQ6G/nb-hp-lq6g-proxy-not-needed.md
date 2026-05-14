---
name: nb-hp-lq6g-proxy-not-needed
description: "На машине NB-HP-LQ6G env HTTP_PROXY/HTTPS_PROXY на scuf-meta.ru:10894 ломает git push, но сам git ходит до GitHub напрямую без прокси"
metadata: 
  node_type: memory
  type: project
  originSessionId: e6d76b06-e24e-44ed-8206-0b7a8dc98b77
---

На рабочей машине пользователя `NB-HP-LQ6G` (Windows 11, login `ifesenko`) выставлены `HTTP_PROXY` и `HTTPS_PROXY` на корп-прокси `scuf-meta.ru:10894` с inline credentials. При попытке `git push origin main` с активным прокси выдаёт `fatal: ... Proxy CONNECT aborted`. При очистке proxy-env в подпроцессе (`Remove-Item Env:HTTP_PROXY,...`) git ходит до github.com **напрямую** и push работает.

**Why:** прокси `scuf-meta.ru:10894` либо применяет правило «native git не пропускаем», либо вообще не нужен для исходящего трафика этой машины (сеть выходит наружу мимо прокси). uvx и Claude Code WebFetch работают и с прокси, и без него — у них своя сетевая логика.

**How to apply:** перед любым `git push` / `git fetch` из PowerShell на этой машине — очищать proxy-env:
```powershell
Remove-Item Env:HTTP_PROXY,Env:HTTPS_PROXY,Env:http_proxy,Env:https_proxy,Env:ALL_PROXY -ErrorAction SilentlyContinue
git -c http.proxy= -c https.proxy= push origin main
```
Долговременное решение — спросить у Даниила: обновить `auto-push.ps1`, чтобы он сам очищал прокси-env перед push, и/или убрать proxy-env из системного окружения этой машины.

См. также [[fessenkoim-arch-github]], [[git-push-diagnostic-order]].
