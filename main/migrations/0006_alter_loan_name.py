# Generated by Django 4.2.9 on 2024-04-06 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_record_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
