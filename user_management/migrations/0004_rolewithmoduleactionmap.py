# Generated by Django 4.2.8 on 2023-12-20 07:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0003_action_module_role_moduleactionmap'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleWithModuleActionMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('last_sync', models.TextField(blank=True, null=True)),
                ('permission', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_by_%(class)ss', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_by_%(class)ss', to=settings.AUTH_USER_MODEL)),
                ('module_role_map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.moduleactionmap')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_management.role')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_by_%(class)ss', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
