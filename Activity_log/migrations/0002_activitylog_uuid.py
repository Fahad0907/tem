# Generated by Django 4.2.8 on 2024-02-29 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Activity_log', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitylog',
            name='uuid',
            field=models.TextField(blank=True, null=True),
        ),
    ]
