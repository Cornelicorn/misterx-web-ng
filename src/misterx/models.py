import uuid
from collections import defaultdict
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import UniqueConstraint
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def get_default_game_name() -> str:
    return _("Mister X {date}").format(date=date.today().isoformat())


class Player(User):
    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse("misterx:player-detail", kwargs={"pk": self.id})


class PlayerGroup(Group):
    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse("misterx:playergroup-detail", kwargs={"pk": self.id})


class Task(models.Model):
    task = models.TextField(_("Task"), help_text=_("The task that has to be solved"))
    points = models.PositiveIntegerField(_("Points"), help_text=_("How many points will be awarded for completing this task"))
    solution = models.TextField(_("Solution"), help_text=_("Solution for this task"), null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.task} ({self.points}P)"

    def get_absolute_url(self):
        return reverse("misterx:task-detail", kwargs={"pk": self.id})

    def has_been_completed(self, game: "Game") -> bool:
        return game.submissions.filter(task=self, accepted=True).exists()

    def completed_by_group(self, game: "Game", group: PlayerGroup) -> bool:
        return game.submissions.filter(task=self, accepted=True, group=group).exists()


class OrderedTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    task_number = models.IntegerField(verbose_name=_("Task number"), null=True, blank=True)

    def __str__(self):
        return f"{self.task_number or _('Unordered')}: {self.task}"

    class Meta:
        ordering = ["task_number"]
        constraints = [
            UniqueConstraint(
                fields=["task", "game"],
                name="unique_game_task_associations",
            )
        ]


class Game(models.Model):
    tasks = models.ManyToManyField(Task, verbose_name=_("Tasks"), related_name="games", blank=True, through=OrderedTask)
    name = models.CharField(_("Name"), max_length=255, default=get_default_game_name)
    date = models.DateField(_("Date of the game"), default=date.today)
    groups = models.ManyToManyField(PlayerGroup, verbose_name=_("Playergroups"), related_name="games", blank=True)
    active = models.BooleanField(
        _("Active"),
        default=False,
        help_text=_(
            "Whether this game is active. Only one game can be active at the same time, activating this game deactivates the currently active game"
        ),
    )

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("misterx:game-detail", kwargs={"pk": self.id})

    # Another active game doesn't make this game invalid, as it is deactivated when saving, see save()
    def validate_constraints(self, exclude=None):
        super().validate_constraints(exclude={*(exclude or ()), "active"})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.active:
                Game.objects.filter(active=True).exclude(pk=self.pk).update(active=False)
            super().save(*args, **kwargs)

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


def get_players_in_multiple_groups(games: models.QuerySet[Game]) -> dict[Game, dict[Player, list[Group]]]:
    """
    Finds the players who are in more than one group of one of the given games, which can happen when groups are
    changed in the admin. Returns their groups by player by game.
    """
    groups_of_players = defaultdict(set)
    for game_id, group_id, user_id in games.values_list("pk", "groups", "groups__user"):
        if user_id is not None:
            groups_of_players[game_id, user_id].add(group_id)
    conflicts = {key: group_ids for key, group_ids in groups_of_players.items() if len(group_ids) > 1}
    if not conflicts:
        return {}

    games_by_id = Game.objects.in_bulk({game_id for game_id, _user_id in conflicts})
    players_by_id = Player.objects.in_bulk({user_id for _game_id, user_id in conflicts})
    groups_by_id = PlayerGroup.objects.in_bulk(set().union(*conflicts.values()))
    result: dict[Game, dict[Player, list[Group]]] = {}
    for (game_id, user_id), group_ids in sorted(conflicts.items()):
        groups = sorted((groups_by_id[group_id] for group_id in group_ids), key=str)
        result.setdefault(games_by_id[game_id], {})[players_by_id[user_id]] = groups
    return result


class Submission(models.Model):
    group = models.ForeignKey(PlayerGroup, verbose_name=_("Group"), related_name="submissions", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, verbose_name=_("Game"), related_name="submissions", on_delete=models.CASCADE)
    task = models.ForeignKey(Task, verbose_name=_("Task"), related_name="submissions", on_delete=models.CASCADE)
    time = models.DateTimeField(_("Time"), help_text=_("Time of submission"), auto_now_add=True)
    submitter = models.ForeignKey(
        Player, verbose_name=_("Submitter"), related_name="submissions", null=True, on_delete=models.SET_NULL
    )
    accepted = models.BooleanField(
        _("Accepted"), help_text=_("Whether the solution was accepted"), null=True, blank=True, default=None
    )
    points_override = models.PositiveIntegerField(
        _("Granted points override"),
        help_text=_("Override the number of points the group will receive for this submission"),
        null=True,
        blank=True,
        default=None,
    )
    explanation = models.TextField(
        _("Explanation"), help_text=_("Further explanations you might want to add"), null=True, blank=True
    )
    feedback = models.TextField(
        _("Feedback"), help_text=_("Optional feedback on why this wasn't accepted"), null=True, blank=True
    )

    @property
    def granted_points(self) -> int:
        if not self.accepted:
            return 0
        elif self.points_override is not None:
            return self.points_override

        # Only the first accepted submission of a group for a task is awarded points
        first_accepted = (
            Submission.objects.filter(game=self.game, task=self.task, group=self.group)
            .order_by("time")
            .filter(accepted=True)
            .first()
        )
        if first_accepted is not None and first_accepted.pk != self.pk:
            return 0
        else:
            return self.task.points

    def __str__(self) -> str:
        return f"{self.group} with task {self.task}"

    def get_absolute_url(self):
        return reverse("misterx:submission-detail", kwargs={"pk": self.id})

    def clean(self):
        error_dict = {}
        # Missing game, task or group are already reported by the field validation
        if self.game_id is not None and self.task_id is not None and self.task not in self.game.tasks.all():
            error_dict["task"] = _("The selected task is not chosen in the selected game")
        if self.game_id is not None and self.group_id is not None and self.group not in self.game.groups.all():
            error_dict["group"] = _("The selected group is not playing in the selected game")
        if self.submitter and self.group_id is not None and self.group not in self.submitter.groups.all():
            error_dict["submitter"] = _("The selected submitter is not part of the selected group")
        if error_dict:
            raise ValidationError(error_dict)
        return super().clean()

    class Meta:
        indexes = [
            models.Index(fields=["task"], name="%(app_label)s_%(class)s_task_idx"),
            models.Index(fields=["-time"], name="%(app_label)s_%(class)s_time_idx"),
        ]


def get_upload_path(instance: "Upload", filename: str):
    sub = instance.submission
    uuid = instance.uuid
    return f"proofs/{sub.game.pk}/{sub.group.pk}/{sub.task.pk}/{uuid}.{filename}"


class Upload(models.Model):
    submission = models.ForeignKey("Submission", on_delete=models.CASCADE, related_name="proofs")
    uuid = models.UUIDField(verbose_name=_("UUID for upload"), default=uuid.uuid4, editable=False)
    file = models.FileField(_("File"), upload_to=get_upload_path)
