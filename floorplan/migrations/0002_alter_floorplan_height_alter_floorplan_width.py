
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('floorplan', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floorplan',
            name='height',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='floorplan',
            name='width',
            field=models.FloatField(default=0),
        ),
    ]
