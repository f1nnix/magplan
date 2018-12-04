from django.shortcuts import redirect


# Create your views here.
def index(request):
    return redirect('index_index')
