# SameVibe — бэкенд

Бэкенд мессенджера, который знакомит людей по общим интересам: подбирает собеседников по интересам, управляет друзьями и обеспечивает чат в реальном времени.

Фронтенд на Next.js: [PluxuryPascal/SameVibe](https://github.com/PluxuryPascal/SameVibe)

## Возможности

- **Чат в реальном времени** на WebSockets (Django Channels), сообщения между инстансами идут через Redis channel layer
- **JWT-аутентификация** для REST и WebSocket: токен проверяется на этапе handshake
- **Интересы и друзья**: профиль, выбор интересов, заявки в друзья
- **Медиа** (аватары, вложения) хранятся в Cloudinary
- **OpenAPI-документация** через drf-spectacular, Swagger UI

## Стек

`Python` · `Django` · `Django REST Framework` · `Django Channels` · `Daphne` · `PostgreSQL` · `Redis` · `Simple JWT` · `Cloudinary` · `Docker`

## API

| Префикс | Назначение |
|---|---|
| `/api/v1/token/` | получение, обновление и проверка JWT |
| `/api/v1/users/` | пользователи и профили |
| `/api/v1/interests/` | интересы |
| `/api/v1/friends/` | друзья и заявки |
| `/api/v1/chat/` | чаты и история сообщений |
| `/api/v1/docs/schema/ui/` | Swagger UI |

WebSocket-маршруты чата описаны в `samevibe/chat/routing.py`.

## Структура

```
samevibe/
├── samevibe/     # настройки, ASGI-роутинг (HTTP + WebSocket)
├── users/        # пользователи и профили
├── interests/    # интересы
├── friends/      # друзья
└── chat/         # чаты, WebSocket-консьюмеры
Dockerfile        # multi-stage сборка
```

## Запуск

Конфигурация берётся из переменных окружения: `SECRET_KEY`, `DATABASE_*`, `CLOUDINARY_*`, `EMAIL_*`.

```bash
docker build -t samevibe-back .
docker run --env-file .env -p 8000:8000 samevibe-back
```

Перед стартом контейнер ждёт доступности PostgreSQL на хосте `db:5432`.
