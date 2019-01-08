from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import models

import datetime

# Create your views here.
def dashboard(request):
    if request.user.is_authenticated:
        tks = models.tasks.objects.filter(year=datetime.date.today().year)
        context = {'tks':tks}
        return render(request, 'bedrock/dashboard.html', context)
    else:
        return HttpResponseRedirect('/')
