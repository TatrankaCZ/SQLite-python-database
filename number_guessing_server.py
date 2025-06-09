# Server
from calendar import c
import hashlib
import os
import requests

from client import Prisma
from dotenv import load_dotenv

import random
from urllib.parse import parse_qs
# https://docs.aiohttp.org/en/stable/
from aiohttp import web

EMAIL_ENCRYPT_PASSWORD = "1ad165188847264634ac1d2f3f1519418e6ad689"


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

    room = await request.app.db.room.create({
        'guess_number': hadane_cislo,
        'score': 10,
        'min_number': min_,
        'max_number': max_,
        'completed': False,
    })
    return web.json_response(text=str(room.id), status=201)

def send_simple_message(email, code):
    res = requests.post(
        "https://api.mailgun.net/v3/sandbox0e68097b9ede45b890b4acbd86886e01.mailgun.org/messages",
        auth=("api", os.getenv('API_KEY', 'API_KEY')),
        data={"from": "Mailgun Sandbox <postmaster@sandbox0e68097b9ede45b890b4acbd86886e01.mailgun.org>",
              "to": email,
              "subject": "Auth code from Number Guessing",
              "text": f"Hello \n\n your auth code is: {code}"})

    res.raise_for_status()
    return res

genCode = None

async def login(request):
    data = await request.json()
    email = data.get("email")
    code = data.get("code")
    global genCode

    if not email:
        return web.HTTPBadRequest(reason="Missing 'email'")
    if not code:
        genCode = random.randint(1000, 9999)
        send_simple_message(email, genCode)
        return web.json_response(text="Kód pro přihlášení zaslán na e-mail.", status=202)
    if code == str(genCode):
        hashKey = hashlib.md5(email.encode("ascii") + EMAIL_ENCRYPT_PASSWORD.encode("ascii")).hexdigest()
        userExist = False
        with open("./hash.txt", "r") as file:
            existing_hashes = file.readlines()
            if f"{email}:{hashKey}\n" in existing_hashes:
                userExist = True
        if not userExist:
            with open("./hash.txt", "a") as file:
                file.write(f"{email}:{hashKey}\n")
            print(hashKey)
        return web.json_response({"hashKey": hashKey, "text": "Přihlášení úspěšné."}, status=200)

    return web.json_response(text="Přihlášení neúspěšné.", status=401)




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

async def getGuesses(request):
    params = request.rel_url.query
    print("Parametry:", params)
    if "room_id" not in params:
        return web.HTTPBadRequest(reason="Missing 'room_id'")
    try:
        room_id = int(params["room_id"])
    except ValueError:
        return web.HTTPBadRequest(reason="room_id must be an integer")

    guesses = await request.app.db.guesslog.find_many(where={"roomId": room_id})
    out = []
    for guess in guesses:
        out.append({
            "id": guess.id,
            "guess": guess.guess,
            "result": guess.result,
            "roomId": guess.roomId
        })
    return web.json_response(out)



async def guess_number(request):
    params = request.rel_url.query
    print("Parametry:", params)
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
            room.completed = True

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


    await request.app.db.guesslog.create({
        "guess": number,
        "result": answer,
        "roomId": room_id
    })

    out = {
        "status": answer,
    }
    await request.app.db.room.update(where={"id": room_id}, data={"score": room.score, "completed": room.completed})


    return web.json_response(out)


def create_app():
    app = web.Application()
    app.add_routes([
        #https://cs.wikipedia.org/wiki/Representational_State_Transfer#:~:text=distribuuje%20v%20RPC.-,Vlastnosti,-metod%5Beditovat
        web.post('/create', create_room),
        web.post("/rooms", create_room),
        web.get("/rooms", list_rooms),
        web.get('/guess', guess_number),
        web.get('/logs', getGuesses),
        web.post('/login', login)
    ])
    return app

if __name__ == "__main__":
    app = create_app()
    load_dotenv(".env")
    app.on_startup.append(on_startup)
    web.run_app(app, port=8081)
    print("Server stopped.")
