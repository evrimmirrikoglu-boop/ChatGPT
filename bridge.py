#!/usr/bin/env python3
import argparse
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


def run_http_server(host: str, port: int) -> None:
    web_dir = pathlib.Path(__file__).parent / "web"
    handler = partial(SimpleHTTPRequestHandler, directory=str(web_dir))
    server = ThreadingHTTPServer((host, port), handler)
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PhonePad Web desktop bridge")
    parser.add_argument("--http-host", default="0.0.0.0", help="HTTP host (default: 0.0.0.0)")
    parser.add_argument("--http-port", type=int, default=8765, help="HTTP port (default: 8765)")
    parser.add_argument("--ws-host", default="0.0.0.0", help="WebSocket host (default: 0.0.0.0)")
    parser.add_argument("--ws-port", type=int, default=8766, help="WebSocket port (default: 8766)")
    parser.add_argument(
        "--public-url",
        default="",
        help="Telefonunda açacağın public URL (örn: https://pad.senin-domainin.com)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    local_ip = get_local_ip()

    print("\n=== PhonePad Web hazır ===")
    print("Yerel ağ:")
    print(f"  UI: http://{local_ip}:{args.http_port}")
    print(f"  WS: ws://{local_ip}:{args.ws_port}")
    if args.public_url:
        print("İnternet üzerinden:")
        print(f"  UI: {args.public_url}")
        print("  WS: public URL'inle aynı hostu kullan (https ise wss://)")
    print(f"Token: {SESSION_TOKEN}")
    print("(Çıkış için Ctrl+C)\n")

    http_thread = Thread(target=run_http_server, args=(args.http_host, args.http_port), daemon=True)
    http_thread.start()

    async with websockets.serve(handle_client, args.ws_host, args.ws_port, max_size=1024):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        os._exit(0)
