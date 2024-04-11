# Generated by Django 4.2.11 on 2024-04-08 10:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_favorite_recipe_alter_favorite_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(help_text='Цвет должен быть представлен в формате HEX (например, #ff0000).', max_length=7, unique=True, validators=[django.core.validators.RegexValidator(message='Код цвета не соответсвует формату HEX.', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='Цвет'),
        ),
    ]
