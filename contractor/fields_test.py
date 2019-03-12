import pytest

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.db import models
from django.core.exceptions import ValidationError

from contractor.fields import MapField, JSONField, StringListField, IpAddressField


def test_mapfield_init():
  MapField()

  with pytest.raises( ValueError ):
    MapField( default=None )

  MapField( default=None, null=True )

  with pytest.raises( ValueError ):
    MapField( default='bob' )

  with pytest.raises( ValueError ):
    MapField( default=[ 'bob' ] )

  MapField( default={} )

  MapField( default={ 'a': 'sdf' } )

  MapField( default=lambda: {} )

  MapField( default=lambda: 'yeah it is bad, but can we really call the callable during __init__?' )


def test_mapfield_cross_contamination( mocker ):
  class testModel1( models.Model ):
    f = MapField()

  class testModel2( models.Model ):
    f = MapField()

  m1 = testModel1()
  m1.f = { 'a': 'sfd' }

  m12 = testModel1()
  assert m12.f == {}

  m2 = testModel2()
  assert m2.f == {}

  m1 = testModel1()
  m1.f[ 'a' ] = 'rtr'

  m12 = testModel1()
  assert m12.f == {}

  m2 = testModel2()
  assert m2.f == {}


def test_mapfield_validation():
  for blank_default, default in ( ( True, None ), ( True, {} ), ( False, { 'stuff': 1 } ) ):
    for null in ( True, False ):
      for blank in ( True, False ):
        kwargs = { 'null': null, 'blank': blank  }
        if default is not None:
          kwargs[ 'default' ] = default

        print( 'test paramaters: {0}'.format( kwargs ) )

        class testModel( models.Model ):
          f = MapField( **kwargs )

        m = testModel()

        if blank_default:
          if blank:
            m.full_clean()

          else:
            with pytest.raises( ValidationError ) as e:
              m.full_clean()

            if default is None or isinstance( default, dict ):
              assert e.value.message_dict == { 'f': [ 'This field cannot be blank.' ] }
            else:
              assert e.value.message_dict == { 'f': [ 'must be a dict.' ] }

        else:
            m.full_clean()

        m.f = None
        if not blank:
          with pytest.raises( ValidationError ) as e:
            m.full_clean()

          if null:
            assert e.value.message_dict == { 'f': [ 'This field cannot be blank.' ] }
          else:
            assert e.value.message_dict == { 'f': [ 'must be a dict.' ] }

        else:
          m.full_clean()

        m.f = 0
        with pytest.raises( ValidationError ) as e:
          m.full_clean()
        assert e.value.message_dict == { 'f': [ 'must be a dict.' ] }

        m.f = 42
        with pytest.raises( ValidationError ) as e:
          m.full_clean()
        assert e.value.message_dict == { 'f': [ 'must be a dict.' ] }

        m.f = ''
        with pytest.raises( ValidationError ) as e:
          m.full_clean()
        assert e.value.message_dict == { 'f': [ 'must be a dict.' ] }

        m.f = 'bob'
        with pytest.raises( ValidationError ) as e:
          m.full_clean()
        assert e.value.message_dict == { 'f': [ 'must be a dict.' ] }

        m.f = []
        with pytest.raises( ValidationError ) as e:
          m.full_clean()
        assert e.value.message_dict == { 'f': [ 'must be a dict.' ] }

        m.f = [ 'stuff' ]
        with pytest.raises( ValidationError ) as e:
          m.full_clean()
        assert e.value.message_dict == { 'f': [ 'must be a dict.' ] }

        m.f = {}
        if not blank:
          with pytest.raises( ValidationError ) as e:
            m.full_clean()
          assert e.value.message_dict == { 'f': [ 'This field cannot be blank.' ] }

        else:
          m.full_clean()

        m.f = { 'a': 'sally' }
        m.full_clean()

        testModel.objects.filter( f=None )
        testModel.objects.filter( f={} )
        with pytest.raises( ValidationError ):
          testModel.objects.filter( f='' )
        with pytest.raises( ValidationError ):
          testModel.objects.filter( f='bob' )
        with pytest.raises( ValidationError ):
          testModel.objects.filter( f=0 )
        with pytest.raises( ValidationError ):
          testModel.objects.filter( f=42 )
        with pytest.raises( ValidationError ):
          testModel.objects.filter( f=[] )
        with pytest.raises( ValidationError ):
          testModel.objects.filter( f=[ 1, 2 ] )
        testModel.objects.filter( f__isnull=True )
        testModel.objects.filter( f__isnull=False )


@pytest.mark.django_db
def test_mapfield_save_load_empty_blank( mocker ):
  class testModel( models.Model ):
    f = MapField( default=None, null=True, blank=True )

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()

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

  m.f = {}
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{}' ) ]

  m.f = { 'a': [ 1, 2, 3 ] }
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{"a": [1, 2, 3]}' ) ]

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )
  assert testModel.objects.get().f is None

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '{}' ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '{"a": [1, 2, 3]}' ] )
  assert testModel.objects.get().f == { 'a': [ 1, 2, 3 ] }

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ 'bob' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '0' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '42' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '[]' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '[ 1, 2 ]' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()


@pytest.mark.django_db
def test_mapfield_save_load_empty_blank_nonnull( mocker ):
  class testModel( models.Model ):
    f = MapField( blank=True )

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()

  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{}' ) ]

  m.f = None
  m.full_clean()
  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{}' ) ]

  m.f = {}
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{}' ) ]

  m.f = { 'a': [ 1, 2, 3 ] }
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{"a": [1, 2, 3]}' ) ]

  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      with connection.cursor() as cursor:
        cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '{}' ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '{"a": [1, 2, 3]}' ] )
  assert testModel.objects.get().f == { 'a': [ 1, 2, 3 ] }

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ 'bob' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '0' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '42' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '[]' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '[ 1, 2 ]' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()


@pytest.mark.django_db
def test_mapfield_save_default( mocker ):
  class testModel( models.Model ):
    f = MapField( default={ 'b': 2 } )

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()

  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{"b": 2}' ) ]

  m.f = { 'a': [ 1, 2, 3 ] }
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{"a": [1, 2, 3]}' ) ]

  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      with connection.cursor() as cursor:
        cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '{}' ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '{"a": [1, 2, 3]}' ] )
  assert testModel.objects.get().f == { 'a': [ 1, 2, 3 ] }

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ 'bob' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '0' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '42' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '[]' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '[ 1, 2 ]' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()


@pytest.mark.django_db
def test_mapfield_save_default_blank( mocker ):
  class testModel( models.Model ):
    f = MapField( default={ 'b': 2 }, blank=True )

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()

  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{"b": 2}' ) ]

  m.f = None
  m.full_clean()
  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{"b": 2}' ) ]

  m.f = {}
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{}' ) ]

  m.f = { 'a': [ 1, 2, 3 ] }
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert cursor.fetchall() == [ ( 1, '{"a": [1, 2, 3]}' ) ]

  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      with connection.cursor() as cursor:
        cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '{}' ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '{"a": [1, 2, 3]}' ] )
  assert testModel.objects.get().f == { 'a': [ 1, 2, 3 ] }

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ 'bob' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '0' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '42' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '[]' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ '[ 1, 2 ]' ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()


@pytest.mark.django_db
def test_jsonfield_blank_null():
  class testModel( models.Model ):
    f = JSONField( default=None, null=True, blank=True )

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
