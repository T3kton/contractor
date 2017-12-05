from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from contractor.fields import MapField, name_regex, config_name_regex
from contractor.lib.config import getConfig
from contractor.Directory.models import Zone

# this is the what we want implemented, ie where, how it's grouped and waht is in thoes sites/groups, the logical aspect

cinp = CInP( 'Site', '0.1' )


@cinp.model()
class Site( models.Model ):
  name = models.CharField( max_length=40, primary_key=True )  # update Architect if this changes max_length
  zone = models.ForeignKey( Zone, null=True, blank=True )
  description = models.CharField( max_length=200 )
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.CASCADE )
  config_values = MapField( blank=True )
  updated = models.DateTimeField( editable=False, auto_now=True )
  created = models.DateTimeField( editable=False, auto_now_add=True )

  @cinp.action( 'Map' )
  def getConfig( self ):
    return getConfig( self )

  @cinp.action( 'Map' )
  def getDependancyMap( self ):
    result = {}
    external_list = []
    structure_job_list = [ i.structurejob.structure.pk for i in self.basejob_set.filter( structurejob__isnull=False ) ]
    foundation_job_list = [ i.foundationjob.foundation.pk for i in self.basejob_set.filter( foundationjob__isnull=False ) ]
    dependancy_job_list = [ i.dependancyjob.dependancy.pk for i in self.basejob_set.filter( dependancyjob__isnull=False ) ]

    for structure in self.networked_set.filter( structure__isnull=False ).order_by( 'pk' ):
      structure = structure.structure
      dependancy_list = [ structure.foundation.dependancyId ]
      if structure.foundation.site != self:
        external_list.append( structure.foundation )

      result[ structure.dependancyId ] = { 'description': structure.description, 'type': 'Structure', 'state': structure.state, 'dependancy_list': dependancy_list, 'has_job': ( structure.pk in structure_job_list ), 'external': False }

    for foundation in self.foundation_set.all().order_by( 'pk' ):
      foundation = foundation.subclass
      dependancy_list = list( set( [ i.dependancyId for i in foundation.dependancy_set.all() ] ) )
      try:
        dependancy_list += [ foundation.complex.dependancyId ]
        if foundation.complex.site != self:
          external_list += [ foundation.complex  ]
      except AttributeError:
        pass

      result[ foundation.dependancyId ] = { 'description': foundation.description, 'type': 'Foundation', 'state': foundation.state, 'dependancy_list': dependancy_list, 'has_job': ( foundation.pk in foundation_job_list ), 'external': False }

      for dependancy in foundation.dependancy_set.all().order_by( 'pk' ):  # Dependancy's "site" is the foundation's site, so it is never external
        dependancy_list = [ dependancy.structure.dependancyId ]
        if dependancy.structure.site != self:
          external_list += [ dependancy.structure ]

        result[ dependancy.dependancyId ] = { 'description': dependancy.description, 'type': 'Dependancy', 'state': dependancy.state, 'dependancy_list': dependancy_list, 'has_job': ( dependancy.pk in dependancy_job_list ), 'external': False }

    for complex in self.complex_set.all().order_by( 'pk' ):
      complex = complex.subclass
      dependancy_list = [ i.structure.dependancyId for i in complex.complexstructure_set.all() ]
      external_list += [ i.structure if i.structure.site != self else None for i in complex.complexstructure_set.all() ]

      result[ complex.dependancyId ] = { 'description': complex.description, 'type': 'Complex', 'state': complex.state, 'dependancy_list': dependancy_list, 'external': False }

    external_list = list( set( external_list ) )

    for external in external_list:
      if external is None:
        continue

      result[ external.dependancyId ] = { 'description': external.description, 'type': external.type, 'state': external.state, 'dependancy_list': [], 'external': True }

    return result

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not name_regex.match( self.name ):
      errors[ 'name' ] = 'name "{0}" is invalid'.format( self.name )

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
