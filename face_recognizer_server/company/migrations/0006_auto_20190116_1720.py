# Generated by Django 2.1.4 on 2019-01-16 17:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0005_auto_20181225_1620'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='door',
            name='status',
        ),
        migrations.RemoveField(
            model_name='door',
            name='to_company',
        ),
        migrations.AddField(
            model_name='door',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='company.Company', verbose_name='Company FK'),
        ),
    ]