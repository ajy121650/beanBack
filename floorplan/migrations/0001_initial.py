
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cafe', '0002_cafe_keywords_cafe_owner_cafetagrating_cafe_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='FloorPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
                ('cafe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floor_plans', to='cafe.cafe')),
            ],
        ),
    ]
