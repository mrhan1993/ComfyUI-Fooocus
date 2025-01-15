import json
import asyncio
import socket
import os
import subprocess
import time

import pynvml
import websockets
import aiohttp

from apis.utils.port_check import is_port_alive


while True:
    try:
        live = is_port_alive('127.0.0.1', 8188)
        if live:
            break
    except Exception as e:
        print("Waiting for server to start")
        time.sleep(3)
        continue


def get_gpu_info():
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        pynvml.nvmlShutdown()
        return gpu_name.decode('utf-8')
    except Exception as e:
        print(f"Failed to get GPU info: {e}")
        return "Unknown"


async def get_task_queue():
    url = "http://127.0.0.1:8188/queue"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                res = await resp.text()
                res = json.loads(res)
                queue_running = len(res.get("queue_running", 0))
                queue_pending = len(res.get("queue_pending", 0))
                return queue_running, queue_pending
    except Exception as e:
        print(f"Failed to get task queue: {e}")
        return 0, 0


HOST_NAME = subprocess.getoutput("hostname")
GPU_NAME = get_gpu_info()
POD_NAME = os.getenv("POD_NAME", HOST_NAME)


class AsyncWebSocketClient:
    def __init__(self):
        self._cpu_utilization = 0
        self._ram_total = 0
        self._ram_used = 0
        self._ram_used_percent = 0
        self._gpu_utilization = 0
        self._gpu_temperature = 0
        self._vram_total = 0
        self._vram_used = 0
        self._vram_used_percent = 0
        self._queue_running = 0
        self._queue_pending = 0
        self._extras = {'gpu_name': GPU_NAME, 'pod_name': POD_NAME}

    async def on_message(self, message):
        try:
            msg = json.loads(message)
            await self.update_data(msg)
        except Exception as e:
            print(f"Error parsing message: {e}")

    async def update_data(self, msg):
        data = msg.get("data", {})
        gpus = data.get("gpus", [{}])
        self._cpu_utilization = data.get("cpu_utilization", 0)
        self._ram_total = round(data.get("ram_total", 0) / 1024 / 1024 / 1024, 2)
        self._ram_used = round(data.get("ram_used", 0) / 1024 / 1024 / 1024, 2)
        self._ram_used_percent = round(data.get("ram_used_percent", 0), 2)
        gpu = gpus[0] if gpus else {}
        self._gpu_utilization = gpu.get("gpu_utilization", 0)
        self._gpu_temperature = gpu.get("gpu_temperature", 0)
        self._vram_total = round(gpu.get("vram_total", 0) / 1024 / 1024 / 1024, 2)
        self._vram_used = round(gpu.get("vram_used", 0) / 1024 / 1024 / 1024, 2)
        self._vram_used_percent = round(gpu.get("vram_used_percent", 0), 2)
        self._queue_running, self._queue_pending = await get_task_queue()

    async def get_metrics(self):
        return {
            'cpu_utilization': self._cpu_utilization,
            'ram_total': self._ram_total,
            'ram_used': self._ram_used,
            'ram_used_percent': self._ram_used_percent,
            'gpu_utilization': self._gpu_utilization,
            'gpu_temperature': self._gpu_temperature,
            'vram_total': self._vram_total,
            'vram_used': self._vram_used,
            'vram_used_percent': self._vram_used_percent,
            'queue_running': self._queue_running,
            'queue_pending': self._queue_pending,
            'extras': self._extras
        }

    async def start_monitor(self):
        uri = "ws://127.0.0.1:8188/ws"
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    print("WebSocket connected")
                    while True:
                        message = await websocket.recv()
                        await self.on_message(message)
            except Exception as e:
                print(f"WebSocket connection error: {e}, retrying in 5 seconds...")
                await asyncio.sleep(5)


class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, ws_client):
        self.ws_client = ws_client

    def connection_made(self, transport):
        self.transport = transport
        print("UDP server started on 0.0.0.0:8189")

    def datagram_received(self, data, addr):
        print(f"Received from {addr}: {data.decode('utf-8')}")
        asyncio.create_task(self.handle_udp(data, addr))

    async def handle_udp(self, data, addr):
        send_data = json.dumps(await self.ws_client.get_metrics())
        self.transport.sendto(send_data.encode('utf-8'), addr)

async def udp_server(ws_client: AsyncWebSocketClient):
    loop = asyncio.get_event_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPProtocol(ws_client),
        local_addr=('0.0.0.0', 8189)
    )
    await asyncio.Event().wait()  # Keep the server running indefinitely

async def main():
    client = AsyncWebSocketClient()
    await asyncio.gather(
        client.start_monitor(),
        udp_server(client)
    )

if __name__ == "__main__":
    socket.connect(("127.0.0.1", 8188))
    asyncio.run(main())
