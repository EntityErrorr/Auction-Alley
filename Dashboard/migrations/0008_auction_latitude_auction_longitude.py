# Generated by Django 4.2.13 on 2024-07-27 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0007_alter_auction_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='auction',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
