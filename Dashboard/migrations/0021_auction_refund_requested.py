# Generated by Django 4.2.13 on 2024-08-08 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0020_auction_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='refund_requested',
            field=models.BooleanField(default=False),
        ),
    ]
