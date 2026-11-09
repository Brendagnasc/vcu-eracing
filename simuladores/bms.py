import threading
import time

import can

from simuladores.barramento import abrir_barramento
from simuladores.mensagens import DB

MSG_BMS = DB.get_message_by_name("BMS_STATUS")
MSG_INV = DB.get_message_by_name("INV_STATUS")

PERIODO = 0.1           # 10 Hz
CELULAS_SERIE = 96
CAPACIDADE_AH = 14.0
RESISTENCIA = 0.1       # ohm, resistência interna do pack
CAPACIDADE_TERMICA = 30000.0  # J/K

estado = {"ts_ativo": False, "falha": False}


def ler_teclado():
    print("Comandos: t + Enter liga/desliga o TS | f + Enter liga/desliga falha")
    while True:
        cmd = input().strip().lower()
        if cmd == "t":
            estado["ts_ativo"] = not estado["ts_ativo"]
            print(f"TS ativo: {estado['ts_ativo']}")
        elif cmd == "f":
            estado["falha"] = not estado["falha"]
            print(f"Falha BMS: {estado['falha']}")


def main():
    bus = abrir_barramento()
    threading.Thread(target=ler_teclado, daemon=True).start()

    soc = 0.9
    corrente = 0.0
    temperatura = 25.0
    proximo = time.monotonic()

    try:
        while True:
            # 1. Lê tudo que chegou, sem bloquear
            msg = bus.recv(timeout=0)
            while msg is not None:
                if msg.arbitration_id == MSG_INV.frame_id:
                    corrente = MSG_INV.decode(msg.data)["CORRENTE_DC"]
                msg = bus.recv(timeout=0)

            # 2. Física do pack
            if not estado["ts_ativo"]:
                corrente = 0.0
            soc -= corrente * PERIODO / 3600 / CAPACIDADE_AH
            soc = min(max(soc, 0.0), 1.0)
            tensao = CELULAS_SERIE * (3.5 + 0.7 * soc) - corrente * RESISTENCIA
            calor = corrente ** 2 * RESISTENCIA
            temperatura += (calor / CAPACIDADE_TERMICA - (temperatura - 25) * 0.001) * PERIODO

            # 3. Envia o status
            dados = MSG_BMS.encode({
                "TENSAO_PACK": tensao,
                "CORRENTE_PACK": corrente,
                "SOC": soc * 100,
                "TEMP_MAX_CELULA": round(temperatura),
                "TS_ATIVO": int(estado["ts_ativo"]),
                "FALHA_BMS": int(estado["falha"]),
            })
            bus.send(can.Message(arbitration_id=MSG_BMS.frame_id, data=dados, is_extended_id=False))

            # 4. Espera o próximo ciclo
            proximo += PERIODO
            time.sleep(max(0.0, proximo - time.monotonic()))
    except KeyboardInterrupt:
        pass
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
