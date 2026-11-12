import pytest

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.db import models
from django.core.exceptions import ValidationError

from contractor.fields import JSONField, JSONMapField, StringListField, IpAddressField, JSON_MAGIC


@pytest.mark.django_db
def test_jsonfield_blank_null():
  class testModel( models.Model ):
    f = JSONField( default=None, null=True, blank=True )

    class Meta:
      app_label = 'test_jsonfield_blank_null'

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()
  m.full_clean()

  m.f = None
  m.full_clean()

  m.f = ''
  m.full_clean()

  m.f = 0
  m.full_clean()

  m.f = []
  m.full_clean()

  m.f = {}
  m.full_clean()

  m.f = None
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, None ) ]

  m.f = None
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, None ) ]

  m.f = ''
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03""' ) ]

  m.f = 'sally'
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03"sally"' ) ]

  m.f = 0
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x030' ) ]

  m.f = 221341
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03221341' ) ]

  m.f = []
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03[]' ) ]

  m.f = [ 1, 2 ]
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03[1, 2]' ) ]

  m.f = {}
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03{}' ) ]

  m.f = { 'a': 123 }
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03{"a": 123}' ) ]

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )
  assert testModel.objects.get().f is None

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ 'qwerty' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ 123 ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03""' ] )
  assert testModel.objects.get().f == ''

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03"qwerty"' ] )
  assert testModel.objects.get().f == 'qwerty'

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x030' ] )
  assert testModel.objects.get().f == 0

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03223311' ] )
  assert testModel.objects.get().f == 223311

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03[]' ] )
  assert testModel.objects.get().f == []

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03["asdf"]' ] )
  assert testModel.objects.get().f == [ "asdf" ]

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03{}' ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03"{}"' ] )
  assert testModel.objects.get().f == '{}'

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03{"a": 23}' ] )
  assert testModel.objects.get().f == { 'a': 23 }


@pytest.mark.django_db
def test_jsonfield():
  class testModel( models.Model ):
    f = JSONField()

    class Meta:
      app_label = 'test_jsonfield'

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()
  m.full_clean()

  m.f = None
  with pytest.raises( ValidationError ):
   m.full_clean()

  m.f = ''
  m.full_clean()

  m.f = 0
  m.full_clean()

  m.f = []
  m.full_clean()

  m.f = {}
  m.full_clean()

  m.f = ''
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03""' ) ]

  m.f = 'sally'
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03"sally"' ) ]

  m.f = 0
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x030' ) ]

  m.f = 221341
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03221341' ) ]

  m.f = []
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03[]' ) ]

  m.f = [ 1, 2 ]
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03[1, 2]' ) ]

  m.f = {}
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03{}' ) ]

  m.f = { 'a': 123 }
  m.full_clean()
  m.save()

  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '\x02JSON\x03{"a": 123}' ) ]

  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      with connection.cursor() as cursor:
        cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ 'qwerty' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ 123 ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03""' ] )
  assert testModel.objects.get().f == ''

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03"qwerty"' ] )
  assert testModel.objects.get().f == 'qwerty'

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x030' ] )
  assert testModel.objects.get().f == 0

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03223311' ] )
  assert testModel.objects.get().f == 223311

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03[]' ] )
  assert testModel.objects.get().f == []

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03["asdf"]' ] )
  assert testModel.objects.get().f == [ "asdf" ]

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03{}' ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03"{}"' ] )
  assert testModel.objects.get().f == '{}'

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '\x02JSON\x03{"a": 23}' ] )
  assert testModel.objects.get().f == { 'a': 23 }


def test_stringfield_init():
  with pytest.raises( ValueError ):
    StringListField()

  StringListField( max_length=50 )

  with pytest.raises( ValueError ):
    StringListField( max_length=50, default=None )

  with pytest.raises( ValueError ):
    StringListField( max_length=50, default=None, null=True )

  with pytest.raises( ValueError ):
    StringListField( max_length=50, default='bob' )

  StringListField( max_length=50, default=[ 'bob' ] )

  with pytest.raises( ValueError ):
    StringListField( max_length=50, default=0 )

  with pytest.raises( ValueError ):
    StringListField( max_length=50, default={} )

  StringListField( max_length=50, default=lambda: [ '1.2.3.4' ] )


def test_ipaddressfield_init():
  IpAddressField()

  with pytest.raises( ValueError ):
    IpAddressField( default=None )

  IpAddressField( default=None, null=True )

  with pytest.raises( ValueError ):
    IpAddressField( default='bob' )

  with pytest.raises( ValueError ):
    IpAddressField( default=[ 'bob' ] )

  with pytest.raises( ValueError ):
    IpAddressField( default=0 )

  with pytest.raises( ValueError ):
    IpAddressField( default={} )

  with pytest.raises( ValueError ):
    IpAddressField( default='0' )

  IpAddressField( default='127.0.0.1' )

  IpAddressField( default='0.0.0.0' )

  IpAddressField( default=lambda: '1.2.3.4' )


def test_jsonmapfield_init():
  JSONMapField()

  with pytest.raises( ValueError ):
    JSONMapField( default=None )

  JSONMapField( default=None, null=True )

  with pytest.raises( ValueError ):
    JSONMapField( default='bob' )

  with pytest.raises( ValueError ):
    JSONMapField( default=[ 'bob' ] )

  JSONMapField( default={} )
  JSONMapField( default={ 'a': 'sdf' } )
  JSONMapField( default=lambda: {} )


def test_jsonmapfield_dict_only():
  f = JSONMapField()

  assert f.get_prep_value( { 'a': 1 } ) == JSON_MAGIC + '{"a": 1}'
  assert f.get_prep_value( None ) is None

  # MapField's dict-only contract is kept
  for bad in ( [ 1, 2 ], 'a string', 7, True ):
    with pytest.raises( ValidationError ):
      f.get_prep_value( bad )

    with pytest.raises( ValidationError ):
      f.to_python( bad )

  assert f.to_python( { 'a': 1 } ) == { 'a': 1 }
  assert f.to_python( JSON_MAGIC + '{"a": 1}' ) == { 'a': 1 }  # ie. a fixture-loaded value


def test_jsonmapfield_from_db_value():
  f = JSONMapField()

  assert f.from_db_value( None, None, None ) is None
  assert f.from_db_value( JSON_MAGIC + '{"a": 1}', None, None ) == { 'a': 1 }

  with pytest.raises( ValidationError ):
    f.from_db_value( '{"a": 1}', None, None )

  with pytest.raises( ValidationError ):
    f.from_db_value( JSON_MAGIC + 'not json', None, None )

  # valid JSON that is not a dict is still not acceptable
  with pytest.raises( ValidationError ):
    f.from_db_value( JSON_MAGIC + '[ 1, 2 ]', None, None )
