from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse

from magplan.models import Issue, User


@login_required
def issues_search(request):
    q = request.GET.get('q', None)
    issues = Issue.objects.filter(number__exact=q)
    return JsonResponse(
        [{'id': issue.id, 'text': issue.__str__()} for issue in issues]
        , safe=False)


@login_required
def authors_search(request):
    q = request.GET.get('q', None)

    # FIXME: heavy request, should be optimized
    users = User.objects.filter(
        Q(email__icontains=q) |
        Q(meta__icontains=q) |
        Q(profile__f_name__icontains=q) |
        Q(profile__l_name__icontains=q) |
        Q(profile__m_name__icontains=q)
    )
    return JsonResponse(
        [{'id': user.id, 'text': user.__str__()} for user in users]
        , safe=False)
