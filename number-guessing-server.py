# Server
import uuid
import mysql.connector
import asyncio

from http.server import HTTPServer, BaseHTTPRequestHandler

import random
from urllib.parse import parse_qs
# https://docs.aiohttp.org/en/stable/
from aiohttp import web

MIN_NUMBER = 0
MAX_NUMBER = 10

#async def on_startup(app):
#    db = mysql.connector.connect(
#    host="localhost",
#    user="admin",
#    password="admin",
#    database="numberguessingdb"
#    )



async def create_room(request):
    hadane_cislo = random.randrange(MIN_NUMBER, MAX_NUMBER)

    room = {
        'guess_number': hadane_cislo,
        "id": str(uuid.uuid4())
    }
    rooms.append(room)
    return web.Response(text=room.id)


async def list_rooms(request):
    #rooms = await room.find_many()
    out = []
    #for room in rooms:
    #    out.append({
    #        "id": room.id,
    #        "min_number": room.min_number,
    #        "max_number": room.max_number
    #    })
    return web.json_response(out)


async def guess_number(request):
    number = request.rel_url.query["number"]
    room_id = request.rel_url.query["room_id"]
    # TODO vyber z databaze pokoj dle room_id
    # TODO porovnej prijate cislo s generovanym
    # TODO a vrat odpoved
    return web.Response(text=str(number))

class MyServer(BaseHTTPRequestHandler):
    
    db = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="numberguessingdb"
    )

    mistnosti = {}

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if self.path == "/create":
            hadane_cislo = random.randrange(MIN_NUMBER, MAX_NUMBER)
            id_mistnosti = str(uuid.uuid4())
            self.mistnosti[id_mistnosti] = hadane_cislo
            self.wfile.write(bytes(id_mistnosti, "utf-8"))
            
        if self.path == "/list":
            for room in self.mistnosti:
                self.wfile.write(bytes(f"{room}\n", "utf-8"))

        if self.path.startswith("/guess"):
            print("jsme v guess")
            params = parse_qs(self.path[7:])
            print(params)
            print(params["number"])
            print(params["room_id"])
            print(params["score"])
            number = int(params["number"][0])
            room_id = params["room_id"][0]
            score = int(params["score"][0])

            if number > self.mistnosti[room_id]:
                if score != 0:
                    score = score - 10
                self.wfile.write(bytes(f"MENSI {score}", "utf-8"))
            elif number < self.mistnosti[room_id]:
                if score != 0:
                    score = score - 10
                self.wfile.write(bytes(f"VETSI {score}", "utf-8"))
            else:
                self.wfile.write(bytes(f"UHADNUTO {score}", "utf-8"))
                cursor = self.db.cursor()

                sql = f"INSERT INTO game_scores (name, score) VALUES ('{room_id}', {score});"
                cursor.execute(sql)
                self.db.commit()





if __name__ == "__main__":
    webServer = HTTPServer(("localhost", 8080), MyServer)
    print("Server started http://%s:%s" % ("localhost", 8080))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    #app = web.Application()
    #app.on_startup.append(on_startup)
    #app.add_routes([
    #    web.get('/create', create_room),
    #    web.get("/list", list_rooms),
    #    web.get('/guess', guess_number)
    #])
    #web.run_app(app)
    print("Server stopped.")
