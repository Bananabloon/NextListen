# Generated by Django 5.2.1 on 2025-05-22 20:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0007_alter_user_last_updated"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="preferencevector",
            name="genre",
        ),
        migrations.AlterField(
            model_name="media",
            name="genre",
            field=models.JSONField(default=list),
        ),
        migrations.RemoveField(
            model_name="preferencevector",
            name="user",
        ),
        migrations.DeleteModel(
            name="Artist",
        ),
        migrations.DeleteModel(
            name="Genre",
        ),
        migrations.DeleteModel(
            name="PreferenceVector",
        ),
    ]
