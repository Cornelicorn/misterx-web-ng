from django.views.generic import CreateView


class InitialCreateView(CreateView):
    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.request.GET.items())
        return initial
