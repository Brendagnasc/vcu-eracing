import math
import time

import can

from simuladores.barramento import abrir_barramento
from simuladores.mensagens import DB

MSG_PEDAIS = DB.get_message_by_name("PEDAIS")


def main():
    bus = abrir_barramento()
    t0 = time.time()
    try:
        while True:
            t = time.time() - t0
            apps1 = (math.sin(t) + 1) / 2 * 100
            apps2 = apps1 * 0.98  # sensores reais nunca batem exatamente
            freio = 30.0 if apps1 < 5 else 0.0

            dados = MSG_PEDAIS.encode({
                "APPS1": apps1,
                "APPS2": apps2,
                "PRESSAO_FREIO": freio,
            })
            bus.send(can.Message(
                arbitration_id=MSG_PEDAIS.frame_id,
                data=dados,
                is_extended_id=False,
            ))
            time.sleep(0.01)  # 100 Hz
    except KeyboardInterrupt:
        pass
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
