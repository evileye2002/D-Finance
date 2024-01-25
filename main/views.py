from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .forms import SignUpForm, SignInForm, PostIncomeForm


# Create your views here.
def test(req):
    return render(req, "test-up.html")


@login_required(login_url="sign-in")
def index(req):
    return render(req, "index.html")


def sign_in(req):
    if req.user.is_authenticated:
        return redirect("index")

    form = SignInForm()

    if req.method == "POST":
        form = SignInForm(req, data=req.POST)
        if form.is_valid():
            username = req.POST.get("username")
            password = req.POST.get("password")
            remember = req.POST.get("remember")
            user = authenticate(req, username=username, password=password)

            if user is not None:
                if remember == "on":
                    req.session.set_expiry(60 * 60 * 24 * 30)  # 1 month
                else:
                    req.session.set_expiry(60 * 60 * 24)  # 1 day

                login(req, user)
                return redirect("index")

    print(form.errors.as_json())
    ctx = {"signInForm": form, "errors": form.non_field_errors()}

    return render(req, "sign-in.html", ctx)


def sign_up(req):
    if req.user.is_authenticated:
        return redirect("index")

    form = SignUpForm()

    if req.method == "POST":
        form = SignUpForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("sign-in")

    print(form.__getitem__("password2").errors.as_json())
    ctx = {"signUpForm": form}

    return render(req, "sign-up.html", ctx)


def sign_out(req):
    logout(req)
    return redirect("sign-in")


@login_required(login_url="sign-in")
def income(req):
    form = PostIncomeForm()

    if req.method == "POST":
        reqPost = req.POST.copy()
        date = req.POST.get("date")
        time = req.POST.get("time")
        if date and time:
            combined_datetime = datetime.fromisoformat(date + ":" + time)
            reqPost.update({"datetime": combined_datetime})

        form = PostIncomeForm(reqPost)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = req.user
            post.save()
            return redirect("income")

    print(req.POST)
    print(form.errors)
    ctx = {"postIncomeDialog": form}

    return render(req, "income.html", ctx)
