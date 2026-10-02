"""
El script de hojas de validación corre contra las BD productivas de los clientes:
debe ser estrictamente de solo lectura.
"""
import importlib.util
import re
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "datos_validacion.py"
_spec = importlib.util.spec_from_file_location("datos_validacion", _SCRIPT)
datos_validacion = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(datos_validacion)

_ESCRITURA = re.compile(r"\b(INSERT|UPDATE|DELETE|ALTER|DROP|TRUNCATE|REPLACE|CREATE|GRANT)\b", re.I)


@pytest.mark.parametrize("sql", datos_validacion.TODAS_LAS_CONSULTAS)
def test_consultas_son_solo_select(sql):
    assert sql.strip().upper().startswith("SELECT")
    assert not _ESCRITURA.search(sql)


def test_todas_las_consultas_del_modulo_estan_registradas():
    constantes = [v for k, v in vars(datos_validacion).items() if k.startswith("SQL_")]
    assert sorted(constantes) == sorted(datos_validacion.TODAS_LAS_CONSULTAS)


def test_guardia_rechaza_escrituras():
    with pytest.raises(RuntimeError):
        datos_validacion._solo_lectura("UPDATE cot013 SET pre_vbgg = 1")
