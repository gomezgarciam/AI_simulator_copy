import asyncio
import logging

import aiohttp
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proxy")


async def handle_request(request):
    path = request.path_qs
    # /ws/ va al backend (8000), todo lo demás a Streamlit (8501)
    target_port = 8000 if path.startswith("/ws/") else 8501
    target_url = f"http://127.0.0.1:{target_port}{path}"

    # Manejo de WebSockets (Crucial para Streamlit y Live Mode)
    if request.headers.get("Upgrade", "").lower() == "websocket":
        ws_server = web.WebSocketResponse(autoclose=True, autoping=True)
        await ws_server.prepare(request)

        async with aiohttp.ClientSession() as session:
            # Importante: Pasar la URL de WebSocket correcta
            ws_url = f"ws://127.0.0.1:{target_port}{path}"
            try:
                async with session.ws_connect(ws_url) as ws_backend:
                    logger.info(f"Conectado WS a {target_port}: {path}")

                    async def forward(src, dst):
                        try:
                            async for msg in src:
                                if msg.type == aiohttp.WSMsgType.TEXT:
                                    await dst.send_str(msg.data)
                                elif msg.type == aiohttp.WSMsgType.BINARY:
                                    await dst.send_bytes(msg.data)
                                elif msg.type == aiohttp.WSMsgType.CLOSE:
                                    break
                                elif msg.type == aiohttp.WSMsgType.ERROR:
                                    break
                        except Exception:
                            pass
                        finally:
                            await dst.close()

                    await asyncio.gather(
                        forward(ws_server, ws_backend), forward(ws_backend, ws_server)
                    )
            except Exception as e:
                logger.error(f"Error conectando al backend WS en {target_port}: {e}")
        return ws_server

    # Manejo de HTTP normal
    async with aiohttp.ClientSession() as session:
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in ("host", "content-length")
        }
        try:
            async with session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=await request.read(),
                allow_redirects=False,
            ) as resp:
                body = await resp.read()
                out_headers = {
                    k: v
                    for k, v in resp.headers.items()
                    if k.lower()
                    not in ("content-encoding", "transfer-encoding", "content-length")
                }
                return web.Response(body=body, status=resp.status, headers=out_headers)
        except Exception as e:
            return web.Response(text=f"Proxy error: {str(e)}", status=502)


app = web.Application()
app.router.add_route("*", "/{path:.*}", handle_request)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
