from django.contrib import auth
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from . import forms, models, config
from urllib import parse

import json
import re


def redirect(user):
    if str(user.groups.all()[0]) in config.group[:2]:
        return JsonResponse({'response': '200_1'})
    else:
        return JsonResponse({'response': '200_2'})


def is_admin(user):
    try:
        if str(user.groups.all()[0]) == config.group[2]:
            return True
    except BaseException:
        pass
    return False


def college_check(college):
    if bool(re.match(r'jss', college.lower())):
        return 250, 1   # Inside college Fee
    else:
        return 250, 0   # Other college Fee


def login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        if request.user.is_authenticated:
            return JsonResponse({'response': 'Already logged in.'})
        else:
            username = data['username']
            password = data['password']
            if data['token'] == config.token[0]:
                user = auth.authenticate(username=username,
                                         password=password)
                if user and user.is_active:
                    auth.login(request, user)
                    return redirect(request.user)
                else:
                    return JsonResponse({'response': 'Invalid credential'})
            else:
                return JsonResponse({'response': 'Method not allowed'})
    return HttpResponseRedirect(config.root)


def logout(request):
    auth.logout(request)
    if request.method == 'POST':
        return JsonResponse({'response': 'logged_out'})
    return HttpResponseRedirect(config.root)


def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        if(request.method == 'POST'):
            if data['token'] == config.token[1]:
                form_a = forms.signup_form(data)
                form_b = forms.user_form(data)
                if(form_a.is_valid() and form_b.is_valid()):
                    user = form_b.save(commit=False)
                    pswd = form_b.cleaned_data['password']
                    grp = Group.objects.get(name=config.group[0])
                    user.set_password(pswd)
                    user.save()
                    user.groups.add(grp)
                    details = form_a.save(commit=False)
                    details.user = user
                    details.save()
                    return JsonResponse({'response': 'user created'})
                else:
                    context = {'response': [form_a.errors, form_b.errors]}
                    return(JsonResponse(context))
        return JsonResponse({'response': 'Method not allowed'})
    return HttpResponseRedirect(config.root)


def online_reg(request):
    return render(request, "keystone/online.html", {})


def temp_submit(request, id):
    return render(request, "keystone/online_submit.html", {'zeal_id': id})


def dashboard(request):
    if request.user.is_authenticated:
        if str(request.user.groups.all()[0]) == config.group[3]:
            return HttpResponseRedirect('/zeal_admin')
        elif str(request.user.groups.all()[0]) == config.group[2]:
            return render(request, "keystone/dashboard.html", {})
    return HttpResponseRedirect(config.root)


def temp_reg(request, chk=False):
    try:
        if chk:
            response = request.body.decode(encoding='utf-8')
            response = dict(parse.parse_qsl(response))
            cnvrt = json.dumps(response)
            data = json.loads(cnvrt)
        else:
            data = json.loads(request.body.decode('utf-8'))
        if request.method == 'POST':
            if data['token'] in config.token[6:8]:
                data = forms.details_form(data)
                if data.is_valid():
                    details = data.save()
                    details.temp_id = "ZO_"+str(details.id)
                    details.save()
                    return JsonResponse({'response': '200', 'id': details.id})
                else:
                    context = {'errors': data.errors, 'response': '500'}
                    return JsonResponse(context)
    except BaseException:
        pass
    return JsonResponse({'response': 'Invalid'})


def generate(user, details):
    user = models.reg_admin.objects.get(user=user)
    fee, flag = college_check(details.college)
    user.amount_transferred += fee
    if flag:
        user.in_clg_reg += 1
    else:
        user.outside_clg_reg += 1
    reg = models.registeration.objects.create(fee=fee,
                                              created_by=user,
                                              details=details,
                                              created_at=timezone.now().date())
    reg.zeal_id = 'Zeal_'+str(reg.id)
    details.temp_status = False
    reg.save()
    details.save()
    user.save()
    return reg.zeal_id


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def register(request):
    if request.method == 'POST':
        data = request.POST
        if data['token'] == config.token[7]:
            stat = json.loads(temp_reg(request, True).content.decode('utf-8'))
            if stat['response'] == '200':
                details = models.details.objects.get(id=stat['id'])
                zeal_id = generate(request.user, details)
                context = {'zeal_id': zeal_id}
                return render(request, 'keystone/print.html', context)
            else:
                return render(request, 'keystone/register.html', stat)
        return HttpResponseRedirect(config.root)
    return render(request, 'keystone/register.html', {})


def search(request, chk=False):
    if request.method == 'POST':
        data = request.POST
        if data['token'] in config.token[8:10]:
            fields = data.keys()
            try:
                query = models.details.objects
                if 'id' in fields:
                    details = query.get(temp_id=data['id'])
                elif 'email' in fields:
                    details = query.get(email=data['email'])
                elif 'contact' in fields:
                    details = query.get(contact=data['contact'])
            except BaseException:
                context = {'response': '400'}
                if chk:
                    return 0, None
                return render(request, 'keystone/search.html', context)
            if details.temp_status:
                context = {'details': details}
                if chk:
                    return 1, context
                return render(request, 'keystone/search.html', context)
            zeal_id = models.registeration.objects.get(details=details)
            context = {'details': details, 'zeal_id': zeal_id.zeal_id}
            if chk:
                return 2, context
            return render(request, 'keystone/search.html', context)
        return HttpResponseRedirect(config.root)
    else:
        return render(request, 'keystone/search.html', {})


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def transfer(request):
    if request.method == 'POST':
        if request.POST['token'] == config.token[8]:
            fields = request.POST.keys()
            if 'tid' in fields:
                details = models.details.objects.get(id=request.POST['tid'])
                zeal_id = generate(request.user, details)
                context = {'zeal_id': zeal_id}
                return render(request, 'keystone/print.html', context)
            status, data = search(request, True)
            if not bool(status):
                context = {'response': '400'}
                return render(request, 'keystone/transfer.html', context)
            elif status == 2:
                context = {'response': '200', 'zeal_id': data['zeal_id']}
                return render(request, 'keystone/transfer.html', context)
            else:
                context = {'details': data['details']}
                return render(request, 'keystone/transfer.html', context)
    else:
        return render(request, 'keystone/transfer.html', {})


@user_passes_test(is_admin, login_url=config.root, redirect_field_name=None)
def printing(request):
    if request.method == 'POST':
        data = request.POST
        if data['token'] == config.token[10]:
            try:
                query = models.registeration.objects
                if data['id'] == '1':
                    ids = query.all()
                elif data['id'] == '2':
                    mn = int(data['min'])
                    mx = int(data['max'])
                    ids = query.filter(id__range=(mn, mx))
                else:
                    ids = query.filter(zeal_id=data['id'])
                context = {'zeal_ids': ids}
                return render(request, 'keystone/cards.html', context)
            except BaseException:
                pass
        context = {'errors': 'Invalid'}
        return render(request, 'keystone/print.html', context)
    return render(request, 'keystone/print.html', {})


def admin_dashboard(request):
    if request.user.is_authenticated:
        if str(request.user.groups.all()[0]) == config.group[3]:
            data = list(models.registeration.objects.values('created_at'))
            days = list()
            days_stat = list()
            admin_stat = list()
            for i in data:
                days.append(i['created_at'])
            days = set(days)
            amount = 0
            for day in days:
                if day is not None:
                    ids = models.registeration.objects.filter(created_at=day)
                    val = 0
                    for i in ids:
                        val += i.fee
                    amount += val
                    days_stat.append({'day': day, 'amount': val, 'ids': ids})
            admins = models.reg_admin.objects.all()
            for admin in admins:
                ids = models.registeration.objects.filter(created_by=admin)
                admin_stat.append({'admin': admin, 'ids': ids})
            context = {'daystat': days_stat,
                       'total': amount,
                       'adminstat': admin_stat}
            return render(request, 'keystone/admin_dash.html', context)
    return HttpResponseRedirect(config.root)
