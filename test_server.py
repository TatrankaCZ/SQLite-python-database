from unittest.mock import AsyncMock, patch

import pytest

from number_guessing_server import on_startup


@pytest.mark.asyncio
async def test_server():
    with patch("number_guessing_server.db", new_callable=AsyncMock) as db_connection:
        await on_startup(None)
        db_connection.connect.assert_awaited_once()
