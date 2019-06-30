import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from main.models import Post, Idea, Issue


def get_schedule_starttime():
    """Get time range for schedule

    Counts two dates:
    * beginning of this week
    * end of next week
    :return:
    """
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0)
    this_week_begin = today - datetime.timedelta(days=today.weekday())
    next_week_end = this_week_begin + datetime.timedelta(days=14)

    return this_week_begin, next_week_end


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


# Create your views here.
@login_required
def index(request):
    self_posts = Post.objects.prefetch_related('stage').filter(
        Q(stage__assignee__isnull=False, stage__assignee=request.user, ) |
        Q(stage__assignee__isnull=True, editor=request.user, )
    ).exclude(stage__slug__in=['vault', 'published'])

    need_to_vote = Idea.objects.filter(approved__isnull=True).exclude(votes__user=request.user)

    # TODO: rewrite as negative query
    opened_issues = Issue.objects.filter(
        posts__stage__slug__in=['waiting', 'proofreading_editor', 'precheck', 'spellcheck', 'markup',
                                'proofreading_spell', 'proofreading_chief_dpt', 'proofreading_chief', 'publishing']) \
        .distinct()

    # Count schedule
    schedule = {}
    time_start, time_end = get_schedule_starttime()
    scheduled_posts = Post.objects.filter(published_at__gte=time_start,
                                          published_at__lte=time_end)

    for day in daterange(time_start, time_end):
        # HACK: used to guaranteed suite day interval to today determination
        day_ = day.replace(hour=6, minute=6, second=6)
        schedule[day_] = list(filter(
            lambda p: day.astimezone() <= p.published_at <= day.astimezone() + datetime.timedelta(days=1),
            scheduled_posts))
    print(schedule)
    return render(request, 'plan/index/index.html', {
        'self_posts': self_posts,
        'need_to_vote': need_to_vote,
        'opened_issues': opened_issues,
        'schedule': schedule,
        'today': datetime.datetime.today().replace(hour=0, minute=0, second=0),
    })
