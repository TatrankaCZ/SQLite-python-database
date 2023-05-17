import asyncio
from prisma import Prisma


async def main() -> None:
    db = Prisma()
    await db.connect()

    post = await db.post.create(
        {
            'title': 'Prisma test',
            #'desc': 'SQLite database test',
            'published': True,
        }
    )
    print(f'created post: {post.json(indent=2, sort_keys=True)}')

    found = await db.post.find_unique(where={'id': post.id})
    assert found is not None
    print(f'found post: {found.json(indent=2, sort_keys=True)}')

    await db.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
