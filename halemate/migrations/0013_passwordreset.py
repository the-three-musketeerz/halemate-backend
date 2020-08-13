# Generated by Django 3.1 on 2020-08-13 12:07

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('halemate', '0012_auto_20200813_1712'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('OTP', models.CharField(max_length=6)),
                ('num_attempts', models.IntegerField(default=3)),
                ('expiry', models.DateTimeField(default=datetime.datetime(2020, 8, 13, 17, 47, 54, 541480))),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
