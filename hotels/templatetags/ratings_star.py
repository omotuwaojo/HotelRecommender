from django import template

register = template.Library()

@register.filter
@register.simple_tag
def stars(rating):
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - int(half_star)
    return '★' * full_stars + ('½' if half_star else '') + '☆' * empty_stars
