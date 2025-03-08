from django import template

register = template.Library()


@register.filter
def humanize_seconds(time):
    seconds = time
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    weeks = days // 7

    seconds = seconds % 60
    minutes = minutes % 60
    hours = hours % 24
    days = days % 7

    t_seconds = f"{seconds} second" if seconds else ""
    t_minutes = f"{minutes} minute" if minutes else ""
    t_hours = f"{hours}   hour" if hours else ""
    t_days = f"{days}    day" if days else ""
    t_weeks = f"{weeks}   week" if weeks else ""

    t_seconds = f"{t_seconds}s" if seconds > 1 else t_seconds
    t_minutes = f"{t_minutes}s" if minutes > 1 else t_minutes
    t_hours = f"{t_hours}s" if hours > 1 else t_hours
    t_days = f"{t_days}s" if days > 1 else t_days
    t_weeks = f"{t_weeks}s" if weeks > 1 else t_weeks

    return f"{t_weeks} {t_days} {t_hours} {t_minutes} {t_seconds}"
