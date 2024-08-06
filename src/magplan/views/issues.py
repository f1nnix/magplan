from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render

from magplan.forms import IssueModelForm
from magplan.models import Issue, Magazine


# Create your views here.
@login_required
def index(request):
    issues = (
        Issue.on_current_site.all()
        .order_by("-number")
        .prefetch_related("magazine")
    )

    return render(
        request,
        "magplan/issues/index.html",
        {
            "issues": issues,
        },
    )


@login_required
def create(request):
    form = IssueModelForm()
    if request.method == "POST":
        form = IssueModelForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.magazine = Magazine.objects.first()
            issue.save()
            return redirect("issues_index")

    return render(
        request,
        "magplan/issues/new.html",
        {
            "form": form,
        },
    )


@login_required
def show(request, issue_id):
    issue = Issue.objects.get(id=issue_id)
    posts = (
        issue.posts.all()
        .order_by("section__sort")
        .prefetch_related("authors", "editor", "stage", "section")
        .exclude(stage__slug="vault")
    )

    return render(
        request,
        "magplan/issues/show.html",
        {
            "issue": issue,
            "posts": posts,
            "stats": {
                "has_text": len(
                    list(
                        filter(
                            lambda p: (p.xmd is not None) and (p.xmd != ""),
                            posts,
                        )
                    )
                ),
                "incomplete": len(
                    list(filter(lambda p: p.stage.slug != "published", posts))
                ),
            },
        },
    )
