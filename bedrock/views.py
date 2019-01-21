from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from . import models, forms
from keystone import config
from keystone.models import ca, ca_admin

import json
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
            mmbr.verified = not mmbr.verified
            mmbr.save()
            return HttpResponseRedirect('/campusambassador/members')
    except BaseException:
        pass
    return HttpResponseRedirect(config.root)


def tasks_create(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            if str(request.user.groups.all()[0]) == config.group[1]:
                try:
                    data = json.loads(request.body.decode('utf-8'))
                except BaseException:
                    data = request.POST
                form = forms.tasks_add(data)
                if data['token'] in config.token[2:4]:
                    if form.is_valid():
                        task = form.save(commit=False)
                        user = ca_admin.objects.get(user=request.user.id)
                        task.posted_by = user
                        task.save()
                        if data['token'] == config.token[2]:
                            return JsonResponse({'response': 'success'})
                        return HttpResponseRedirect(config.root)
                    else:
                        context = {'response': form.errors}
                        if data['token'] == config.token[2]:
                            return JsonResponse(context)
                        return render(request, 'bedrock/tasks.html', context)
                else:
                    return JsonResponse({'response': 'invalid token'})
        except BaseException:
            pass
        return JsonResponse({'response': 'method not allowed'})
    else:
        tks = models.tasks.objects.filter(year=datetime.date.today().year)
        context = {'tks': tks}
        return render(request, 'bedrock/tasks.html', context)


def task_del(request, task_id):
    try:
        if str(request.user.groups.all()[0]) == config.group[1]:
            task = models.tasks.objects.get(id=task_id)
            task.delete()
            return HttpResponseRedirect('/campusambassador/tasks')
    except BaseException:
        pass
    return HttpResponseRedirect('/campusambassador/tasks')
