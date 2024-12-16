
import pytest
from aiohttp import web
from number_guessing_server import create_room, list_rooms, guess_number, on_startup, on_cleanup


@pytest.fixture
async def app():
    app = web.Application()
    app.router.add_post('/rooms', create_room)
    app.router.add_get('/rooms', list_rooms)
    app.router.add_get('/guess', guess_number)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

@pytest.fixture
async def cli(aiohttp_client, app):
    return await aiohttp_client(app)


async def test_create_room(cli):
    resp = await cli.post('/rooms')
    assert resp.status == 201
    text = await resp.text()
    assert text.isdigit()  

async def test_list_rooms(cli):
    resp = await cli.post('/rooms')
    assert resp.status == 201
    resp = await cli.get('/rooms')
    assert resp.status == 200
    json_resp = await resp.json()
    assert isinstance(json_resp, list)
    assert 'id' in json_resp[0]
    assert 'guess_number' in json_resp[0]
    assert 'score' in json_resp[0]

async def test_guess_number(cli):
    # TODO zmen /create na /rooms (hotovo)
    resp = await cli.post('/rooms') # TODO - tady bude cli.post("/rooms") (hotovo)
    # informace o pokoji maji byt pod GET /rooms/{id} nebo /rooms?id={id} (u tohohle potrebuju poradit)
    room_id = await resp.text()


    resp = await cli.get(f'/guess?number=5&room_id={room_id}')
    assert resp.status == 200
    json = await resp.json()
    assert json in ['UHADNUTO', 'VETSI', 'MENSI'], json


async def test_invalid_endpoint(cli):
    resp = await cli.get('/endpoint-that-not-exist')
    assert resp.status == 404


# TODO - osetrit vstupy klienta, aby server vracel 400 
async def test_guess_non_number(cli):
    resp = await cli.get('/guess?number=x&room_id=1')
    assert resp.status == 400 # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
    #assert await resp.json() == "400: Number must be an integer"
    

async def test_guess_negative_number(cli):
    number = -10
    resp = await cli.get('/guess?number=' + str(number) + '&room_id=1')
    assert resp.status == 400
    #assert await resp.json() == "400: Number must be between 0 and 10"
    

async def test_guess_empty_integer(cli):
    resp = await cli.get('/guess?number=&room_id=1')
    assert resp.status == 400
    #assert await resp.json() == "400: Number must be an integer"



async def test_guess_number_out_of_range(cli):
    number = 100
    resp = await cli.get('/guess?number=' + str(number) + '&room_id=1')
    assert resp.status == 400
    #assert await resp.json() == "400: Number must be between 0 and 10"


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
    
