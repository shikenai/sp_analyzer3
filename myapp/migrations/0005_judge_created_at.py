# Generated by Django 4.2 on 2023-05-07 03:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0004_judge"),
    ]

    operations = [
        migrations.AddField(
            model_name="judge",
            name="created_at",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2023, 5, 7, 3, 34, 38, 658141, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
