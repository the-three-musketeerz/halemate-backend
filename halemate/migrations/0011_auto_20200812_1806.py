# Generated by Django 3.1 on 2020-08-12 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('halemate', '0010_auto_20200811_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(default='P', max_length=20),
        ),
    ]
