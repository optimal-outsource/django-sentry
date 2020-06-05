# -*- coding: utf-8 -*-


from django.db import models, migrations
import sentry.models
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FilterValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=32, choices=[(b'server_name', 'server name'), (b'logger', 'logger'), (b'site', 'site')])),
                ('value', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupedMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logger', models.CharField(default=b'root', max_length=64, db_index=True, blank=True)),
                ('class_name', models.CharField(db_index=True, max_length=128, null=True, verbose_name='type', blank=True)),
                ('level', models.PositiveIntegerField(default=40, blank=True, db_index=True, choices=[(10, 'debug'), (20, 'info'), (30, 'warning'), (40, 'error'), (50, 'fatal')])),
                ('message', models.TextField()),
                ('traceback', models.TextField(null=True, blank=True)),
                ('view', models.CharField(max_length=200, null=True, blank=True)),
                ('checksum', models.CharField(max_length=32, db_index=True)),
                ('data', sentry.models.GzippedDictField(null=True, blank=True)),
                ('status', models.PositiveIntegerField(default=0, db_index=True, choices=[(0, 'unresolved'), (1, 'resolved')])),
                ('times_seen', models.PositiveIntegerField(default=1, db_index=True)),
                ('last_seen', models.DateTimeField(default=datetime.datetime.now, db_index=True)),
                ('first_seen', models.DateTimeField(default=datetime.datetime.now, db_index=True)),
                ('score', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'sentry_groupedmessage',
                'verbose_name': 'grouped message',
                'verbose_name_plural': 'grouped messages',
                'permissions': (('can_view', 'Can view'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logger', models.CharField(default=b'root', max_length=64, db_index=True, blank=True)),
                ('class_name', models.CharField(db_index=True, max_length=128, null=True, verbose_name='type', blank=True)),
                ('level', models.PositiveIntegerField(default=40, blank=True, db_index=True, choices=[(10, 'debug'), (20, 'info'), (30, 'warning'), (40, 'error'), (50, 'fatal')])),
                ('message', models.TextField()),
                ('traceback', models.TextField(null=True, blank=True)),
                ('view', models.CharField(max_length=200, null=True, blank=True)),
                ('checksum', models.CharField(max_length=32, db_index=True)),
                ('data', sentry.models.GzippedDictField(null=True, blank=True)),
                ('message_id', models.CharField(max_length=32, unique=True, null=True)),
                ('datetime', models.DateTimeField(default=datetime.datetime.now, db_index=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('server_name', models.CharField(max_length=128, db_index=True)),
                ('site', models.CharField(max_length=128, null=True, db_index=True)),
                ('group', models.ForeignKey(related_name=b'message_set', blank=True, to='sentry.GroupedMessage', null=True)),
            ],
            options={
                'db_table': 'sentry_message',
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageCountByMinute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('times_seen', models.PositiveIntegerField(default=0)),
                ('group', models.ForeignKey(to='sentry.GroupedMessage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageFilterValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('times_seen', models.PositiveIntegerField(default=0)),
                ('key', models.CharField(max_length=32, choices=[(b'server_name', 'server name'), (b'logger', 'logger'), (b'site', 'site')])),
                ('value', models.CharField(max_length=200)),
                ('group', models.ForeignKey(to='sentry.GroupedMessage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageIndex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('column', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='messageindex',
            unique_together={('column', 'value', 'object_id')},
        ),
        migrations.AlterUniqueTogether(
            name='messagefiltervalue',
            unique_together={('key', 'value', 'group')},
        ),
        migrations.AlterUniqueTogether(
            name='messagecountbyminute',
            unique_together={('group', 'date')},
        ),
        migrations.AlterUniqueTogether(
            name='groupedmessage',
            unique_together={('logger', 'view', 'checksum')},
        ),
        migrations.AlterUniqueTogether(
            name='filtervalue',
            unique_together={('key', 'value')},
        ),
    ]
