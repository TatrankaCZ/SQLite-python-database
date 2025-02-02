import random

import pytest
from number_guessing_server import create_app, db, on_cleanup
from dotenv import load_dotenv

load_dotenv(".env.test")

async def on_startup(app):
    await db.connect()


@pytest.fixture
async def app():
    app_object = create_app()
    app_object.on_startup.append(on_startup)
    app_object.on_cleanup.append(on_cleanup)
    return app_object

@pytest.fixture
async def cli(aiohttp_client, app):
    return await aiohttp_client(app)


async def test_create_room(cli):
    resp = await cli.post('/rooms', json={
        "min": 1,
        "max": 100
    })
    assert resp.status == 201
    text = await resp.text()
    assert text.isdigit() 

    room = await db.room.find_unique(where={"id": int(text)})
    assert room.min_number == 1
    assert room.max_number == 100


@pytest.fixture
def create_room():
    async def inner(expected_number=random.randint(1, 100)):
        room = await db.room.create({
            'guess_number': expected_number,
            'score': 10,
            'min_number': 1,
            'max_number': 100
        })
        return room
    return inner


async def test_list_rooms(cli):
    resp = await cli.post('/rooms', json={
        "min": 1,
        "max": 100
    })
    assert resp.status == 201
    resp = await cli.get('/rooms')
    assert resp.status == 200
    json_resp = await resp.json()
    assert isinstance(json_resp, list)
    assert 'id' in json_resp[0]
    assert 'guess_number' in json_resp[0]
    assert 'score' in json_resp[0]

@pytest.mark.parametrize(
    "expected_number,guess_number,status",
    [
        (33, 55, "bigger"),
        (55, 33, "lesser"),
        (50, 50, "found")
    ]
)

async def test_guess_number(cli, create_room, expected_number, guess_number, status):
    room = await create_room(expected_number)
    resp = await cli.get(f'/guess?number={guess_number}&room_id={room.id}')

    assert resp.status == 200
    guess_data = await resp.json()
    assert guess_data["status"] == status


async def test_invalid_endpoint(cli):
    resp = await cli.get('/endpoint-that-not-exist')
    assert resp.status == 404


# TODO - osetrit vstupy klienta, aby server vracel 400 
async def test_guess_non_number(cli, create_room):
    room = await create_room()
    # TODO - tady chybi vytvoreni pokoje
    resp = await cli.get('/guess?number=x&room_id=1')
    assert resp.status == 400 # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
    #assert await resp.json() == "400: Number must be an integer"
    

async def test_guess_negative_number(cli):
    # TODO - tady chybi vytvoreni pokoje
    number = -10
    resp = await cli.get('/guess?number=' + str(number) + '&room_id=1')
    assert resp.status == 400
    #assert await resp.json() == "400: Number must be between 0 and 10"
    

async def test_guess_empty_integer(cli):
    # TODO - tady chybi vytvoreni pokoje
    resp = await cli.get('/guess?number=&room_id=1')
    assert resp.status == 400, await resp.text()
    #assert await resp.json() == "400: Number must be an integer"



# TODO / az bude definovany rozsah v databazi
# async def test_guess_number_out_of_range(cli):
#     TODO - tady chybi vytvoreni pokoje
#     number = 100
#     resp = await cli.get('/guess?number=' + str(number) + '&room_id=1')
#     assert resp.status == 400, await resp.text()
#     #assert await resp.json() == "400: Number must be between 0 and 10"



# TODO - novy test
# 1. vytvor room rucne pres sql insert
# 2. testuj rozsah cisel v pokoji
# 3. testuj, zda doslo k nalezeni spraveneho cisla


async def test_guess_empty_room(cli):
    resp = await cli.get('/guess?number=5&room_id=')
    assert resp.status == 400
    #assert await resp.json() == "400: Room doesn't exist"


async def test_guess_special_character(cli):
    characterList = ["@", "#", "&", "\\", "/", "|", "*", "!", "%", "$", "<", ">"]
    for i in characterList:
        resp = await cli.get('/guess?number=' + str(i) + '&room_id=1')    
    assert resp.status == 400
    #assert await resp.json() == "400: Number must be an integer"
    
