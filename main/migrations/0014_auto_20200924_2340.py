# Generated by Django 2.2 on 2020-09-24 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_post_css'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='css',
            field=models.TextField(blank=True, help_text='CSS, который будет применяться к превью статьи', null=True, verbose_name='CSS-стили для статьи'),
        ),
    ]