# Generated by Django 3.1.6 on 2021-05-23 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('magplan', '0008_auto_20210318_0108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Image'), (1, 'PDF'), (2, 'File'), (3, 'Featured image')], default=0),
        ),
    ]