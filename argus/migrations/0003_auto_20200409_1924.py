# Generated by Django 3.0.4 on 2020-04-09 19:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('argus', '0002_ip_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port_number', models.IntegerField(default=0)),
                ('protocol', models.CharField(choices=[('TCP', 'tcp'), ('UDP', 'udp'), ('UP', 'arp'), ('ICMP', 'icmp'), ('SCTP', 'sctp'), ('ERR', 'err')], default='TCP', max_length=4)),
                ('status', models.CharField(choices=[('UNKNOWN', 'unknown'), ('OPEN', 'open'), ('CLOSED', 'closed'), ('UP', 'up')], default='CLOSED', max_length=7)),
                ('reason', models.CharField(default='', max_length=8)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='argus.Host')),
            ],
        ),
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=30)),
                ('banner', models.TextField(default='')),
                ('port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='argus.Port')),
            ],
        ),
        migrations.DeleteModel(
            name='Ip',
        ),
        migrations.AddField(
            model_name='host',
            name='scan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='argus.Scan'),
        ),
    ]
