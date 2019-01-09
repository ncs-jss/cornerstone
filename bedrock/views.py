from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import models
from keystone import config
from keystone.models import ca

import datetime


def dashboard(request):
    if request.user.is_authenticated:
        tks = models.tasks.objects.filter(year=datetime.date.today().year)
        try:
            val = ca.objects.get(user=request.user).verified
        except BaseException:
            val = True
        context = {'tks': tks, 'check': val}
        return render(request, 'bedrock/dashboard.html', context)
    else:
        return HttpResponseRedirect(config.root)


def members(request):
    try:
        if str(request.user.groups.all()[0]) == config.group[1]:
            mmbrs = ca.objects.filter(year=datetime.date.today().year)
            context = {'members': mmbrs}
            return render(request, 'bedrock/members.html', context)
    except BaseException:
        pass
    return HttpResponseRedirect(config.root)


def member_delete(request, mem_id):
    try:
        if str(request.user.groups.all()[0]) == config.group[1]:
            mmbr = ca.objects.get(id=mem_id)
            mmbr.user.delete()
            mmbr.delete()
            return HttpResponseRedirect('/campusambassador/members')
    except BaseException:
        pass
    return HttpResponseRedirect(config.root)


def member_verify(request, mem_id):
    try:
        if str(request.user.groups.all()[0]) == config.group[1]:
            mmbr = ca.objects.get(id=mem_id)
            mmbr.verified = True
            mmbr.save()
            return HttpResponseRedirect('/campusambassador/members')
    except BaseException:
        pass
    return HttpResponseRedirect(config.root)
