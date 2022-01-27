# Generated by Django 3.0.6 on 2020-06-13 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grards', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlackGrard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_text', models.TextField()),
                ('last_text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='WhiteGrard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_text', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='grard',
            name='current_owner',
        ),
        migrations.RemoveField(
            model_name='player',
            name='game',
        ),
        migrations.DeleteModel(
            name='Game',
        ),
        migrations.DeleteModel(
            name='Grard',
        ),
        migrations.DeleteModel(
            name='Player',
        ),
    ]
