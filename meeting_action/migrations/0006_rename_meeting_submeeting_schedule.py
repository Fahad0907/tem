# Generated by Django 4.2.8 on 2024-01-03 12:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meeting_action', '0005_submeeting'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submeeting',
            old_name='meeting',
            new_name='schedule',
        ),
    ]
