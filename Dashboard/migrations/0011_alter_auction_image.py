# Generated by Django 5.0.6 on 2024-07-29 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0010_auction_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='image',
            field=models.ImageField(upload_to='images/auction_item_images/'),
        ),
    ]
