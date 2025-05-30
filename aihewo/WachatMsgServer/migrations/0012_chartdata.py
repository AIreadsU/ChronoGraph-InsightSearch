# Generated by Django 5.1.1 on 2024-10-11 23:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WachatMsgServer', '0011_alter_wechatmessage_compress_content_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChartData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('chart_data_sender', models.CharField(blank=True, max_length=300, null=True)),
                ('chart_data_types', models.CharField(blank=True, max_length=300, null=True)),
                ('chart_data_weekday', models.CharField(blank=True, max_length=300, null=True)),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='WachatMsgServer.contact')),
            ],
        ),
    ]
