# VCU e-Racing

VCU (Vehicle Control Unit) e comunicação CAN para o carro elétrico da UFOP e-Racing, desenvolvida com simuladores.

## Estrutura

```
docs/          documentação (arquitetura, mensagens CAN)
dbc/           definição das mensagens do barramento
scripts/       utilitários de ambiente
simuladores/   nós simulados em Python (pedais, BMS, inversor, monitor)
vcu/           firmware da VCU em C
  app/         lógica: estados, plausibilidade, torque
  hal/         interfaces de hardware
  port/linux/  HAL implementada com SocketCAN
  port/stm32/  HAL implementada no microcontrolador
```

As pastas são criadas conforme cada parte do projeto avança.

## Como rodar

```bash
./scripts/setup_vcan.sh
source .venv/bin/activate
pip install -r simuladores/requirements.txt
python -m simuladores.pedal     # terminal 1
python -m simuladores.monitor   # terminal 2
```
