# Generated by Django 3.0.2 on 2020-02-06 20:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('explore', '0004_activity_creator'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=512)),
                ('area_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming', to='explore.Area')),
                ('area_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing', to='explore.Area')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
