# Generated by Django 4.2 on 2023-05-04 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file_description',
            field=models.TextField(max_length=300, null=True, verbose_name='Description'),
        ),
    ]
