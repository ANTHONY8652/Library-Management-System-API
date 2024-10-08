# Generated by Django 5.0.7 on 2024-10-04 21:44

import library_api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_api', '0008_alter_transaction_due_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='loan_duration',
            field=models.PositiveIntegerField(default=14, validators=[library_api.models.UserProfile.validate_loan_duration]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('member', 'Member')], default='member', max_length=6, validators=[library_api.models.UserProfile.validate_role]),
        ),
    ]
