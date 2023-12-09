# Generated by Django 4.1.2 on 2023-12-08 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('img_path', models.CharField(blank=True, max_length=255, null=True)),
                ('encoded_img', models.BinaryField(blank=True, null=True)),
            ],
            options={
                'db_table': 'employee',
            },
        ),
    ]
