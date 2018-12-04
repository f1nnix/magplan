from main.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from main.models import Issue

from django.db.models import Q
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
    users = User.objects.filter(
        Q(email__icontains=q) |
        Q(meta__icontains=q)
    )
    return JsonResponse(
        [{'id': user.id, 'text': user.__str__()} for user in users]
    , safe=False)
