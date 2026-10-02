"""
pre_nro acepta entero o texto y conserva el tipo tal como llega
(spec presupuestos/identificador-presupuesto).
"""
import pytest
from pydantic import ValidationError

from app.schemas.presupuesto import PresupuestoAprobar
from app.schemas.presupuesto_detalle import DetallePresupuesto


@pytest.mark.parametrize("valor", [12345, "06798-2026-0", "00123", "12345"])
def test_conserva_tipo_y_valor(valor):
    dumped = PresupuestoAprobar(Loc_cod=1, pre_nro=valor).model_dump(mode="json")
    assert dumped["pre_nro"] == valor
    assert type(dumped["pre_nro"]) is type(valor)


def test_entero_se_serializa_como_numero_json():
    assert DetallePresupuesto(loc_cod=1, pre_nro=6798).model_dump_json().startswith('{"loc_cod":1,"pre_nro":6798,')


def test_texto_se_serializa_como_string_json():
    assert '"pre_nro":"06798-2026-0"' in DetallePresupuesto(loc_cod=1, pre_nro="06798-2026-0").model_dump_json()


@pytest.mark.parametrize("valor", ["1' OR 1=1", "x" * 21, "", "06798 2026"])
def test_rechaza_texto_invalido(valor):
    with pytest.raises(ValidationError):
        PresupuestoAprobar(Loc_cod=1, pre_nro=valor)


def test_openapi_expone_integer_o_string():
    from app.main import app

    esquema = app.openapi()["components"]["schemas"]["PresupuestoAprobar"]["properties"]["pre_nro"]
    assert {t["type"] for t in esquema["anyOf"]} == {"integer", "string"}
