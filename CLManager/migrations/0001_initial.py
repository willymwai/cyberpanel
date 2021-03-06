# Generated by Django 3.0.1 on 2020-04-09 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('packages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CLPackages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('speed', models.CharField(max_length=50)),
                ('vmem', models.CharField(max_length=50)),
                ('pmem', models.CharField(max_length=50)),
                ('io', models.CharField(max_length=50)),
                ('iops', models.CharField(max_length=50)),
                ('ep', models.CharField(max_length=50)),
                ('nproc', models.CharField(max_length=50)),
                ('inodessoft', models.CharField(max_length=50)),
                ('inodeshard', models.CharField(max_length=50)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='packages.Package')),
            ],
        ),
    ]
