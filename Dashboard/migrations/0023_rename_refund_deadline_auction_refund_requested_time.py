# Generated by Django 4.2.13 on 2024-08-15 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0022_auction_refund_deadline'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auction',
            old_name='refund_deadline',
            new_name='refund_requested_time',
        ),
    ]