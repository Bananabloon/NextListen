from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_user_explicit_content_filter_enabled'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='explicit_content_filter_enabled',
            new_name='explicit_content_enabled',
        ),
    ]