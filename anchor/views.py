from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User
from django.utils import timezone
from keystone import config
from keystone.models import registeration
from . import models

import requests
import json


def is_admin(user):
    try:
        if str(user.groups.all()[0]) == config.group[4]:
            return True
    except BaseException:
        pass
    return False


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/events/ev_dashboard')
    if request.method == 'POST':
        url = config.login
        username = request.POST['username']
        password = request.POST['password']
        data = {"username": username,
                "password": password}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            data = json.loads(response.text)
            first_name = data['first_name']
            if data['group'] == 'others':
                try:
                    user = User.objects.get(username=username)
                    user = auth.authenticate(username=username,
                                             password=config.auth)
                except BaseException:
                    user = User.objects.create_user(username=username,
                                                    password=config.auth,
                                                    first_name=first_name)
                    grp = Group.objects.get(name=config.group[4])
                    user.groups.add(grp)
                    user.save()
                auth.login(request, user)
                return HttpResponseRedirect('/events/ev_dashboard')
            else:
                return HttpResponseRedirect(config.root)
        else:
            context = {'error': 'Invalid Credentials'}
            return render(request, 'anchor/login.html', context)
    else:
        return render(request, 'anchor/login.html', {})


def ev_register(request, evid):
    if request.method == 'POST':
        z_id = request.POST['id']
        contact = request.POST['contact']
        try:
            user = registeration.objects.get(zeal_id=z_id)
        except BaseException:
            context = {'response': '404', 'id': evid}
            return render(request, 'anchor/register_ev.html', context)
        if user.details.contact == contact:
            event = models.events.objects.get(api_ref_id=evid)
            try:
                context = models.ev_registration.objects.get(zeal_id=user,
                                                             event=event)
                context = {'response': 'False', 'id': evid}
                return render(request, 'anchor/register_ev.html', context)
            except BaseException:
                pass
            models.ev_registration.objects.create(event=event,
                                                  zeal_id=user,
                                                  reg_at=timezone.now())
            context = {'response': 'True', 'id': evid}
            return render(request, 'anchor/register_ev.html', context)
        else:
            context = {'response': '500', 'id': evid}
            return render(request, 'anchor/register_ev.html', context)
    event = models.events.objects.get(api_ref_id=evid)
    context = {'title': event.title, 'id': event.api_ref_id}
    return render(request, 'anchor/register_ev.html', context)


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def ev_dashboard(request):
    events = list()
    user = User.objects.get(id=request.user.id)
    instances = models.events.objects.filter(creator=user)
    for instance in instances:
        count = len(models.ev_registration.objects.filter(event=instance))
        data = {'title': instance.title,
                'id': instance.api_ref_id,
                'count': count}
        events.append(data)
    context = {'events': events}
    return render(request, 'anchor/dashboard_ev.html', context)


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def details(request):
    events = list()
    user = User.objects.get(id=request.user.id)
    instances = models.events.objects.filter(creator=user)
    for instance in instances:
        reg = models.ev_registration.objects.filter(event=instance)
        context = {'title': instance.title,
                   'registrations': reg}
        events.append(context)
    context = {'events': events}
    return render(request, 'anchor/details.html', context)
