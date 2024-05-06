# Generated by Django 3.2.4 on 2021-06-24 07:41

import django.contrib.sites.managers
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import magplan.models
import magplan.models.abc


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("magplan", "0009_auto_20210523_1641"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="idea",
            managers=[
                ("objects", django.db.models.manager.Manager()),
                (
                    "on_current_site",
                    django.contrib.sites.managers.CurrentSiteManager(),
                ),
            ],
        ),
        migrations.AlterModelManagers(
            name="issue",
            managers=[
                ("objects", django.db.models.manager.Manager()),
                (
                    "on_current_site",
                    django.contrib.sites.managers.CurrentSiteManager(),
                ),
            ],
        ),
        migrations.AddField(
            model_name="idea",
            name="site",
            field=models.ForeignKey(
                default=magplan.models.abc.current_site_id,
                on_delete=django.db.models.deletion.CASCADE,
                to="sites.site",
            ),
        ),
        migrations.AddField(
            model_name="issue",
            name="site",
            field=models.ForeignKey(
                default=magplan.models.abc.current_site_id,
                on_delete=django.db.models.deletion.CASCADE,
                to="sites.site",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="site",
            field=models.ForeignKey(
                default=magplan.models.abc.current_site_id,
                on_delete=django.db.models.deletion.CASCADE,
                to="sites.site",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="slug",
            field=models.SlugField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="Слаг для URL",
            ),
        ),
        migrations.AlterField(
            model_name="section",
            name="site",
            field=models.ForeignKey(
                default=magplan.models.abc.current_site_id,
                on_delete=django.db.models.deletion.CASCADE,
                to="sites.site",
            ),
        ),
        migrations.AlterField(
            model_name="stage",
            name="site",
            field=models.ForeignKey(
                default=magplan.models.abc.current_site_id,
                on_delete=django.db.models.deletion.CASCADE,
                to="sites.site",
            ),
        ),
    ]
