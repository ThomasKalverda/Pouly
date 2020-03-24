# Generated by Django 3.0.4 on 2020-03-23 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lobby', '0004_auto_20200320_1733'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('poule', '0006_auto_20200321_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='poule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='lobby.Poule'),
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.SmallIntegerField(default=0)),
                ('poule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='lobby.Poule')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prediction1', models.SmallIntegerField(blank=True, null=True)),
                ('prediction2', models.SmallIntegerField(blank=True, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictions', to='poule.Game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
