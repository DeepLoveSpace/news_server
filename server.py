from aiohttp import web, WSMsgType
from collections import deque
import asyncio

connected_clients = set()
recent_news = deque(maxlen=50)

async def websocket_handler(request):
    ws = web.WebSocketResponse(heartbeat=30.0)
    await ws.prepare(request)

    connected_clients.add(ws)
    print(f"Клиент подключился. Всего клиентов: {len(connected_clients)}")

    for news in recent_news:
        await ws.send_str(news)

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                print(f"Получено от клиента: {msg.data}")
            elif msg.type == WSMsgType.ERROR:
                print(f"Ошибка WebSocket: {ws.exception()}")
    finally:
        connected_clients.discard(ws)
        print(f"Клиент отключился. Осталось: {len(connected_clients)}")

    return ws

async def post_news(request):
    try:
        data = await request.json()
        news_text = data.get("text", "").strip()
        
        if not news_text:
            return web.json_response({"error": "Поле 'text' обязательно"}, status=400)

        recent_news.append(news_text)

        for ws in connected_clients.copy():
            if not ws.closed:
                await ws.send_str(news_text)
        
        print(f"Новость разослана {len(connected_clients)} клиентам: {news_text}")
        return web.json_response({"status": "ok", "sent_to": len(connected_clients)})
        
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

async def index(request):
    """Отдаёт HTML страницу."""
    return web.FileResponse('./index.html')

app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/ws', websocket_handler)
app.router.add_post('/news', post_news)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)