# Generated by Django 3.0.4 on 2020-04-09 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('argus', '0004_scan_scan_range'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='host_scan_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scan',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]