import django_tables2 as tables
from django.utils.translation import gettext_lazy as _


class OpenColumn(tables.TemplateColumn):
    def __init__(self, url_target: str, verbose_name: str = _("Open")):
        super().__init__(
            template_name="utilities/tables/columns/open.html",
            verbose_name=verbose_name,
            attrs={
                "td": {"align": "right"},
                "th": {"style": "text-align: right;", "class": "w-1"},
            },
            orderable=False,
        )
        self.extra_context.update({"url_target": url_target})


class EditColumn(tables.TemplateColumn):
    def __init__(self, url_target: str, verbose_name: str = _("Edit")):
        super().__init__(
            template_name="utilities/tables/columns/edit.html",
            verbose_name=verbose_name,
            attrs={
                "td": {"align": "right"},
                "th": {"style": "text-align: right;", "class": "w-1"},
            },
            orderable=False,
        )
        self.extra_context.update({"url_target": url_target})


class DeleteColumn(tables.TemplateColumn):
    def __init__(self, url_target: str, verbose_name: str = _("Delete")):
        super().__init__(
            template_name="utilities/tables/columns/delete.html",
            verbose_name=verbose_name,
            attrs={
                "td": {"align": "right"},
                "th": {"style": "text-align: right;", "class": "w-1"},
            },
            orderable=False,
        )
        self.extra_context.update({"url_target": url_target})


class HumanizedSecondsColumn(tables.TemplateColumn):
    def __init__(self):
        super().__init__(template_name="utilities/tables/columns/humanized_seconds.html")
