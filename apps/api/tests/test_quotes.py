from app.constants import MIN_MATERIAL_CHARS
from tests.fixtures import MATERIAL


def test_fixture_material_is_long_enough():
    assert len(MATERIAL) >= MIN_MATERIAL_CHARS
