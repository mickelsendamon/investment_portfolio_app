# Generated by Django 2.2 on 2021-04-14 04:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=5)),
                ('after_ticker', models.CharField(max_length=2)),
                ('price', models.DecimalField(decimal_places=6, max_digits=13)),
                ('description', models.TextField()),
                ('fifty_two_week_high', models.DecimalField(decimal_places=6, max_digits=13)),
                ('fifty_two_week_low', models.DecimalField(decimal_places=6, max_digits=13)),
                ('fifty_day_moving_average', models.DecimalField(decimal_places=6, max_digits=13)),
                ('two_hundred_day_moving_average', models.DecimalField(decimal_places=6, max_digits=13)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email_address', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('day_open', models.DecimalField(decimal_places=6, max_digits=13)),
                ('day_close', models.DecimalField(decimal_places=6, max_digits=13)),
                ('day_high', models.DecimalField(decimal_places=6, max_digits=13)),
                ('day_low', models.DecimalField(decimal_places=6, max_digits=13)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_days', to='stock_app.Stock')),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio', to='stock_app.User')),
            ],
        ),
        migrations.CreateModel(
            name='OwnedStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shares', models.IntegerField()),
                ('purchase_date_time', models.DateTimeField()),
                ('sell_date_time', models.DateTimeField(null=True)),
                ('purchase_price', models.DecimalField(decimal_places=6, max_digits=13)),
                ('sell_price', models.DecimalField(decimal_places=6, max_digits=13, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='stock_app.User')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_stocks', to='stock_app.Portfolio')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_stocks', to='stock_app.Stock')),
            ],
        ),
        migrations.CreateModel(
            name='OneMinuteSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('price', models.DecimalField(decimal_places=6, max_digits=13)),
                ('stock_day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_series_days', to='stock_app.StockDay')),
            ],
        ),
        migrations.CreateModel(
            name='Investment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('investment_amount', models.DecimalField(decimal_places=6, max_digits=13)),
                ('investment_date', models.DateTimeField()),
                ('bank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investments', to='stock_app.Bank')),
            ],
        ),
        migrations.AddField(
            model_name='bank',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='banks', to='stock_app.Portfolio'),
        ),
        migrations.AddField(
            model_name='bank',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='banks', to='stock_app.User'),
        ),
    ]
