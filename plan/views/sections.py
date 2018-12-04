from django.shortcuts import render
from main.models import Section
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def index(request):
    return render(request, 'plan/sections/index.html', {
        'sections': Section.objects.order_by('sort').all()
    })
