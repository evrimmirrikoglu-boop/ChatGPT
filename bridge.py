#!/usr/bin/env python3
import asyncio
import json
import os
import pathlib
import secrets
import socket
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import websockets
from pynput.mouse import Button, Controller

HTTP_HOST = "0.0.0.0"
HTTP_PORT = 8765
WS_HOST = "0.0.0.0"
WS_PORT = 8766

mouse = Controller()
SESSION_TOKEN = secrets.token_urlsafe(6)


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def run_http_server() -> None:
    web_dir = pathlib.Path(__file__).parent / "web"
    handler = partial(SimpleHTTPRequestHandler, directory=str(web_dir))
    server = ThreadingHTTPServer((HTTP_HOST, HTTP_PORT), handler)
    server.serve_forever()


async def handle_client(websocket: websockets.WebSocketServerProtocol) -> None:
    authed = False
    async for raw in websocket:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue

        msg_type = msg.get("type")

        if not authed:
            if msg_type == "auth" and msg.get("token") == SESSION_TOKEN:
                authed = True
                await websocket.send(json.dumps({"type": "auth_ok"}))
            else:
                await websocket.send(json.dumps({"type": "auth_fail"}))
            continue

        if msg_type == "move":
            dx = int(float(msg.get("dx", 0)))
            dy = int(float(msg.get("dy", 0)))
            if dx or dy:
                mouse.move(dx, dy)

        elif msg_type == "scroll":
            dx = int(float(msg.get("dx", 0)) / 2)
            dy = int(float(msg.get("dy", 0)) / 2)
            if dx or dy:
                mouse.scroll(dx, -dy)

        elif msg_type == "click":
            button = msg.get("button", "left")
            target = Button.right if button == "right" else Button.left
            mouse.click(target, 1)

        elif msg_type == "double_click":
            mouse.click(Button.left, 2)


async def main() -> None:
    local_ip = get_local_ip()

    print("\n=== PhonePad Web hazır ===")
    print(f"Telefonunda aç: http://{local_ip}:{HTTP_PORT}")
    print(f"WebSocket: ws://{local_ip}:{WS_PORT}")
    print(f"Token: {SESSION_TOKEN}")
    print("(Çıkış için Ctrl+C)\n")

    http_thread = Thread(target=run_http_server, daemon=True)
    http_thread.start()

    async with websockets.serve(handle_client, WS_HOST, WS_PORT, max_size=1024):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os._exit(0)
