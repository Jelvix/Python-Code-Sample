# Generated by Django 2.1.4 on 2019-02-16 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stuff', '0013_auto_20190204_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persons', to='company.Company', verbose_name='Company'),
        ),
    ]
