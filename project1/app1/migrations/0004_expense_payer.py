# Generated by Django 4.1.13 on 2024-05-08 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0003_expense_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='payer',
            field=models.CharField(default=100, max_length=50),
            preserve_default=False,
        ),
    ]
