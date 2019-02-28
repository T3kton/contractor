import pytest
from django.core.exceptions import ValidationError

from contractor.Site.models import Site


@pytest.mark.django_db
def test_site():
  s = Site()
  with pytest.raises( ValidationError ):
    s.full_clean()

  s = Site( name='test' )
  with pytest.raises( ValidationError ):
    s.full_clean()

  s = Site( name='test', description='test site' )
  s.full_clean()
  s.save()

  s = Site( name='test', description='test site' )
  s.config_values = None
  with pytest.raises( ValidationError ):
    s.full_clean()

  s = Site( name=' test' )
  with pytest.raises( ValidationError ):
    s.full_clean()

  s = Site( name='test', description='more testing' )
  with pytest.raises( ValidationError ):
    s.full_clean()

  s = Site( name='test2', description='more testing' )
  s.full_clean()
  s.config_values = { 'stuff': 'yep' }
  s.full_clean()
  s.save()

  s = Site( name='test3', description='blah blah' )
  s.full_clean()
  s.config_values = { ' stuff': 'yep' }
  with pytest.raises( ValidationError ):
    s.full_clean()
