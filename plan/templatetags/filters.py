import datetime
import re
from typing import List

from django import template
from django.conf import settings
from django.urls import reverse

from finance.models import Payment
from main.models import Vote, Comment
from plan.views import posts, ideas

register = template.Library()


@register.filter(name='voted')
def voted(value, user):
    return value.voted(user)


@register.filter(name='humanize_score')
def humanize_score(value):
    # Unsafe. but should work for fair use
    return Vote.SCORE_CHOICES[value // 25][1]


@register.filter(name='times')
def times(number):
    return range(number)


@register.filter(name='trim_filename')
def trim_filename(filename):
    if len(filename) > 30:
        return '%s...%s' % (
            filename[:20],
            filename[-5:]
        )
    return filename


@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None


class SetVarNode(template.Node):

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value

        return u""


@register.tag(name='set')
def set_var(parser, token):
    """
    {% set some_var = '123' %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError(
            "'set' tag must be of the form: {% set <var_name> = <var_value> %}")

    return SetVarNode(parts[1], parts[3])


@register.filter
def can_be_moved_to_stage_by(post, user):
    return (post.stage.assignee and post.stage.assignee == user) or \
           (not post.stage.assignee and post.editor == user)


@register.filter
def sub(value, arg):
    return value - arg


@register.filter
def url_for_post_comments(post):
    return reverse(posts.comments, kwargs={
        'post_id': post.id,
    })


@register.filter
def url_for_idea_comments(idea):
    return reverse(ideas.comments, kwargs={
        'idea_id': idea.id,
    })


@register.filter
def is_overdue(date):
    return date > datetime.datetime.now()


@register.filter
def humazine_payment_type(payment):
    return Payment.FORMAT_CHOICES[payment.format][1]


@register.filter
def count_human_comments(comments: List[Comment]) -> int:
    """Count comment from arrays, made by real users.

    It seems, plain iterator with incrementable counter may be faster
    as it does not produce additional map in closure.

        counter = 0
        for comment in comments:
            if comment.type != Comment.TYPE_SYSTEM:
                counter+=1
        return counter

    :param comments: Array of Comment instances
    :return: Actual comments number
    """
    return len(list(filter(lambda c: c.type != Comment.TYPE_SYSTEM, comments)))


@register.filter
def date_class(datetime_obj: datetime.datetime) -> str:
    """Return numeric representaion of provided dates, where:

    datetime_obj|f = 1 if passed
    datetime_obj|f = 2 if today
    datetime_obj|f = 0 else
    """
    # Convert 'datetime' => 'date' class for easier comparison
    date = datetime_obj.date()
    today = datetime.datetime.now().date()

    if date < today:
        return 'past'
    elif date == today:
        return 'today'
    else:
        return ''


@register.filter
def get_item(dictionary, key):
    return dictionary[key]


numeric_test = re.compile("^\d+$")


@register.filter(name='get_attr')
def get_attr(value, arg):
    """Gets an attribute of an object dynamically from a string name"""

    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        return settings.TEMPLATE_STRING_IF_INVALID
