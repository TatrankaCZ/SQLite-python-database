"""
This a server for number guessing game
"""
# Server
import random

# https://docs.aiohttp.org/en/stable/
from aiohttp import web
from prisma import Prisma

MIN_NUMBER = 0
MAX_NUMBER = 10
db = Prisma()


async def on_startup(_):
    """
    Connects to database
    :param app:
    :return:
    """
    await db.connect()


async def create_room():
    hadane_cislo = random.randrange(MIN_NUMBER, MAX_NUMBER)

    room = await db.room.create(
        {
            "guess_number": hadane_cislo,
            "min_number": MIN_NUMBER,
            "max_number": MAX_NUMBER,
        }
    )
    return web.Response(text=str(room.id))


async def list_rooms():
    rooms = await db.room.find_many()
    out = []
    for room in rooms:
        out.append(
            {
                "id": room.id,
                "min_number": room.min_number,
                "max_number": room.max_number,
            }
        )
    return web.json_response(out)


async def guess_number(request):
    number = request.rel_url.query["number"]
    # pylint: disable=unused-variable
    room_id = request.rel_url.query["room_id"]
    # pylint:disable=fixme
    # TODO vyber z databaze pokoj dle room_id
    # TODO porovnej prijate cislo s generovanym
    # TODO a vrat odpoved
    return web.Response(text=str(number))


# class MyServer(BaseHTTPRequestHandler):
#     mistnosti = {}
#
#     async def do_GET(self):
#         self.send_response(200)
#         self.send_header("Content-type", "text/html")
#         self.end_headers()
#
#         if self.path.startswith("/guess"):
#             print("jsme v guess")
#             params = parse_qs(self.path[7:])
#             print(params)
#             print(params["number"])
#             print(params["room_id"])
#             number = int(params["number"][0])
#             room_id = params["room_id"][0]
#
#             if number > self.mistnosti[room_id]:
#                 self.wfile.write(bytes("MENSI", "utf-8"))
#             elif number < self.mistnosti[room_id]:
#                 self.wfile.write(bytes("VETSI", "utf-8"))
#             else:
#                 self.wfile.write(bytes("UHADNUTO", "utf-8"))
#                 MyServer.hadane_cislo = random.randrange(self.X, self.Y)


if __name__ == "__main__":
    app = web.Application()
    app.on_startup.append(on_startup)
    app.add_routes(
        [
            web.get("/create", create_room),
            web.get("/list", list_rooms),
            web.get("/guess", guess_number),
        ]
    )
    web.run_app(app)
    print("Server stopped.")
