# Generated by Django 3.0.1 on 2020-04-09 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DBUsers',
            fields=[
                ('host', models.CharField(db_column='Host', max_length=60, primary_key=True, serialize=False)),
                ('user', models.CharField(db_column='User', max_length=16)),
                ('password', models.CharField(db_column='Password', max_length=41)),
                ('select_priv', models.CharField(db_column='Select_priv', max_length=1)),
                ('insert_priv', models.CharField(db_column='Insert_priv', max_length=1)),
                ('update_priv', models.CharField(db_column='Update_priv', max_length=1)),
                ('delete_priv', models.CharField(db_column='Delete_priv', max_length=1)),
                ('create_priv', models.CharField(db_column='Create_priv', max_length=1)),
                ('drop_priv', models.CharField(db_column='Drop_priv', max_length=1)),
                ('reload_priv', models.CharField(db_column='Reload_priv', max_length=1)),
                ('shutdown_priv', models.CharField(db_column='Shutdown_priv', max_length=1)),
                ('process_priv', models.CharField(db_column='Process_priv', max_length=1)),
                ('file_priv', models.CharField(db_column='File_priv', max_length=1)),
                ('grant_priv', models.CharField(db_column='Grant_priv', max_length=1)),
                ('references_priv', models.CharField(db_column='References_priv', max_length=1)),
                ('index_priv', models.CharField(db_column='Index_priv', max_length=1)),
                ('alter_priv', models.CharField(db_column='Alter_priv', max_length=1)),
                ('show_db_priv', models.CharField(db_column='Show_db_priv', max_length=1)),
                ('super_priv', models.CharField(db_column='Super_priv', max_length=1)),
                ('create_tmp_table_priv', models.CharField(db_column='Create_tmp_table_priv', max_length=1)),
                ('lock_tables_priv', models.CharField(db_column='Lock_tables_priv', max_length=1)),
                ('execute_priv', models.CharField(db_column='Execute_priv', max_length=1)),
                ('repl_slave_priv', models.CharField(db_column='Repl_slave_priv', max_length=1)),
                ('repl_client_priv', models.CharField(db_column='Repl_client_priv', max_length=1)),
                ('create_view_priv', models.CharField(db_column='Create_view_priv', max_length=1)),
                ('show_view_priv', models.CharField(db_column='Show_view_priv', max_length=1)),
                ('create_routine_priv', models.CharField(db_column='Create_routine_priv', max_length=1)),
                ('alter_routine_priv', models.CharField(db_column='Alter_routine_priv', max_length=1)),
                ('create_user_priv', models.CharField(db_column='Create_user_priv', max_length=1)),
                ('event_priv', models.CharField(db_column='Event_priv', max_length=1)),
                ('trigger_priv', models.CharField(db_column='Trigger_priv', max_length=1)),
                ('create_tablespace_priv', models.CharField(db_column='Create_tablespace_priv', max_length=1)),
                ('ssl_type', models.CharField(max_length=9)),
                ('ssl_cipher', models.TextField()),
                ('x509_issuer', models.TextField()),
                ('x509_subject', models.TextField()),
                ('max_questions', models.IntegerField()),
                ('max_updates', models.IntegerField()),
                ('max_connections', models.IntegerField()),
                ('max_user_connections', models.IntegerField()),
                ('plugin', models.CharField(max_length=64)),
                ('authentication_string', models.TextField()),
            ],
            options={
                'db_table': 'user',
                'unique_together': {('host', 'user')},
            },
        ),
    ]
