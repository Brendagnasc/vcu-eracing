import math
import time

import can

from simuladores.barramento import abrir_barramento
from simuladores.mensagens import DB

MSG_CMD = DB.get_message_by_name("VCU_CMD_INV")
MSG_BMS = DB.get_message_by_name("BMS_STATUS")
MSG_INV = DB.get_message_by_name("INV_STATUS")

PERIODO = 0.01          # 100 Hz
TIMEOUT_CMD = 0.1       # watchdog: 100 ms sem comando zera o torque
TAU_PRECARGA = 0.5      # s, constante de tempo do circuito de pré-carga

# Modelo simples do carro
MASSA = 280.0           # kg, carro + piloto
RAIO_RODA = 0.26        # m
REDUCAO = 4.0           # relação motor:roda
CDA = 1.2               # m², coeficiente de arrasto x área frontal
CRR = 0.015             # coeficiente de resistência ao rolamento
EFICIENCIA = 0.9


def main():
    bus = abrir_barramento()

    torque_req = 0.0
    habilita = False
    ultimo_cmd = 0.0
    ts_ativo = False
    tensao_pack = 0.0
    tensao_dc = 0.0
    velocidade = 0.0    # m/s
    temp_motor = 25.0
    ciclos = 0
    proximo = time.monotonic()

    try:
        while True:
            agora = time.monotonic()

            # 1. Lê comandos da VCU e status do BMS
            msg = bus.recv(timeout=0)
            while msg is not None:
                if msg.arbitration_id == MSG_CMD.frame_id:
                    cmd = MSG_CMD.decode(msg.data)
                    torque_req = cmd["TORQUE_REQ"]
                    habilita = bool(cmd["HABILITA"])
                    ultimo_cmd = agora
                elif msg.arbitration_id == MSG_BMS.frame_id:
                    bms = MSG_BMS.decode(msg.data)
                    ts_ativo = bool(bms["TS_ATIVO"])
                    tensao_pack = bms["TENSAO_PACK"]
                msg = bus.recv(timeout=0)

            # 2. Barramento DC: sobe pela pré-carga ou descarrega
            alvo = tensao_pack if ts_ativo else 0.0
            tensao_dc += (alvo - tensao_dc) * PERIODO / TAU_PRECARGA

            # 3. Watchdog: só aplica torque com comando recente e TS ativo
            comando_valido = habilita and (agora - ultimo_cmd) < TIMEOUT_CMD
            torque = torque_req if (comando_valido and ts_ativo) else 0.0

            # 4. Dinâmica do carro (segunda lei de Newton)
            forca = torque * REDUCAO / RAIO_RODA
            arrasto = 0.5 * 1.2 * CDA * velocidade ** 2
            rolamento = CRR * MASSA * 9.81 if velocidade > 0 else 0.0
            velocidade += (forca - arrasto - rolamento) / MASSA * PERIODO
            velocidade = max(velocidade, 0.0)

            omega = velocidade / RAIO_RODA * REDUCAO   # rad/s no motor
            rpm = omega * 60 / (2 * math.pi)

            # 5. Corrente puxada do pack (potência elétrica / tensão)
            potencia = torque * omega
            potencia = potencia / EFICIENCIA if potencia > 0 else potencia * EFICIENCIA
            corrente = potencia / tensao_dc if tensao_dc > 10 else 0.0
            corrente = min(max(corrente, -500.0), 500.0)

            temp_motor += (abs(torque) * 0.005 - (temp_motor - 25) * 0.01) * PERIODO

            # 6. Envia o status
            dados = MSG_INV.encode({
                "RPM": round(rpm),
                "TENSAO_DC": tensao_dc,
                "TEMP_MOTOR": round(temp_motor),
                "FALHA_INV": 0,
                "CORRENTE_DC": corrente,
            })
            bus.send(can.Message(arbitration_id=MSG_INV.frame_id, data=dados, is_extended_id=False))

            ciclos += 1
            if ciclos % 50 == 0:  # imprime a cada 0,5 s
                print(f"v={velocidade * 3.6:5.1f} km/h  rpm={rpm:6.0f}  "
                      f"Vdc={tensao_dc:5.1f} V  I={corrente:6.1f} A  T={torque:5.1f} Nm")

            proximo += PERIODO
            time.sleep(max(0.0, proximo - time.monotonic()))
    except KeyboardInterrupt:
        pass
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
