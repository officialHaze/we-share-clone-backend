# Generated by Django 4.2 on 2023-04-27 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShortURL',
            fields=[
                ('id', models.CharField(max_length=8, primary_key=True, serialize=False, verbose_name='URL Id')),
                ('long_url', models.TextField(verbose_name='Long URL')),
                ('visited', models.IntegerField(default=0, verbose_name='Visitors')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created on')),
            ],
        ),
    ]
