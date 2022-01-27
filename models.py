from django.db import models

class Grard(models.Model):
    type = models.CharField(max_length=25)
    card_text = models.TextField()

class CahCard(models.Model):
    type = models.CharField(max_length=25)
    card_text = models.TextField()

# class BlackGrard(models.Model):
#     first_text = models.TextField()
#     last_text = models.TextField()


# class Game(models.Model):
#     game_code = models.IntegerField()
#
# class Player(models.Model):
#     user_name = models.CharField(max_length=25)
#     point_count = models.IntegerField(default=0)
#     game = models.ForeignKey(Game, on_delete=models.CASCADE)
