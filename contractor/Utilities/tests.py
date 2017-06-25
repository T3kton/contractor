import pytest

from django.core.exceptions import ValidationError, ObjectDoesNotExist

from contractor.lib.ip import StrToIp
from contractor.Utilities.models import AddressBlock
from contractor.Site.models import Site


@pytest.mark.django_db
def test_addressblock():
  s1 = Site( name='tsite1', description='test site1' )
  s1.full_clean()
  s1.save()

  ab = AddressBlock()
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ) )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ), prefix=24 )
  ab.full_clean()
  ab.save()

  ab = AddressBlock( site=s1, subnet=StrToIp( '0.0.0.0' ), prefix=24 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=24 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=-1 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=33 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '255.0.0.0' ), prefix=1 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=32 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=24, gateway_offset=1 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=32, gateway_offset=0 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=32, gateway_offset=1 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=32, gateway_offset=2 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, gateway_offset=0 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, gateway_offset=1 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=31, gateway_offset=2 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=30, gateway_offset=0 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=30, gateway_offset=1 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=30, gateway_offset=2 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=30, gateway_offset=3 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=29, gateway_offset=0 )
  with pytest.raises( ValidationError ):
    ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=29, gateway_offset=1 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=29, gateway_offset=2 )
  ab.full_clean()

  ab = AddressBlock( site=s1, subnet=StrToIp( '1.0.0.0' ), prefix=29, gateway_offset=3 )
  ab.full_clean()
