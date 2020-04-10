# Generated by Django 3.0.1 on 2020-04-09 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ACL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('adminStatus', models.IntegerField(default=0)),
                ('versionManagement', models.IntegerField(default=0)),
                ('createNewUser', models.IntegerField(default=0)),
                ('listUsers', models.IntegerField(default=0)),
                ('deleteUser', models.IntegerField(default=0)),
                ('resellerCenter', models.IntegerField(default=0)),
                ('changeUserACL', models.IntegerField(default=0)),
                ('createWebsite', models.IntegerField(default=0)),
                ('modifyWebsite', models.IntegerField(default=0)),
                ('suspendWebsite', models.IntegerField(default=0)),
                ('deleteWebsite', models.IntegerField(default=0)),
                ('createPackage', models.IntegerField(default=0)),
                ('listPackages', models.IntegerField(default=0)),
                ('deletePackage', models.IntegerField(default=0)),
                ('modifyPackage', models.IntegerField(default=0)),
                ('createDatabase', models.IntegerField(default=1)),
                ('deleteDatabase', models.IntegerField(default=1)),
                ('listDatabases', models.IntegerField(default=1)),
                ('createNameServer', models.IntegerField(default=0)),
                ('createDNSZone', models.IntegerField(default=1)),
                ('deleteZone', models.IntegerField(default=1)),
                ('addDeleteRecords', models.IntegerField(default=1)),
                ('createEmail', models.IntegerField(default=1)),
                ('listEmails', models.IntegerField(default=1)),
                ('deleteEmail', models.IntegerField(default=1)),
                ('emailForwarding', models.IntegerField(default=1)),
                ('changeEmailPassword', models.IntegerField(default=1)),
                ('dkimManager', models.IntegerField(default=1)),
                ('createFTPAccount', models.IntegerField(default=1)),
                ('deleteFTPAccount', models.IntegerField(default=1)),
                ('listFTPAccounts', models.IntegerField(default=1)),
                ('createBackup', models.IntegerField(default=1)),
                ('restoreBackup', models.IntegerField(default=0)),
                ('addDeleteDestinations', models.IntegerField(default=0)),
                ('scheDuleBackups', models.IntegerField(default=0)),
                ('remoteBackups', models.IntegerField(default=0)),
                ('manageSSL', models.IntegerField(default=1)),
                ('hostnameSSL', models.IntegerField(default=0)),
                ('mailServerSSL', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Administrator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userName', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=200)),
                ('firstName', models.CharField(default='None', max_length=20)),
                ('lastName', models.CharField(default='None', max_length=20)),
                ('email', models.CharField(max_length=50)),
                ('type', models.IntegerField()),
                ('owner', models.IntegerField(default=1)),
                ('token', models.CharField(default='None', max_length=500)),
                ('api', models.IntegerField(default=0)),
                ('securityLevel', models.IntegerField(default=0)),
                ('state', models.CharField(default='ACTIVE', max_length=10)),
                ('initWebsitesLimit', models.IntegerField(default=0)),
                ('acl', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='loginSystem.ACL')),
            ],
        ),
    ]
