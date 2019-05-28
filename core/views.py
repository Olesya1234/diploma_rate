import functools

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from core.models import Group


def index(request):
    if not request.user.profile or not request.user.is_authenticated:
        return redirect('/login')

    groups = Group.objects.all()

    if request.user.profile.role == 1:
        page_type = 'chairman'
    else:
        page_type = 'commission'

    if groups:
        return redirect('/cabinet/{}/group/{}'.format(page_type, groups.first().id))
    else:
        return render(request, '{}_student_table.html'.format(page_type))


def check_perm(role_str):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(*args, **kwargs):
            request = args[0]

            if not request.user.is_authenticated:
                return redirect('/login')

            role_d = {
                'chairman': 1,
                'commission': 2
            }

            if not request.user.profile:
                return logout_view(request)

            if role_d.get(role_str) != request.user.profile.role:
                raise PermissionDenied()

            return func(*args, **kwargs)

        return wrapper_repeat

    return decorator_repeat


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        page_next = request.POST.get("next", "/")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(page_next)
        else:
            return render(request, 'login.html', {"next": page_next, "invalid": True})

    else:
        page_next = request.GET.get("next", "/")
        return render(request, 'login.html', {"next": page_next})


def logout_view(request):
    logout(request)
    return redirect("/login")
