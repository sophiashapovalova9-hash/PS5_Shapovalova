import aiohttp
import asyncio
import json
import os
import webbrowser
from datetime import datetime
from aiohttp import web

SERVICES_API_URL = "https://dummyjson.com/products/category/beauty"
BOOKINGS_API_URL = "https://dummyjson.com/carts?limit=5"

semaphore = asyncio.Semaphore(3)

DATA_FILE = "data.json"
BOOKING_FILE = "booking.json"


async def fetch_data(url, session):
    async with semaphore:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    return await response.json()
        except Exception:
            pass
        return None


async def get_salon_info():
    async with aiohttp.ClientSession() as session:
        services_task = fetch_data(SERVICES_API_URL, session)
        bookings_task = fetch_data(BOOKINGS_API_URL, session)
        
        services_data, bookings_data = await asyncio.gather(services_task, bookings_task)
        
        return {
            "services": services_data,
            "bookings": bookings_data,
            "timestamp": datetime.now().isoformat()
        }


def save_data(data, filename=DATA_FILE):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")


async def collector_loop():
    while True:
        data = await get_salon_info()
        if data and (data["services"] or data["bookings"]):
            save_data(data)
        await asyncio.sleep(600)


def load_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def load_bookings():
    if not os.path.exists(BOOKING_FILE):
        return []
    try:
        with open(BOOKING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_bookings(bookings):
    with open(BOOKING_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)


def render_table(bookings):
    if not bookings:
        return '<p class="empty">Пока нет записей.</p>'
    rows = ""
    for b in bookings:
        rows += (
            f"<tr><td>{b.get('name', '')}</td>"
            f"<td>{b.get('phone', '')}</td>"
            f"<td>{b.get('service', '')}</td>"
            f"<td>{b.get('date', '')} {b.get('time', '')}</td></tr>"
        )
    return (
        "<table><thead><tr>"
        "<th>Имя</th><th>Телефон</th><th>Услуга</th><th>Дата/время</th>"
        "</tr></thead><tbody>" + rows + "</tbody></table>"
    )


async def handle_index(request):
    bookings = load_bookings()
    success = '<div class="ok">Ваша заявка принята.</div>' if request.query.get("ok") else ""
    html_template = load_file("index.html")
    html_page = (html_template
                 .replace("[SUCCESS]", success)
                 .replace("[COUNT]", str(len(bookings)))
                 .replace("[TABLE]", render_table(bookings)))
    return web.Response(text=html_page, content_type="text/html")


async def handle_css(request):
    css_content = load_file("style.css")
    return web.Response(text=css_content, content_type="text/css")


async def handle_book(request):
    form = await request.post()
    booking = {
        "name": form.get("name", "").strip(),
        "phone": form.get("phone", "").strip(),
        "service": form.get("service", "").strip(),
        "date": form.get("date", "").strip(),
        "time": form.get("time", "").strip(),
        "created": datetime.now().isoformat(),
    }
    if booking["name"] and booking["phone"] and booking["service"]:
        bookings = load_bookings()
        bookings.append(booking)
        save_bookings(bookings)
    return web.HTTPFound("/?ok=1")


async def start_web():
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_post("/book", handle_book)
    app.router.add_get("/style.css", handle_css)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8000)
    await site.start()


async def main():
    await start_web()
    print("Сервер запущен: http://127.0.0.1:8000")
    webbrowser.open("http://127.0.0.1:8000")
    
    asyncio.create_task(collector_loop())
    
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass