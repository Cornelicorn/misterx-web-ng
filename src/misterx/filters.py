from django_filters import FilterSet

from .forms import FilterForm
from .models import Game


class GameFilter(FilterSet):
    class Meta:
        model = Game
        form = FilterForm
        fields = [
            "name",
            "date",
        ]
