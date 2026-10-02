import pytest

from app.services.presupuesto_service import PresupuestoService


@pytest.mark.parametrize("valor", [6798, 0, "6798", "00123", 2**63 - 1])
def test_numericos_validos(valor):
    assert PresupuestoService._es_numero_reppdf(valor)


@pytest.mark.parametrize("valor", ["06798-2026-0", "-1", -1, "", "9" * 20, 2**63, None, True, "１２", "6798 "])
def test_no_numericos(valor):
    assert not PresupuestoService._es_numero_reppdf(valor)


def test_batch_sin_numericos_no_abre_sesion_reppdf(monkeypatch):
    def _no_debe_llamarse():
        raise AssertionError("no debe consultar REPPDF")

    monkeypatch.setattr(PresupuestoService, "_get_reppdf_session", staticmethod(_no_debe_llamarse))
    items = [(1, "06798-2026-0"), (1, "00123-2026-0")]
    assert PresupuestoService._verificar_pdfs_batch(items, 6, 1) == {item: 0 for item in items}


def test_eliminar_no_numerico_no_abre_sesion_reppdf(monkeypatch):
    monkeypatch.setattr(
        PresupuestoService, "_get_reppdf_session", staticmethod(lambda: pytest.fail("no debe consultar REPPDF"))
    )
    PresupuestoService._eliminar_pdf_reppdf(1, "06798-2026-0", 6)
