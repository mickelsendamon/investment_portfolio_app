# Generated by Django 2.2 on 2021-04-18 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock_app', '0002_auto_20210413_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockday',
            name='day_close',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=13, null=True),
        ),
        migrations.AlterField(
            model_name='stockday',
            name='day_high',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=13, null=True),
        ),
        migrations.AlterField(
            model_name='stockday',
            name='day_low',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=13, null=True),
        ),
        migrations.AlterField(
            model_name='stockday',
            name='day_open',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=13, null=True),
        ),
    ]
