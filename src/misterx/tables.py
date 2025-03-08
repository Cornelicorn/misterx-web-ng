import django_tables2 as tables

from .models import Game


class GameTable(tables.Table):
    class Meta:
        model = Game
        fields = [
            "name",
            "date",
        ]
