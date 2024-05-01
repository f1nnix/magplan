from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from magplan.models import Section


# Create your views here.
@login_required
def index(request):
    return render(
        request,
        "magplan/sections/index.html",
        {"sections": Section.objects.order_by("sort").all()},
    )
