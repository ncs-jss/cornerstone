from django.contrib import auth
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from . import models, forms, config

import datetime
import json


def redirect(request):
    if str(request.user.groups.all()[0]) in config.group[:2]:
        return JsonResponse({'response':'type 1 login'})
    else:
        return JsonResponse({'response':'type 2 login'})


def login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        if request.user.is_authenticated:
            return JsonResponse({'response':'Already logged in.'})
        else:
            username = data['username']
            password = data['password']
            if data['token'] == config.token[0]:
                user = auth.authenticate(username=username,
                                         password=password)
                if user and user.is_active:
                    auth.login(request,user)
                    return redirect(request)
                else:
                    return JsonResponse({'response': 'Invalid credentias'})
            else:
                return JsonResponse({'response':'Method not allowed'})
    return HttpResponseRedirect('/')


def logout(request):
    auth.logout(request)
    if request.method == 'POST':
        return JsonResponse({'response':'logged out'})
    return HttpResponseRedirect('/')


def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        if(request.method == 'POST'):
            if data['token'] == config.token[1]:
                form_a = forms.signup_form(data)
                form_b = forms.user_form(data)
                if(form_a.is_valid() and form_b.is_valid()):
                    user = form_b.save(commit = False)
                    pswd = form_b.cleaned_data['password']
                    grp = Group.objects.get(name=config.group[0])
                    user.set_password(pswd)
                    user.save()
                    user.groups.add(grp)
                    details = form_a.save(commit=False)
                    details.user = user
                    clg = form_a.cleaned_data['college']
                    contact = form_a.cleaned_data['contact']
                    details.save()
                    return JsonResponse({'response':'successfully created a user'})
                else:
                    context = {'response': [form_a.errors, form_b.errors]}
                    return(JsonResponse(context))
        return JsonResponse({'response': 'Method not allowed'})
    return HttpResponseRedirect('/')
