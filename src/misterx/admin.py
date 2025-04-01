from django.contrib import admin

from .models import Game, OrderedTask, Task

admin.site.register(Game)
admin.site.register(OrderedTask)
admin.site.register(Task)
