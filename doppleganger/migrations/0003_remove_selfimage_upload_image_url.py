# Generated by Django 3.2.9 on 2021-11-24 23:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doppleganger', '0002_selfimage_upload_image_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='selfimage',
            name='upload_image_url',
        ),
    ]
