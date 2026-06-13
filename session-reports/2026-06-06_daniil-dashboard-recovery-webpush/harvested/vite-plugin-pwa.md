# vite-plugin-pwa (vite-pwa/vite-plugin-pwa)

- **URL:** https://github.com/vite-pwa/vite-plugin-pwa
- **Stars:** 4182 (верифицировано GitHub API 2026-06-06)
- **Last commit:** 2026-05-05
- **License:** MIT
- **Описание:** Zero-config PWA для Vite.

## Зачем смотрели

PWA (manifest + offline-shell) и Service Worker для React+Vite 5, чтобы получить
Web Push на iOS (требует установленной PWA) + регистрацию SW.

## Оценка

- Подходит? **Да.**
- Сильные стороны: де-факто стандарт (4.2k★, активный, MIT); режим `injectManifest`
  позволяет писать кастомный SW с push-обработчиком + precache от Workbox; готовый
  хук `useRegisterSW` (`virtual:pwa-register/react`) для регистрации SW из React.
- Слабые стороны / риски: push-уведомления — **out of scope** плагина (нужен custom
  SW через injectManifest; сам push-код пишем мы). Документация по push скудная —
  опираться на референс `11bluetree/vite-pwa-push-notice-app` и elk.zone SW.
- Решение: **используем для PWA/SW-каркаса** (injectManifest + useRegisterSW).
