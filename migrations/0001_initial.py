# Generated by Django 3.0.6 on 2020-06-09 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_code', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=25)),
                ('point_count', models.IntegerField(default=0)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grards.Game')),
            ],
        ),
        migrations.CreateModel(
            name='Grard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_text', models.TextField()),
                ('discarded', models.BooleanField(default=False)),
                ('current_owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='grards.Player')),
            ],
        ),
    ]
