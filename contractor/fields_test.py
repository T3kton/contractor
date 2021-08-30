import pickle
import pytest
import datetime

from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.db import models
from django.core.exceptions import ValidationError

from contractor.fields import MapField, JSONField, StringListField, IpAddressField


def _convert_recs( recs ):
  return [ ( id, ( None if value is None else pickle.loads( value.tobytes() ) ) ) for id, value in recs ]


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


def test_mapfield_cross_contamination():
  class testModel1( models.Model ):
    f = MapField()

    class Meta:
      app_label = 'test_mapfield_cross_contamination'

  class testModel2( models.Model ):
    f = MapField()

    class Meta:
      app_label = 'test_mapfield_cross_contamination'

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
  counter = 0
  for blank_default, default in ( ( True, None ), ( True, {} ), ( False, { 'stuff': 1 } ) ):
    for null in ( True, False ):
      for blank in ( True, False ):
        kwargs = { 'null': null, 'blank': blank  }
        if default is not None:
          kwargs[ 'default' ] = default

        counter += 1

        class testModel( models.Model ):
          f = MapField( **kwargs )

          class Meta:
            app_label = 'test_mapfield_validation_{0}'.format( counter )

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
def test_mapfield_save_load_empty_blank():
  class testModel( models.Model ):
    f = MapField( default=None, null=True, blank=True )

    class Meta:
      app_label = 'test_mapfield_save_load_empty_blank'

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()

  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, None ) ]

  m.f = None
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, None ) ]

  m.f = {}
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, {} ) ]

  m.f = { 'a': [ 1, 2, 3 ] }
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, { 'a': [ 1, 2, 3 ] } ) ]

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )
  assert testModel.objects.get().f is None

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( {}, protocol=4 ) ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( { 'a': [ 1, 2, 3 ] }, protocol=4 ) ] )
  assert testModel.objects.get().f == { 'a': [ 1, 2, 3 ] }

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 'bob', protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 0, protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 42, protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( '', protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( [], protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( [ 1, 2 ], protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()


@pytest.mark.django_db
def test_mapfield_save_load_empty_blank_nonnull():
  class testModel( models.Model ):
    f = MapField( blank=True )

    class Meta:
      app_label = 'test_mapfield_save_load_empty_blank_nonnull'

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()

  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, {} ) ]

  m.f = None
  m.full_clean()
  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, {} ) ]

  m.f = {}
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, {} ) ]

  m.f = { 'a': [ 1, 2, 3 ] }
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, { 'a': [ 1, 2, 3 ] } ) ]

  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      with connection.cursor() as cursor:
        cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( {}, protocol=4 ) ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( { 'a': [ 1, 2, 3 ] }, protocol=4 ) ] )
  assert testModel.objects.get().f == { 'a': [ 1, 2, 3 ] }

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 'bob', protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 0, protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 42, protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( '', protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( [], protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( [ 1, 2 ], protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()


@pytest.mark.django_db
def test_mapfield_save_default():
  class testModel( models.Model ):
    f = MapField( default={ 'b': 2 } )

    class Meta:
      app_label = 'test_mapfield_save_default'

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()

  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, { 'b': 2 }  ) ]

  m.f = { 'a': [ 1, 2, 3 ] }
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, { 'a': [ 1, 2, 3 ] } ) ]

  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      with connection.cursor() as cursor:
        cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( {}, protocol=4 ) ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( { 'a': [ 1, 2, 3 ] }, protocol=4 ) ] )
  assert testModel.objects.get().f == { 'a': [ 1, 2, 3 ] }

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 'bob', protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 0, protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 42, protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( '', protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( [], protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( [ 1, 2 ], protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()


@pytest.mark.django_db
def test_mapfield_save_default_blank():
  class testModel( models.Model ):
    f = MapField( default={ 'b': 2 }, blank=True )

    class Meta:
      app_label = 'test_mapfield_save_default_blank'

  with connection.schema_editor() as schema_editor:
    schema_editor.create_model( testModel )

  m = testModel()

  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, { 'b': 2 } ) ]

  m.f = None
  m.full_clean()
  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, { 'b': 2 } ) ]

  m.f = {}
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, {} ) ]

  m.f = { 'a': [ 1, 2, 3 ] }
  m.full_clean()
  m.save()
  with connection.cursor() as cursor:
    cursor.execute( 'SELECT * FROM "{0}" ORDER BY id'.format( testModel._meta.db_table ) )
    assert _convert_recs( cursor.fetchall() ) == [ ( 1, { 'a': [ 1, 2, 3 ] } ) ]

  with pytest.raises( IntegrityError ):
    with transaction.atomic():
      with connection.cursor() as cursor:
        cursor.execute( 'UPDATE "{0}" SET f = NULL WHERE id = ''1'''.format( testModel._meta.db_table ) )

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( {}, protocol=4 ) ] )
  assert testModel.objects.get().f == {}

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( { 'a': [ 1, 2, 3 ] }, protocol=4 ) ] )
  assert testModel.objects.get().f == { 'a': [ 1, 2, 3 ] }

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 'bob', protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 0, protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( 42, protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( '', protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( [], protocol=4 ) ]  )
  with pytest.raises( ValidationError ):
    testModel.objects.get()

  with connection.cursor() as cursor:
    cursor.execute( 'UPDATE "{0}" SET f = %s WHERE id = ''1'''.format( testModel._meta.db_table ), [ pickle.dumps( [ 1, 2 ], protocol=4 ) ] )
  with pytest.raises( ValidationError ):
    testModel.objects.get()


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
