#(©)WANGLING
#@i_am_never_die

from aiohttp import web


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    return web_app