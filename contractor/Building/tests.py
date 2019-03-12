import pytest

from django.core.exceptions import ValidationError

from contractor.Building.models import Foundation, Structure, Dependency


def _loadBluePrints():
  pass


@pytest.mark.django_db
def test_foundation_create():
  _loadBluePrints()
  f = Foundation()

  with pytest.raises( ValidationError ):
    f.full_clean()

# def test_structure_create():
#   assert IpIsV4( 281470681743360 )
