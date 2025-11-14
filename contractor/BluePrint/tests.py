from contractor.BluePrint.lib import validateTemplate


def test_validate_template():
  id_map = { 'hardware': None, 'network': None, 'disks': None }
  validation_template = {}

  validateTemplate( id_map, validation_template )
