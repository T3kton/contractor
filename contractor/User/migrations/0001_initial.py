# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def setPassword( user, password ):
  user.password = hashlib.sha256( password.encode( 'utf-8' ) ).hexdigest()
  user.save()

def load_users( app, schema_editor ):
  User = app.get_model( 'User', 'User' )
  u = User( username='bob', nick_name='Bobby Bob' )
  u.save()
  setPassword( u, 'bob' )

  u = User( username='admin', nick_name='Admin', superuser=True )
  u.save()
  setPassword( u, 'adm1n' )


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('token', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('last_hearbeat', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('username', models.CharField(max_length=40, serialize=False, primary_key=True)),
                ('password', models.CharField(max_length=64, editable=False)),
                ('nick_name', models.CharField(max_length=100, blank=True, null=True)),
                ('superuser', models.BooleanField(default=False, editable=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='session',
            name='user',
            field=models.ForeignKey(to='User.User'),
        ),
        migrations.RunPython( load_users ),
    ]
