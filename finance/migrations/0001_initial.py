# Generated by Django 2.1.2 on 2018-12-04 13:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('format', models.SmallIntegerField(choices=[(0, 'Бюджетное'), (1, 'Внебюджетное'), (2, 'Рекламное')], default=0, verbose_name='Тип начисления')),
                ('sum', models.IntegerField(default=6000, verbose_name='Сумма')),
                ('notified_at', models.DateTimeField(blank=True, null=True, verbose_name='Уведомлен?')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='За что')),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
                ('fee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='editable', to='finance.Fee')),
            ],
            options={
                'verbose_name': 'Начисление',
                'verbose_name_plural': 'Начисления',
            },
        ),
        migrations.CreateModel(
            name='Notation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('sort', models.SmallIntegerField(default=0, verbose_name='Сортировка')),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Нотация',
                'verbose_name_plural': 'Нотации',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('format', models.SmallIntegerField(choices=[(0, 'Наличными'), (1, 'Банковский счет'), (2, 'Перевод через платежную систему')], default=0, verbose_name='Тип начисления')),
                ('sum', models.IntegerField(default=10000, verbose_name='Сумма')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Комментарий к выплате')),
                ('notified_at', models.DateTimeField(blank=True, null=True, verbose_name='Уведомлен?')),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Выплата',
                'verbose_name_plural': 'Выплаты',
            },
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('month', models.SmallIntegerField(choices=[(1, 'Январь'), (2, 'Февраль'), (3, 'Март'), (4, 'Апрель'), (5, 'Май'), (6, 'Июнь'), (7, 'Июль'), (8, 'Август'), (9, 'Сентябрь'), (0, 'Октябрь'), (11, 'Ноябрь'), (12, 'Декабрь')], default=12, verbose_name='Месяц')),
                ('year', models.SmallIntegerField(default=2018, verbose_name='Год')),
                ('is_finished', models.BooleanField(default=False, verbose_name='Закрыт?')),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Период',
                'verbose_name_plural': 'Периоды',
                'ordering': ['-year', '-month'],
            },
        ),
        migrations.AddField(
            model_name='fee',
            name='notation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Notation'),
        ),
        migrations.AddField(
            model_name='fee',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='finance.Period'),
        ),
        migrations.AddField(
            model_name='fee',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
