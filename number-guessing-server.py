# Server
from client import *

from http.server import BaseHTTPRequestHandler

import random
from urllib.parse import parse_qs
# https://docs.aiohttp.org/en/stable/
from aiohttp import web

MIN_NUMBER = 0
MAX_NUMBER = 10
db = Prisma()


async def on_startup(app):
    await db.connect()


async def create_room(request):
    hadane_cislo = random.randrange(MIN_NUMBER, MAX_NUMBER)

    room = await db.room.create({
        'guess_number': hadane_cislo,
        'score': 10
        
    
    })
    return web.Response(text=str(room.id))


async def list_rooms(request):
    rooms = await db.room.find_many()
    out = []
    for room in rooms:
        out.append({
            "id": room.id,
            'guess_number': room.guess_number,
            "score": room.score
        })
    return web.json_response(out)


async def guess_number(request):
    number = request.rel_url.query["number"]
    room_id = request.rel_url.query["room_id"]
    answer = ""
    room = await db.room.find_unique(where={"id": int(room_id)})
    try:
        if int(number) == room.guess_number:
            answer = "UHADNUTO"
            
        elif int(number) > room.guess_number:
            answer = "VETSI"
            
        else:
            answer = "MENSI"
    except:
        answer = "NaN"
    
    return web.Response(text=answer)

class MyServer(BaseHTTPRequestHandler):

    mistnosti = {}

    async def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if self.path.startswith("/guess"):
            print("jsme v guess")
            params = parse_qs(self.path[7:])
            print(params)
            print(params["number"])
            print(params["room_id"])
            number = int(params["number"][0])
            room_id = params["room_id"][0]

            if number > self.mistnosti[room_id]:
                self.wfile.write(bytes("MENSI", "utf-8"))
            elif number < self.mistnosti[room_id]:
                self.wfile.write(bytes("VETSI", "utf-8"))
            else:
                self.wfile.write(bytes("UHADNUTO", "utf-8"))
                MyServer.hadane_cislo = random.randrange(self.X, self.Y)





if __name__ == "__main__":
    app = web.Application()
    app.on_startup.append(on_startup)
    app.add_routes([
        web.get('/create', create_room),
        web.get("/list", list_rooms),
        web.get('/guess', guess_number)
    ])
    web.run_app(app)
    print("Server stopped.")
