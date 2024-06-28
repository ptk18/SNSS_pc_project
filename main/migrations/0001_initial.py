# Generated by Django 5.0.6 on 2024-06-28 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customerName', models.CharField(max_length=70)),
                ('customerCode', models.CharField(max_length=70)),
                ('templateName', models.CharField(max_length=70)),
                ('customerPartNumber', models.CharField(max_length=70)),
                ('SNSSPartNumber', models.CharField(max_length=70)),
                ('category', models.CharField(default='GEN', max_length=70)),
                ('templateID', models.CharField(default='NULL', max_length=70)),
            ],
            options={
                'db_table': 'customerData',
            },
        ),
        migrations.CreateModel(
            name='CustomerOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('templateName', models.CharField(max_length=70)),
                ('customerCode', models.CharField(max_length=70)),
                ('customerPartNumber', models.CharField(max_length=70)),
                ('orderQuantity', models.IntegerField()),
                ('deliveryDate', models.CharField(max_length=70)),
                ('deliveryTime', models.CharField(default='NULL', max_length=70)),
                ('deliveryPlant', models.CharField(default='NULL', max_length=70)),
                ('templateID', models.CharField(max_length=70)),
            ],
            options={
                'db_table': 'customerOrder',
            },
        ),
        migrations.CreateModel(
            name='CustomerOrderForecast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('templateName', models.CharField(max_length=70)),
                ('customerCode', models.CharField(max_length=70)),
                ('customerPartNumber', models.CharField(max_length=70)),
                ('orderQuantity', models.IntegerField()),
                ('deliveryDate', models.CharField(max_length=70)),
                ('deliveryTime', models.CharField(default='NULL', max_length=70)),
                ('deliveryPlant', models.CharField(default='NULL', max_length=70)),
                ('templateID', models.CharField(max_length=70)),
            ],
            options={
                'db_table': 'customerOrderForecast',
            },
        ),
        migrations.CreateModel(
            name='StockData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snssPartID', models.IntegerField()),
                ('snssPartNumber', models.CharField(max_length=70)),
                ('stockQty', models.CharField(max_length=70)),
                ('lineInfo', models.CharField(max_length=70)),
                ('dateImport', models.CharField(max_length=70)),
            ],
            options={
                'db_table': 'stockData',
            },
        ),
        migrations.CreateModel(
            name='TemplateActualNormal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('templateID', models.IntegerField()),
                ('templateName', models.CharField(max_length=70)),
                ('templateType', models.CharField(max_length=70)),
                ('startRow', models.IntegerField()),
                ('columnName', models.CharField(max_length=70)),
                ('columnNumber', models.CharField(max_length=30)),
                ('fileType', models.CharField(max_length=30)),
                ('condition', models.CharField(max_length=200)),
                ('amountdaysplus', models.IntegerField(default=0)),
                ('columnNumberplus', models.IntegerField(default=0)),
                ('needBackupData', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'template_actual_n',
            },
        ),
        migrations.CreateModel(
            name='TemplateSpecial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('templateID', models.IntegerField()),
                ('templateName', models.CharField(max_length=70)),
                ('templateType', models.CharField(max_length=70)),
                ('startRow', models.IntegerField()),
                ('columnName', models.CharField(max_length=70)),
                ('columnNumber', models.CharField(max_length=30)),
                ('fileType', models.CharField(max_length=30)),
                ('needBackupData', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'template_s',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=30)),
                ('password', models.CharField(max_length=50)),
                ('fname', models.CharField(default='First Name', max_length=70)),
                ('lname', models.CharField(default='Last Name', max_length=70)),
                ('department', models.CharField(default='Engineering', max_length=70)),
            ],
            options={
                'db_table': 'user',
            },
        ),
    ]