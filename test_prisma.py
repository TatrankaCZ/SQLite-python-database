import pytest
from aiohttp import web
from number_guessing_server import create_room, list_rooms, guess_number, on_startup  # Import your server functions here

@pytest.fixture
async def cli(event_loop, aiohttp_client):
    app = web.Application()
    app.router.add_get('/create', create_room)
    app.router.add_get('/list', list_rooms)
    app.router.add_get('/guess', guess_number)
    return await aiohttp_client(app)


async def test_create_room(cli):
    resp = await cli.get('/create')
    assert resp.status == 200
    text = await resp.text()
    assert text.isdigit()  # Assuming the response is the room ID

async def test_list_rooms(cli):
    # create a room first
    await cli.get('/create')
    resp = await cli.get('/list')
    assert resp.status == 200
    json_resp = await resp.json()
    assert isinstance(json_resp, list)
    assert 'id' in json_resp[0]
    assert 'guess_number' in json_resp[0]
    assert 'score' in json_resp[0]

async def test_guess_number(cli):
    # create a room first
    resp = await cli.get('/create')
    room_id = await resp.text()
    
    # guess a number
    resp = await cli.get(f'/guess?number=5&room_id={room_id}')
    assert resp.status == 200
    text = await resp.text()
    assert text in ['UHADNUTO', 'VETSI', 'MENSI']
