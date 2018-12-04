from django import template
from main.models import Vote
from finance.models import Payment
from django.urls import reverse
from plan.views import posts, ideas
import datetime

register = template.Library()


@register.filter(name='voted')
def voted(value, user):
    return value.voted(user)


@register.filter(name='humanize_score')
def humanize_score(value):
    return Vote.SCORE_CHOICES[value][1]


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
        raise template.TemplateSyntaxError("'set' tag must be of the form: {% set <var_name> = <var_value> %}")

    return SetVarNode(parts[1], parts[3])


@register.filter
def divide(value, arg):
    try:
        return str(int(value) / int(arg))
    except (ValueError, ZeroDivisionError):
        return None


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
