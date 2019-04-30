# Generated by Django 2.1.2 on 2019-04-22 21:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20190116_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='last_updater',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts_updated', to=settings.AUTH_USER_MODEL, verbose_name='Кто последний обновлял'),
        ),
    ]