import django_tables2 as tables
from utilities.tables.columns import OpenColumn, EditColumn

from .models import Game


class GameTable(tables.Table):
    open = OpenColumn("misterx:game-detail")
    edit = EditColumn("misterx:game-edit")
    class Meta:
        model = Game
        fields = [
            "name",
            "date",
            "open",
            "edit",
        ]
