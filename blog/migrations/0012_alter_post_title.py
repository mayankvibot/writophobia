# Generated by Django 4.1.5 on 2023-03-06 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_category_thumbnail_200_category_thumbnail_500_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=512),
        ),
    ]
