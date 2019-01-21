from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from . import models, forms
from keystone import config
from keystone.models import ca, ca_admin

import json


def is_admin(user):
    try:
        if str(user.groups.all()[0]) == config.group[1]:
            return True
    except BaseException:
        pass
    return False


@login_required(login_url=config.root)
def dashboard(request):
    tks = models.tasks.objects.filter(year=timezone.now().year)
    try:
        val = ca.objects.get(user=request.user).verified
    except BaseException:
        val = True
    context = {'tks': tks, 'check': val}
    return render(request, 'bedrock/dashboard.html', context)


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def members(request):
    mmbrs = ca.objects.filter(year=timezone.now().year)
    context = {'members': mmbrs}
    return render(request, 'bedrock/members.html', context)


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def member_delete(request, mem_id):
    mmbr = ca.objects.get(id=mem_id)
    mmbr.user.delete()
    mmbr.delete()
    return HttpResponseRedirect('/campusambassador/members')


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def member_verify(request, mem_id):
    mmbr = ca.objects.get(id=mem_id)
    mmbr.verified = not mmbr.verified
    mmbr.save()
    return HttpResponseRedirect('/campusambassador/members')


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def tasks_create(request):
    if request.method == 'POST':
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
                return HttpResponseRedirect('/campusambassador/tasks')
            else:
                context = {'response': form.errors}
                if data['token'] == config.token[2]:
                    return JsonResponse(context)
                return render(request, 'bedrock/tasks.html', context)
        else:
            return JsonResponse({'response': 'invalid token'})
    else:
        tks = models.tasks.objects.filter(year=timezone.now().year)
        context = {'tks': tks}
        return render(request, 'bedrock/tasks.html', context)


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def task_del(request, task_id):
    if str(request.user.groups.all()[0]) == config.group[1]:
        task = models.tasks.objects.get(id=task_id)
        task.delete()
        return HttpResponseRedirect('/campusambassador/tasks')


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def task_active(request, task_id):
        task = models.tasks.objects.get(id=task_id)
        task.is_active = not task.is_active
        task.save()
        return HttpResponseRedirect('/campusambassador/tasks')


@login_required(login_url=config.root)
def leaderboard(request):
    mmbrs = ca.objects.filter(verified=True, year=timezone.now().year)
    mmbrs = mmbrs.order_by('-score')
    context = {'mmbrs': mmbrs}
    return render(request, 'bedrock/leaderboard.html', context)


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def score_update(request, mem_id):
    if request.POST['token'] == config.token[4]:
        mmbr = ca.objects.get(id=mem_id)
        mmbr.score = request.POST['score']
        mmbr.save()
    return HttpResponseRedirect('/campusambassador/members')
