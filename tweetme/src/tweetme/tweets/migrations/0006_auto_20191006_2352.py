# Generated by Django 2.2.5 on 2019-10-06 18:52

from django.db import migrations, models
import tweets.models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0005_auto_20191006_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='content',
            field=models.CharField(max_length=140, validators=[tweets.models.validate_content]),
        ),
    ]
