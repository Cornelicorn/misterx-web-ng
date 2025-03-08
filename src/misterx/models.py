from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def get_default_game_name() -> str:
    return _("Mister X {date}").format(date=date.today().isoformat())


class Player(User):
    class Meta:
        proxy = True


class PlayerGroup(Group):
    class Meta:
        proxy = True


class Task(models.Model):
    task = models.TextField(_("Task"), help_text=_("The task that has to be solved"))
    points = models.PositiveIntegerField(_("Points"), help_text=_("How many points will be awarded for completing this task"))
    solution = models.TextField(_("Solution"), help_text=_("Solution for this task"), null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.task} ({self.points}P)"

    def get_absolute_url(self):
        return reverse("misterx:task-detail", kwargs={"pk": self.id})

    def has_been_completed(self, game: "Game") -> bool:
        if game.submissions.filter(task=self, accepted=True).count():
            return True
        else:
            return False

    def completed_by_group(self, game: "Game", group: PlayerGroup) -> bool:
        if game.submissions.filter(task=self, accepted=True, group=group).count():
            return True
        else:
            return False


class Game(models.Model):
    tasks = models.ManyToManyField(Task, related_name="games", blank=True)
    name = models.CharField(_("Name of Task Set"), max_length=255, default=get_default_game_name)
    date = models.DateField(_("Date of the game"), default=date.today)
    groups = models.ManyToManyField(PlayerGroup, related_name="games", blank=True)
    active = models.BooleanField(
        _("Active"),
        default=False,
        help_text=_(
            "Whether this game is active. Only one game can be active at the same time, setting this will override the value of the currently active model"
        ),
    )

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("misterx:game-detail", kwargs={"pk": self.id})

    class Meta:
        ordering = ["-date"]
        constraints = [
            UniqueConstraint(
                fields=["active"],
                condition=models.Q(active=True),
                name="unique_active",
                violation_error_message=_("There is an active game already."),
            )
        ]


class Submission(models.Model):
    group = models.ForeignKey(PlayerGroup, related_name="submissions", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name="submissions", on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name="submissions", on_delete=models.CASCADE)
    time = models.DateTimeField(_("Time"), help_text=_("Time of submission"), auto_now=True)
    accepted = models.BooleanField(
        _("Accepted"), help_text=_("Whether the solution was accepted"), null=True, blank=True, default=None
    )
    points_override = models.PositiveIntegerField(
        _("Granted points"),
        help_text="Override the number of points the group will receive for this submission",
        null=True,
        blank=True,
        default=None,
    )
    explanation = models.TextField(
        _("Explanation"), help_text=_("Further explanations you might want to add"), null=True, blank=True
    )

    @property
    def granted_points(self) -> int:
        if not self.accepted:
            return 0
        elif self.points_override is not None:
            return self.points_override
        else:
            return self.task.points

    def __str__(self) -> str:
        return f"{self.group} with task {self.task}"

    def get_absolute_url(self):
        return reverse("misterx:submission-detail", kwargs={"pk": self.id})

    class Meta:
        indexes = [
            models.Index(fields=["task"], name="%(app_label)s_%(class)s_task_idx"),
            models.Index(fields=["-time"], name="%(app_label)s_%(class)s_time_idx"),
        ]
