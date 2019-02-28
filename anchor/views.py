from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import Group, User
from keystone import config

import requests
import json


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/events/reg_dashboard')
    if request.method == 'POST':
        if request.POST['token'] == config.token[11]:
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
                        grp = Group.objects.get(name=config.group[3])
                        user.groups.add(grp)
                        user.save()
                    auth.login(request, user)
                    return HttpResponseRedirect('/events/reg_dashboard')
                else:
                    return HttpResponseRedirect(config.root)
            else:
                context = {'error': 'Invalid Credentials'}
                return render(request, 'anchor/login.html', context)
        else:
            return HttpResponseRedirect(config.root)
    else:
        return render(request, 'anchor/login.html', {})
