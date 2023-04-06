# Generated by Django 4.2 on 2023-04-06 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifyData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('refresh_token', models.CharField(max_length=100)),
                ('access_token', models.CharField(max_length=100)),
                ('expires_in', models.DateTimeField()),
                ('token_type', models.CharField(max_length=100)),
            ],
        ),
    ]
