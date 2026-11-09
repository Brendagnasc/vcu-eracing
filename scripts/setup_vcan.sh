#!/usr/bin/env bash
set -e

if sudo modprobe vcan 2>/dev/null; then
    sudo ip link add dev vcan0 type vcan 2>/dev/null || true
    sudo ip link set up vcan0
    echo "vcan0 pronto"
else
    echo "vcan indisponível neste kernel. Use: export CAN_IFACE=udp"
fi
