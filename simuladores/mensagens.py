from pathlib import Path

import cantools

CAMINHO_DBC = Path(__file__).resolve().parent.parent / "dbc" / "carro.dbc"
DB = cantools.database.load_file(CAMINHO_DBC)
