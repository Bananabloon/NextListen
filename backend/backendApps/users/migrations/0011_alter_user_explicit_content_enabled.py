# Generated by Django 5.2.1 on 2025-06-02 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_rename_explicit_content_filter_enabled_user_explicit_content_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='explicit_content_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
