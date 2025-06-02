
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_remove_preferencevector_genre_alter_media_genre_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='explicit_content_filter_enabled',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]