from simuladores.barramento import abrir_barramento
from simuladores.mensagens import DB


def formatar(valor):
    return f"{valor:.1f}" if isinstance(valor, float) else str(valor)


def main():
    bus = abrir_barramento()
    try:
        for msg in bus:
            try:
                definicao = DB.get_message_by_frame_id(msg.arbitration_id)
            except KeyError:
                print(f"ID desconhecido: 0x{msg.arbitration_id:03X}")
                continue

            sinais = definicao.decode(msg.data)
            texto = "  ".join(f"{nome}={formatar(v)}" for nome, v in sinais.items())
            print(f"{definicao.name:<12} {texto}")
    except KeyboardInterrupt:
        pass
    finally:
        bus.shutdown()


if __name__ == "__main__":
    main()
