# Generated by Django 4.2.8 on 2023-12-20 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0004_rolewithmoduleactionmap'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermoduleprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'male'), ('female', 'female'), ('others', 'others')], max_length=10, null=True),
        ),
    ]
