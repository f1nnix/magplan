from django.db import models

from magplan.models.abs import AbstractBase
from magplan.models.idea import Idea
from magplan.models.user import User


class Vote(AbstractBase):
    SCORE_0 = 0
    SCORE_25 = 25
    SCORE_50 = 50
    SCORE_75 = 75
    SCORE_100 = 100
    SCORE_CHOICES = (
        (SCORE_0, "Против таких статей в «Хакере»"),
        (SCORE_25, "Не верю, что выйдет хорошо"),
        (SCORE_50, "Тема нормальная, но не для меня"),
        (SCORE_75, "Почитал бы, встретив в журнале"),
        (SCORE_100, "Ради таких статей мог бы подписаться"),
    )
    score = models.SmallIntegerField(choices=SCORE_CHOICES, default=SCORE_50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(
        Idea, on_delete=models.CASCADE, related_name="votes"
    )

    @property
    def score_humanized(self):
        return self.__class__.SCORE_CHOICES
