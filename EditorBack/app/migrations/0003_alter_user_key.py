# Generated by Django 5.0.6 on 2024-07-09 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_user_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='key',
            field=models.CharField(max_length=128, null=True, verbose_name='访问令牌'),
        ),
    ]