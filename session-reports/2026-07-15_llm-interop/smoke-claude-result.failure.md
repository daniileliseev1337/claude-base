# LLM interop failure: interop-smoke-claude

- Партнёр: `claude`
- Тип: `nonzero_exit`
- Код: `1`

## Диагностика

```text
{"type":"result","subtype":"success","is_error":true,"api_error_status":403,"duration_ms":1669,"duration_api_ms":0,"num_turns":1,"result":"Your organization does not have access to Claude. Please login again or contact your administrator.","stop_reason":"stop_sequence","session_id":"<redacted>","total_cost_usd":0,"usage":{"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"terminal_reason":"completed","fast_mode_state":"off","uuid":"<redacted>"}
```
