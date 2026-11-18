News WebSocket Server

Сервер на aiohttp: принимает новости через `POST /news`,
рассылает их всем WebSocket-клиентам на `/ws`, хранит последние 50 новостей.

Отправка новости (команда PowerShell)