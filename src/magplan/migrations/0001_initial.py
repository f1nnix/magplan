# Generated by Django 3.1.2 on 2020-10-30 17:56

import datetime
import django.contrib.auth.models
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание')),
                ('approved', models.BooleanField(null=True)),
                ('author_type', models.CharField(choices=[('NO', 'Нет автора'), ('NW', 'Новый автор'), ('EX', 'Существующий автор(ы)')], default='NO', max_length=2, verbose_name='Автор')),
                ('authors_new', models.CharField(blank=True, max_length=255, null=True, verbose_name='Новые автор')),
            ],
            options={
                'permissions': (('edit_extended_idea_attrs', 'Edit extended Idea attributes'), ('recieve_idea_email_updates', 'Recieve email updates for Idea')),
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('number', models.SmallIntegerField(default=0)),
                ('title', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(null=True)),
                ('published_at', models.DateField(default=datetime.date.today)),
            ],
            options={
                'ordering': ['-number'],
            },
        ),
        migrations.CreateModel(
            name='Magazine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Postype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(null=True)),
                ('sort', models.SmallIntegerField(default=0)),
                ('color', models.CharField(default='000000', max_length=6)),
                ('is_archived', models.BooleanField(default=False)),
                ('is_whitelisted', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.user')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
            ],
            options={
                'permissions': (('manage_authors', 'Can manage authors'),),
            },
            bases=('auth.user', models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Widgetype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('score', models.SmallIntegerField(choices=[(0, 'Против таких статей в «Хакере»'), (25, 'Не верю, что выйдет хорошо'), (50, 'Тема нормальная, но не для меня'), (75, 'Почитал бы, встретив в журнале'), (100, 'Ради таких статей мог бы подписаться')], default=50)),
                ('idea', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='magplan.idea')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='magplan.user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('slug', models.SlugField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('sort', models.SmallIntegerField(default=0)),
                ('duration', models.SmallIntegerField(blank=True, default=1, null=True)),
                ('skip_notification', models.BooleanField(default=False)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='magplan.user')),
                ('next_stage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='p_stage', to='magplan.stage')),
                ('prev_stage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='n_stage', to='magplan.stage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('is_public', models.BooleanField(default=False)),
                ('f_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя')),
                ('m_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Отчество')),
                ('l_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия')),
                ('n_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ник')),
                ('country', models.SmallIntegerField(choices=[(0, 'Россия'), (1, 'Украина'), (2, 'Беларусь'), (3, 'Казахстан')], default=0, verbose_name='Страна')),
                ('city', models.CharField(blank=True, max_length=255, null=True, verbose_name='Город или поселок')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Примечания')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='magplan.user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('format', models.SmallIntegerField(choices=[(0, 'Default'), (1, 'Featured')], default=0)),
                ('finished_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дедлайн')),
                ('published_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата публикации')),
                ('kicker', models.CharField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(blank=True, max_length=255, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Заголовок статьи')),
                ('description', models.TextField(blank=True, verbose_name='Описание статьи')),
                ('views', models.IntegerField(default=0)),
                ('is_paywalled', models.BooleanField(default=False)),
                ('xmd', models.TextField(null=True)),
                ('html', models.TextField(null=True)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('is_locked', models.BooleanField(default=False)),
                ('css', models.TextField(blank=True, help_text='CSS, который будет применяться к превью статьи', null=True, verbose_name='CSS-стили для статьи')),
                ('authors', models.ManyToManyField(to='magplan.User', verbose_name='Авторы')),
                ('editor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edited', to='magplan.user', verbose_name='Редактор')),
                ('issues', models.ManyToManyField(related_name='posts', to='magplan.Issue', verbose_name='Выпуски')),
                ('last_updater', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts_updated', to='magplan.user', verbose_name='Кто последний обновлял')),
                ('postype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='magplan.postype')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='magplan.section', verbose_name='Раздел')),
                ('stage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='magplan.stage', verbose_name='Этап')),
            ],
            options={
                'permissions': (('recieve_post_email_updates', 'Recieve email updates for Post'), ('edit_extended_post_attrs', 'Edit extended Post attributes')),
            },
        ),
        migrations.AddField(
            model_name='issue',
            name='magazine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='magplan.magazine'),
        ),
        migrations.AddField(
            model_name='idea',
            name='authors',
            field=models.ManyToManyField(blank=True, related_name='authors', to='magplan.User', verbose_name='Авторы'),
        ),
        migrations.AddField(
            model_name='idea',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editor', to='magplan.user'),
        ),
        migrations.AddField(
            model_name='idea',
            name='post',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='magplan.post'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('text', models.TextField(blank=True)),
                ('type', models.SmallIntegerField(choices=[(5, 'system'), (10, 'private'), (15, 'public')], default=10)),
                ('object_id', models.PositiveIntegerField()),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='magplan.user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('_old_id', models.PositiveIntegerField(blank=True, null=True)),
                ('type', models.SmallIntegerField(choices=[(0, 'Image'), (1, 'PDF'), (2, 'File')], default=0)),
                ('original_filename', models.CharField(max_length=255)),
                ('file', models.FileField(max_length=2048, upload_to='attachments/%Y/%m/%d/')),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='magplan.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='magplan.user')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
