# Generated by Django 4.2.13 on 2024-08-14 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0021_auction_refund_requested'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='refund_deadline',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
