# Generated by Django 4.2.13 on 2024-07-31 20:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Dashboard', '0013_alter_auction_seller_delete_buyer_seller'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaperworkConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=32, unique=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('auction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Dashboard.auction')),
            ],
        ),
    ]
