---
name: fessenkoim-arch-github
description: Машина NB-HP-LQ6G пушит в claude-base под GitHub-аккаунтом fessenkoim-arch (личный аккаунт пользователя)
metadata: 
  node_type: memory
  type: project
  originSessionId: e6d76b06-e24e-44ed-8206-0b7a8dc98b77
---

Windows Credential Manager + Git Credential Manager на машине `NB-HP-LQ6G` отдают токен GitHub-аккаунта `fessenkoim-arch`. Этот аккаунт **добавлен collaborator'ом** в репо `daniileliseev1337/claude-base` Даниилом 2026-05-14 после того, как первая попытка push выдала 403 `Permission denied`.

**Why:** auto-sync hooks claude-base работают с remote `https://github.com/daniileliseev1337/claude-base.git`, push-доступ к нему даётся индивидуально (внутренний круг). Изначально `fessenkoim-arch` доступа не имел, отсюда 403.

**How to apply:** если на этой машине push снова упадёт с `Permission denied to fessenkoim-arch` — проверять не PAT (он валиден), а **факт активности collaborator-приглашения** (https://github.com/daniileliseev1337/claude-base/invitations) или то, что аккаунт не удалили из коллабораторов. Не пытаться менять credential helper без явной отмашки пользователя.

См. также [[nb-hp-lq6g-proxy-not-needed]], [[git-push-diagnostic-order]].
