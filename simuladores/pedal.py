import math
import time

import can

from simuladores.barramento import abrir_barramento

ID_PEDAL = 0x100


def main():
    bus = abrir_barramento()
    t0 = time.time()
    try:
        while True:
            t = time.time() - t0
            # 0 a 1000 representa 0,0% a 100,0%
            pedal = int((math.sin(t) + 1) / 2 * 1000)
            msg = can.Message(
                arbitration_id=ID_PEDAL,
                data=pedal.to_bytes(2, "little"),
                is_extended_id=False,
            )
            bus.send(msg)
            time.sleep(0.01)  # 100 Hz
    except KeyboardInterrupt:
        pass
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
