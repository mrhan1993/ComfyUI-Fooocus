#!/bin/bash
python3 /ComfyUI/custom_nodes/ComfyUI-Fooocus/monitor.py &
python3 /ComfyUI/custom_nodes/ComfyUI-Fooocus/udp_monitor.py &

exec "$@"