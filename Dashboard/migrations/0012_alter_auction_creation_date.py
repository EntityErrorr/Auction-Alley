# Generated by Django 5.0.6 on 2024-07-30 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0011_alter_auction_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='creation_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
