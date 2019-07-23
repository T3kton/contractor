import os

os.environ.setdefault( 'DJANGO_SETTINGS_MODULE', 'contractor.settings' )

from cinp.django_file_handler import FILE_STORAGE

if not os.path.isdir( FILE_STORAGE ):
  os.makedirs( FILE_STORAGE )

import django
django.setup()

from django.conf import settings
from contractor.app import get_app

application = get_app( settings.DEBUG )
