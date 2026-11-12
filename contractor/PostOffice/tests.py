import pytest

from datetime import datetime, timezone, timedelta

from django.core.exceptions import ValidationError

from contractor.Site.models import Site
from contractor.BluePrint.models import FoundationBluePrint
from contractor.Building.models import Foundation
from contractor.PostOffice.models import FoundationBox


def _makeFoundation():
  si = Site( name='test', description='test' )
  si.full_clean()
  si.save()

  fb = FoundationBluePrint( name='fdnb1', description='Foundation BluePrint 1' )
  fb.foundation_type_list = [ 'Unknown' ]
  fb.full_clean()
  fb.save()

  f = Foundation( locator='test', site=si, blueprint=fb )
  f.full_clean()
  f.save()

  return f


@pytest.mark.django_db
def test_box_extend():
  f = _makeFoundation()

  box = FoundationBox( foundation=f, url='http://example.com', type='post', one_shot=True, extra_data={ 'a': 1 } )
  box.expires = datetime.now( timezone.utc ) + timedelta( hours=1 )
  box.full_clean()
  box.save()

  box.extend( 2 )
  assert box.expires > datetime.now( timezone.utc ) + timedelta( hours=2 )


@pytest.mark.django_db
def test_box_clean_requires_expires_when_not_one_shot():
  f = _makeFoundation()

  box = FoundationBox( foundation=f, url='http://example.com', type='post', one_shot=False, extra_data={ 'a': 1 } )
  with pytest.raises( ValidationError ) as execinfo:
    box.full_clean()
  assert 'expires' in execinfo.value.error_dict

  box.expires = datetime.now( timezone.utc ) + timedelta( hours=1 )
  box.full_clean()
  box.save()
