# Generated by Django 5.2 on 2025-04-22 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_chat'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='user_id',
            new_name='user',
        ),
    ]
