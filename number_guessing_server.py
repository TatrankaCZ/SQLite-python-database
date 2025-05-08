# Server
from calendar import c
import os

from client import Prisma
from dotenv import load_dotenv

import random
from urllib.parse import parse_qs
# https://docs.aiohttp.org/en/stable/
from aiohttp import web




async def on_startup(app):
    app.db = Prisma()
    # db = Prisma()
    await app.db.connect()
    
async def on_cleanup(app):

    await app.db.disconnect()


async def create_room(request):  # pokud je vyzadovan callback argument (puvodne v definic funkce bylo request) a neni pouzivan uvnitr funkce, pouziva se podtrzitko
    post_data = await request.json()

    min_ = int(post_data["min"])
    max_ = int(post_data["max"])

    hadane_cislo = random.randrange(min_, max_)
    # TODO - rozsah hodnot bude endpoint prijimat v POST datech [HOTOVO]

    room = await request.app.db.room.create({
        'guess_number': hadane_cislo,
        'score': 10,
        'min_number': min_,
        'max_number': max_,
        'completed': False
    })
    return web.json_response(text=str(room.id), status=201)


async def list_rooms(request):
    rooms = await request.app.db.room.find_many()
    out = []
    for room in rooms:
        out.append({
            "id": room.id,
            'guess_number': room.guess_number,
            "score": room.score,
            "completed": room.completed
        })
    # TODO na klientu osetri chyby serveru
    return web.json_response(out)


async def guess_number(request):
    params = request.rel_url.query
    if "number" not in params:
        return web.HTTPBadRequest(reason="Missing 'number'")
    if "room_id" not in params:
        return web.HTTPBadRequest(reason="Missing 'room_id'")
    try:
        number = int(params["number"])
    except ValueError:
        return web.HTTPBadRequest(reason="number must be an integer")
    try:
        room_id = int(params["room_id"])
    except ValueError:
        return web.HTTPBadRequest(reason="room_id must be an integer")
    if number < 0:
        return web.HTTPBadRequest(reason="number must be positive")
    room = await request.app.db.room.find_unique(where={"id": int(room_id)})

    answer = ""
    try:
        if int(number) == room.guess_number:
            answer = "found"

        elif room.score <= 1:
            answer = "lost"
            room.completed = True
            room.score = 0
            
        elif int(number) > room.guess_number:
            answer = "bigger"
            if room.score > 0:
                room.score -= 1
            
        elif int(number) < room.guess_number:
            answer = "lesser"
            if room.score > 0:
                room.score -= 1

    except:
        answer = "NaN"

    out = {
        "status": answer,
    }
    await request.app.db.room.update(where={"id": room_id}, data={"score": room.score, "completed": True})


    return web.json_response(out)


def create_app():
    app = web.Application()
    app.add_routes([
        # TODO zmenove requesty se provadeji pomoci metody POST, popr. pro update zaznamu pres PUT a PATCH (hotovo?)
        # web.post("/create", create_room)
        #   https://cs.wikipedia.org/wiki/Representational_State_Transfer#:~:text=distribuuje%20v%20RPC.-,Vlastnosti,-metod%5Beditovat
        web.post('/create', create_room), # zde nema byt GET (hotovo)
        web.post("/rooms", create_room),
        web.get("/rooms", list_rooms),
        web.get('/guess', guess_number)
    ])
    return app

if __name__ == "__main__":
    app = create_app()
    app.on_startup.append(on_startup)
    web.run_app(app, port=8081)
    load_dotenv(".env")
    print("Server stopped.")
