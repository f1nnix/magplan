# Generated by Django 3.1.2 on 2020-11-21 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('magplan', '0002_auto_20201115_1140'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Widget',
        ),
        migrations.DeleteModel(
            name='Widgetype',
        ),
        migrations.RemoveField(
            model_name='post',
            name='postype',
        ),
        migrations.DeleteModel(
            name='Postype',
        ),
    ]
