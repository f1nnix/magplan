import datetime
from typing import Generator, Tuple

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from magplan.models import Idea, Issue, Post


def get_schedule_starttime() -> Tuple[datetime.datetime, datetime.datetime]:
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


def daterange(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    skip_weekend: bool = True,
) -> Generator:
    """Yield every day date between two dates.

    Pre-fixes provided dates to include full day cycle.
    @generator
    """
    weekend_days = (5, 6)

    # Fix daterange to include full day cycle to prevent comparison failures
    start_date = start_date.replace(hour=0, minute=0, second=0)
    end_date = end_date.replace(hour=23, minute=59, second=59)
    start_day_weekday = start_date.weekday()

    for days in range(int((end_date - start_date).days)):
        if skip_weekend is False:
            yield start_date + datetime.timedelta(days)
            continue

        next_date_weekday = (start_day_weekday + days) % 7
        if next_date_weekday not in weekend_days:
            yield start_date + datetime.timedelta(days)


# Create your views here.
@login_required
def index(request):
    self_posts = (
        Post.objects.prefetch_related('stage')
        .filter(
            Q(stage__assignee__isnull=False, stage__assignee=request.user.user)
            | Q(stage__assignee__isnull=True, editor=request.user.user)
        )
        .exclude(stage__slug__in=['vault', 'published'])
    )

    need_to_vote = Idea.objects.filter(approved__isnull=True).exclude(
        votes__user=request.user.user
    )

    opened_issues = Issue.objects.filter(
        posts__stage__slug__in=[
            'waiting',
            'proofreading_editor',
            'precheck',
            'spellcheck',
            'markup',
            'proofreading_spell',
            'proofreading_chief_dpt',
            'proofreading_chief',
            'publishing',
        ]
    ).distinct()

    # Count schedule
    schedule = {}
    time_start, time_end = get_schedule_starttime()
    scheduled_posts = Post.objects.filter(
        published_at__gte=time_start, published_at__lte=time_end
    )

    for day in daterange(time_start, time_end):
        schedule[day] = list(
            filter(
                lambda p: day.astimezone()
                <= p.published_at
                <= day.astimezone() + datetime.timedelta(days=1),
                scheduled_posts,
            )
        )

    return render(
        request,
        'magplan/index/index.html',
        {
            'self_posts': self_posts,
            'need_to_vote': need_to_vote,
            'opened_issues': opened_issues,
            'schedule': schedule,
            'today': datetime.datetime.today().replace(hour=0, minute=0, second=0),
        },
    )
