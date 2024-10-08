# Generated by Django 5.0.6 on 2024-07-14 14:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone', models.CharField(max_length=11)),
                ('address', models.CharField(max_length=100)),
                ('ratings_sum', models.IntegerField(default=0)),
                ('ratings_count', models.IntegerField(default=0)),
                ('birth_date', models.DateField(blank=True, null=True)),
            ],
        ),
    ]
