# Generated by Django 4.1.7 on 2023-04-10 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_cod_finca_user_nombre_finca'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cod_finca',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='nombre_finca',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
    ]
