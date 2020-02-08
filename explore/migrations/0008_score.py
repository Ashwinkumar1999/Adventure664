# Generated by Django 3.0.2 on 2020-02-08 14:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('explore', '0007_activity_creator_only'),
    ]

    operations = [
        migrations.CreateModel(
            name='Score',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('total', models.IntegerField(default=0)),
            ],
        ),
    ]
