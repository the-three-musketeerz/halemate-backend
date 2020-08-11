# Generated by Django 3.1 on 2020-08-11 06:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('halemate', '0006_auto_20200810_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to=settings.AUTH_USER_MODEL),
        ),
    ]
