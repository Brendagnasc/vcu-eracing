from simuladores.barramento import abrir_barramento

ID_PEDAL = 0x100


def main():
    bus = abrir_barramento()
    try:
        for msg in bus:
            if msg.arbitration_id == ID_PEDAL:
                pedal = int.from_bytes(msg.data[0:2], "little") / 10
                print(f"Pedal: {pedal:5.1f} %")
    except KeyboardInterrupt:
        pass
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
