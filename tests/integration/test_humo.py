import pytest

pytestmark = pytest.mark.integration


def test_indicadores_responde_en_ambos_esquemas(api):
    r = api.get("/presupuestos/indicadores")
    assert r.status_code == 200, r.text
