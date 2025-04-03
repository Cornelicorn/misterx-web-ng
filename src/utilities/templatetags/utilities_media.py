import magic
from django import template

register = template.Library()


def get_mime_type(f):
    f.seek(0)
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(f.read(2048))
    f.seek(0)
    return mime_type


def get_main_mime_type(file):
    mime_type = get_mime_type(file)
    if mime_type is not None:
        mime_type = mime_type.split("/")[0]
    return mime_type


@register.filter
@register.simple_tag
def mime_type(file):
    return get_mime_type(file)


@register.filter
@register.simple_tag
def main_mime_type(file):
    return get_main_mime_type(file)
