from django.db import models
#from django.core.exceptions import ValidationError

class AddressBlock( models.Model ):
  subnet = models.GenericIPAddressField( protocol='both', blank=True, null=True )
  prefix = models.IntegerField()
  gateway = models.GenericIPAddressField( protocol='both', blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

class Address( models.Model ):
  block = models.ForeignKey( AddressBlock )
  offset = models.IntegerField()
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

class ReservedAddress( ):
  block = models.ForeignKey( AddressBlock )
  offset = models.IntegerField()
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

class DynamicAddress( ):
  block = models.ForeignKey( AddressBlock )
  offset = models.IntegerField()
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )
