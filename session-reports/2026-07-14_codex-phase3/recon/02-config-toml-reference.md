# Разведка 2: полный референс config.toml (Codex 0.144.x)

Дата: 2026-07-14 · Агент: sonnet · Статус: завершено

## Главное
1. **`[profiles.X]` внутри config.toml УСТАРЕЛ с 0.134** — верхнеуровневый `profile="X"` «no longer supported». Текущая механика: **отдельный файл** `$CODEX_HOME/<name>.config.toml`, выбор `codex --profile <name>`. Приоритет: CLI-флаги > project config (`.codex/`) > файл профиля > user config > system > built-in (между «профиль» и «project» источники слегка расходятся). Эталон Эпика 2 проектировать под отдельные файлы; `codex_sync.py` профили пока не пишет — нужен новый рендер-шаг (например из `codex-layer/profiles/{plus,pro}.toml`).
2. Документация переехала: github docs/config.md — заглушка; истина = learn.chatgpt.com/docs/config-file/* (редирект с developers.openai.com). Самый надёжный источник — **config-sample** (полный файл с комментариями).
3. Наши обходы подтверждены официальными открытыми issue: hooks в десктопе — регрессия #21639; `[[skills.config]]` игнорируется — #20210, #14161; user config.toml на Mac Desktop не грузится — #25145. Чинить нечего — риск на стороне OpenAI.
4. Порог авто-компакции ~270000 — эмпирика, НЕ документированный дефолт (`model_auto_compact_token_limit` по умолчанию unset).

## Каталог ключей (сжатый; полный — в config-sample)
- **Модель/reasoning:** model, model_provider, model_reasoning_effort (minimal..xhigh), plan_mode_reasoning_effort, model_reasoning_summary, model_verbosity, model_supports_reasoning_summaries, model_context_window, model_auto_compact_token_limit(+_scope), tool_output_token_limit, model_instructions_file (вместо AGENTS.md!), model_catalog_json, service_tier, review_model, personality.
- **Approval/sandbox:** approval_policy (untrusted|on-request*|never|granular{...}), approvals_reviewer, sandbox_mode (read-only*|workspace-write|danger-full-access), [sandbox_workspace_write] writable_roots/network_access/exclude_slash_tmp/exclude_tmpdir_env_var, allow_login_shell, default_permissions + [permissions.<name>] (новая гранулярная модель — взять на заметку).
- **MCP stdio:** enabled(true)/required(false)/command/args/env/env_vars/cwd/experimental_environment/startup_timeout_sec(10)/tool_timeout_sec(60)/enabled_tools/disabled_tools/scopes/oauth_resource; HTTP: url/bearer_token_env_var/http_headers/env_http_headers; per-tool approval_mode (auto|prompt|writes|approve), default_tools_approval_mode; глобально mcp_oauth_credentials_store/callback_port/callback_url.
- **Agents:** [agents] max_threads=6, max_depth=1, job_max_runtime_seconds=1800, interrupt_message; [agents.<name>] description, config_file, nickname_candidates — совпадает с нашими agents/*.toml.
- **Features:** apps, shell_tool, multi_agent, goals, personality, fast_mode, shell_snapshot, unified_exec (не Windows), skill_mcp_dependency_install, enable_request_compression, remote_plugin, hooks (дефолт спорный: sample=false, basic=true), memories(false), prevent_idle_sleep, network_proxy(+подключи), code_mode(dev), rollout_budget(dev). web_search в [features] — deprecated → верхнеуровневый `web_search = cached*|indexed|live|disabled`.
- **Hooks:** hooks.json (сиблинг) ИЛИ [[hooks.<Event>]] в config.toml (одновременно — warning). События: PreToolUse, PostToolUse, PermissionRequest, PreCompact, PostCompact, SessionStart, SubagentStart, SubagentStop, UserPromptSubmit, Stop. Project-hooks только при trust_level="trusted".
- **Прочее:** [shell_environment_policy] inherit=all*/core/none, set, include_only, exclude (KEY/SECRET/TOKEN фильтруются по умолчанию); [history] persistence/max_bytes; sqlite_home; log_dir; hide_agent_reasoning; file_opener (vscode|cursor|...); check_for_update_on_startup; [projects."<path>"] trust_level; project_doc_max_bytes(32768); [tui] (CLI-only); [desktop] (десктоп-only); [windows] sandbox=elevated|unelevated, sandbox_private_desktop; [analytics]/[feedback]/[otel]; [apps.*] (connectors) ≠ [plugins."X@Y"] (маркетплейс десктопа).

## Локальный конфиг (вне managed-блока, не трогать)
model="gpt-5.6-sol", model_reasoning_effort="high", notify=[computer-use exe], [marketplaces]×2, [plugins]×9 (visualize, documents, pdf, spreadsheets, presentations, template-creator, computer-use, chrome, browser), [features] js_repl=false, [mcp_servers.node_repl] (startup_timeout_sec=120 — рабочий пример ключа), [desktop]×12, [windows] sandbox="elevated", [projects] trust.

## Черновик эталона
- База config.toml (общая для Plus/Pro): web_search="cached", file_opener="vscode", [agents] max_threads=6/max_depth=1, [shell_environment_policy] inherit="all", [sandbox_workspace_write] network_access=false + managed-блок MCP.
- `~/.codex/plus.config.toml`: model="gpt-5.6-luna", effort=medium, approval on-request, workspace-write.
- `~/.codex/pro.config.toml`: model="gpt-5.6-sol", effort=high (на Pro-машине можно не создавать — совпадает с base). Выбор — решение владельца.

## Версии
Стабильная 0.144.4 (патчи без user-facing изменений), 0.145.0-alpha.* без changelog. Рекомендация: остаться на 0.144.x.

## Источники
learn.chatgpt.com/docs/config-file/{config-basic,config-advanced,config-reference,config-sample}; openai/codex issues #25145, #21639, #20210, #14161; GitHub Releases openai/codex. Непроверенное помечено в тексте (дефолт features.hooks, порог 270K, порядок precedence).
