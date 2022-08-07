# Generated by Django 4.0.6 on 2022-08-05 20:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_accounts_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_line_1', models.CharField(blank=True, max_length=350)),
                ('address_line_2', models.CharField(blank=True, max_length=350)),
                ('profile_picture', models.ImageField(blank=True, upload_to='user profile')),
                ('country', models.CharField(max_length=150)),
                ('state', models.CharField(max_length=150)),
                ('city', models.CharField(max_length=150)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]