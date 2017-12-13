import json
from urllib import request

from django.utils import timezone

from contractor.Building.models import Foundation, Structure
from contractor.PostOffice.models import FoundationPost, StructurePost, FoundationBox, StructureBox

WEBHOOK_REQUEST_TIMEOUT = 60


def registerEvent( target, job ):
  if isinstance( target, Foundation ):
    post = FoundationPost( foundation=target )

  elif isinstance( target, Structure ):
    post = StructurePost( structure=target )

  else:
    raise ValueError( 'Target must be a Foundation(or subclass) or Structure' )

  post.name = job.script_name
  post.full_clean()
  post.save()


def _sendPost( data, box ):
  print( 'Sending "{0}" to "{1}"'.format( data, box.url ) )
  if box.proxy is not None:
    opener = request.build_opener( request.ProxyHandler( { 'http': box.proxy, 'https': box.proxy } ) )
  else:
    opener = request.build_opener( request.ProxyHandler( {} ) )

  headers = { 'User-Agent': 'Contractor WebHook', 'Content-Type': 'application/json;charset=utf-8' }

  data = json.dumps( data ).encode( 'utf-8' )
  req = request.Request( box.url, data=data, headers=headers )
  if box.type == 'post':
    req.get_method = lambda: 'POST'

  elif box.type == 'call':
    req.headers[ 'CInP-Version' ] = '0.9'
    req.get_method = lambda: 'CALL'

  else:
    raise ValueError( 'Unknown box type "{0}"'.format( box.type ) )

  try:
    resp = opener.open( req, timeout=WEBHOOK_REQUEST_TIMEOUT )  # Do we care about the return value, ie: allow a re-queue of a one shot or something?
  except Exception as e:
    print( e )
    raise e

  print( 'got "{0}"'.format( resp.code ) )


def _sendFoundationPost( post, box ):
  data = box.extra_data
  data[ 'foundation' ] = post.foundation.pk
  data[ 'script' ] = post.name
  data[ 'at' ] = post.created.isoformat()
  _sendPost( data, box )


def _sendStructurePost( post, box ):
  data = box.extra_data
  data[ 'structure' ] = post.structure.pk
  data[ 'script' ] = post.name
  data[ 'at' ] = post.created.isoformat()
  _sendPost( data, box )


def processPost():
  # first clcean up the expired
  for box in FoundationBox.objects.filter( expires__lt=timezone.now(), expires__isnull=False ):
    box.delete()  # send a expiration notification? ormabey a 4, 2, 1 hour warning so they can renew

  for box in StructureBox.objects.filter( expires__lt=timezone.now(), expires__isnull=False ):
    box.delete()

  # now look over the Posts and see if there is anything that needs to be delievered
  for post in FoundationPost.objects.all():
    for box in FoundationBox.objects.filter( foundation=post.foundation ):
      _sendFoundationPost( post, box )
      if box.one_shot:
        box.delete()

    post.delete()

  for post in StructurePost.objects.all():
    for box in StructureBox.objects.filter( structure=post.structure ):
      _sendStructurePost( post, box )
      if box.one_shot:
        box.delete()

    post.delete()
