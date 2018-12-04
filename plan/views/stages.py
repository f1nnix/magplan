from django.shortcuts import render
from main.models import Stage
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def index(request):
    return render(request, 'plan/stages/index.html', {
        'stages': (Stage.objects.order_by('sort').all()
                   .prefetch_related('prev_stage', 'next_stage', 'assignee'))
    })
