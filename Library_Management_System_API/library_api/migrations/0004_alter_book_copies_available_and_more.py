# Generated by Django 5.0.7 on 2024-09-29 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library_api', '0003_transaction_due_date_userprofile_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='copies_available',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='date_of_membership',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('member', 'Member')], default='MEMBER', max_length=6),
        ),
    ]
