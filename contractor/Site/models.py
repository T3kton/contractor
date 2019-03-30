from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, name_regex, config_name_regex
from contractor.lib.config import getConfig
from contractor.Records.lib import post_save_callback, post_delete_callback
from contractor.Directory.models import Zone

# this is the what we want implemented, ie where, how it's grouped and waht is in thoes sites/groups, the logical aspect

cinp = CInP( 'Site', '0.1' )


class SiteException( ValueError ):
  def __init__( self, code, message ):
    super().__init__( message )
    self.message = message
    self.code = code

  @property
  def response_data( self ):
    return { 'class': 'SiteException', 'error': self.code, 'message': self.message }

  def __str__( self ):
    return 'SiteException ({0}): {1}'.format( self.code, self.message )


@cinp.model()
class Site( models.Model ):
  name = models.CharField( max_length=40, primary_key=True )  # update Architect if this changes max_length
  zone = models.ForeignKey( Zone, null=True, blank=True )
  description = models.CharField( max_length=200 )
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.CASCADE )
  config_values = MapField( blank=True, null=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  @cinp.action( 'Map' )
  def getDependencyMap( self ):
    from contractor.Building.models import Dependency
    result = {}
    external_list = []
    structure_job_list = [ i.structurejob.structure.pk for i in self.basejob_set.filter( structurejob__isnull=False ) ]
    foundation_job_list = [ i.foundationjob.foundation.pk for i in self.basejob_set.filter( foundationjob__isnull=False ) ]
    dependency_job_list = [ i.dependencyjob.dependency.pk for i in self.basejob_set.filter( dependencyjob__isnull=False ) ]

    for structure in self.networked_set.filter( structure__isnull=False ).order_by( 'pk' ):
      structure = structure.structure
      dependency_list = [ structure.foundation.dependencyId ]
      if structure.foundation.site != self:
        external_list.append( structure.foundation )

      result[ structure.dependencyId ] = { 'description': structure.description, 'type': 'Structure', 'state': structure.state, 'dependency_list': dependency_list, 'has_job': ( structure.pk in structure_job_list ), 'external': False }

    for foundation in self.foundation_set.all().order_by( 'pk' ):
      foundation = foundation.subclass
      # dependency_list = list( set( [ i.dependencyId for i in foundation.dependency_set.all() ] ) )
      dependency_list = []
      try:
        dependency_list.append( foundation.dependency.dependencyId )
      except Dependency.DoesNotExist:
        pass
      try:
        dependency_list += [ foundation.complex.dependencyId ]
        if foundation.complex.site != self:
          external_list += [ foundation.complex  ]
      except AttributeError:
        pass

      result[ foundation.dependencyId ] = { 'description': foundation.description, 'type': 'Foundation', 'state': foundation.state, 'dependency_list': dependency_list, 'has_job': ( foundation.pk in foundation_job_list ), 'external': False }

    for dependency in Dependency.objects.filter( Q( foundation__site=self ) |
                                                 Q( foundation__isnull=True, script_structure__site=self ) |
                                                 Q( foundation__isnull=True, script_structure__isnull=True, dependency__structure__site=self ) |
                                                 Q( foundation__isnull=True, script_structure__isnull=True, structure__site=self )
                                                 ).order_by( 'pk' ):

      if dependency.dependency is not None:
        dependency_list = [ dependency.dependency.dependencyId ]
      else:
        dependency_list = [ dependency.structure.dependencyId ]
      if dependency.site != self:
        external_list += [ dependency.structure ]

      result[ dependency.dependencyId ] = { 'description': dependency.description, 'type': 'Dependency', 'state': dependency.state, 'dependency_list': dependency_list, 'has_job': ( dependency.pk in dependency_job_list ), 'external': False }

    for complex in self.complex_set.all().order_by( 'pk' ):
      complex = complex.subclass
      dependency_list = [ i.structure.dependencyId for i in complex.complexstructure_set.all() ]
      external_list += [ i.structure if i.structure.site != self else None for i in complex.complexstructure_set.all() ]

      result[ complex.dependencyId ] = { 'description': complex.description, 'type': 'Complex', 'state': complex.state, 'dependency_list': dependency_list, 'external': False }

    external_list = list( set( external_list ) )

    for external in external_list:
      if external is None:
        continue

      result[ external.dependencyId ] = { 'description': external.description, 'type': external.type, 'state': external.state, 'dependency_list': [], 'external': True }

    return result

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.name and not name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid'

    if self.config_values is not None:
      for name in self.config_values:
        if not config_name_regex.match( name ):
          errors[ 'config_values' ] = 'config item name "{0}" is invalid'.format( name )
          break

        if name in ( 'domain_search', 'dns_servers', 'log_servers' ):
          if not isinstance( self.config_values[ name ], list ):
            errors[ 'config_values' ] = 'config item "{0}" must be a list'.format( name )
          break

    if errors:
      raise ValidationError( errors )

  def __str__( self ):
    return 'Site "{0}"({1})'.format( self.description, self.name )

post_save.connect( post_save_callback, sender=Site )
post_delete.connect( post_delete_callback, sender=Site )
