from django.contrib import admin

from .models import Game, OrderedTask, Submission, Task, Upload

admin.site.register(Game)
admin.site.register(OrderedTask)
admin.site.register(Submission)
admin.site.register(Task)
admin.site.register(Upload)
