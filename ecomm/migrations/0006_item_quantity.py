# Generated by Django 3.0.6 on 2020-06-03 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomm', '0005_item_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
