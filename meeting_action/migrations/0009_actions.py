# Generated by Django 4.2.8 on 2024-01-23 10:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meeting_action', '0008_meetingscoremain_meetingscoreindicator'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('last_sync', models.TextField(blank=True, null=True)),
                ('uuid', models.CharField(blank=True, max_length=500, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('in_progress', 'in_progress'), ('not_started', 'not_started'), ('done', 'done'), ('wont_do', 'wont_do')], max_length=255, null=True)),
                ('date_from', models.DateField(blank=True, null=True)),
                ('date_to', models.DateField(blank=True, null=True)),
                ('supervisor', models.CharField(blank=True, max_length=255, null=True)),
                ('organization', models.CharField(blank=True, max_length=255, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_by_%(class)ss', to=settings.AUTH_USER_MODEL)),
                ('deleted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deleted_by_%(class)ss', to=settings.AUTH_USER_MODEL)),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting_action.indicator')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting_action.submeeting')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_by_%(class)ss', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
