
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chair', '0002_alter_chair_height_alter_chair_width_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chair',
            name='entry_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
