
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('floorplan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
                ('x_position', models.IntegerField(default=0)),
                ('y_position', models.IntegerField(default=0)),
                ('socket', models.BooleanField(default=False)),
                ('window', models.BooleanField(default=False)),
                ('occupied', models.BooleanField(default=False)),
                ('floor_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chairs', to='floorplan.floorplan')),
            ],
        ),
    ]
