# Generated by Django 3.0.4 on 2020-03-31 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('argus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ip',
            name='address',
            field=models.TextField(default=''),
        ),
    ]
