import json
import asyncio
import os
import subprocess
import time
import pynvml

import websockets
import aiohttp

from prometheus_client import start_http_server, Gauge, Info
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
    """
    获取当前 GPU 设备信息
    :return: GPU 型号、显存大小
    """
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_name = pynvml.nvmlDeviceGetName(handle)
        pynvml.nvmlShutdown()
        return gpu_name.decode('utf-8')
    except Exception:
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
    except Exception:
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
        self._lock = asyncio.Lock()  # Lock for thread-safe updates

        self.extras = Info('extras', 'Extras info')
        self.extras.info({'gpu_name': GPU_NAME, 'pod_name': POD_NAME})

        self.queue_running_gauge = Gauge('queue_running', 'Running tasks in queue')
        self.queue_pending_gauge = Gauge('queue_pending', 'Pending tasks in queue')

        self.cpu_utilization_gauge = Gauge('cpu_utilization', 'CPU utilization percentage')
        self.ram_total_gauge = Gauge('ram_total', 'Total RAM in GB')
        self.ram_used_gauge = Gauge('ram_used', 'Used RAM in GB')
        self.ram_used_percent_gauge = Gauge('ram_used_percent', 'Used RAM percentage')
        self.gpu_utilization_gauge = Gauge('gpu_utilization', 'GPU utilization percentage')
        self.gpu_temperature_gauge = Gauge('gpu_temperature', 'GPU temperature in Celsius')
        self.vram_total_gauge = Gauge('vram_total', 'Total VRAM in GB')
        self.vram_used_gauge = Gauge('vram_used', 'Used VRAM in GB')
        self.vram_used_percent_gauge = Gauge('vram_used_percent', 'Used VRAM percentage')

    async def on_message(self, websocket, path, message):
        try:
            msg = json.loads(message)
            await self.update_data(msg)
        except Exception as e:
            print(f"Error parsing message: {e}")

    async def update_data(self, msg):
        data = msg.get("data", {})
        gpus = data.get("gpus", [{}])
        async with self._lock:
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

            queue_running, queue_pending = await get_task_queue()
            self.queue_running_gauge.set(int(queue_running))
            self.queue_pending_gauge.set(int(queue_pending))

            self.cpu_utilization_gauge.set(self._cpu_utilization)
            self.ram_total_gauge.set(self._ram_total)
            self.ram_used_gauge.set(self._ram_used)
            self.ram_used_percent_gauge.set(self._ram_used_percent)
            self.gpu_utilization_gauge.set(self._gpu_utilization)
            self.gpu_temperature_gauge.set(self._gpu_temperature)
            self.vram_total_gauge.set(self._vram_total)
            self.vram_used_gauge.set(self._vram_used)
            self.vram_used_percent_gauge.set(self._vram_used_percent)

    async def get_metrics(self):
        """Safely retrieve the current metrics."""
        async with self._lock:
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
            }

    async def start_monitor(self):
        uri = "ws://127.0.0.1:8188/ws"
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                await self.on_message(websocket, None, message)


if __name__ == "__main__":
    # Start Prometheus HTTP server
    start_http_server(8000)

    # Create and start the WebSocket client
    client = AsyncWebSocketClient()
    asyncio.get_event_loop().run_until_complete(client.start_monitor())
