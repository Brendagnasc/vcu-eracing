import os
import can


def abrir_barramento():
    tipo = os.getenv("CAN_IFACE", "socketcan")
    if tipo == "socketcan":
        return can.Bus(interface="socketcan", channel="vcan0")
    # Plano B: barramento simulado via UDP multicast
    return can.Bus(interface="udp_multicast", channel="239.74.163.2")
