from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from blogs.models import Post, Blog, Topic, Subscription
from .models import Activity,Profile, Style
from .forms import ProfileForm, StyleForm
# Create your views here.
def register(request):
    """Register a new user."""
    if request.method != "POST":
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            nu = form.save()
            login(request, nu)
            return redirect("users:new_profile")
    context = {"form": form}
    return render(request, "registration/register.html", context)
def logged_out(request):
    """Log out"""
    context = {}
    return render(request, "registration/logged_out.html", context)

def profile(request, username, typer="infobio"):
    profile_=get_object_or_404(User, username=username)
    activities=[]
    subscriptions=[]
    styles=Style.objects.none()
    following_blogs=0
    following_topics=0
    total_posts = 0
    rating = 0
    profile_1=Profile.objects.filter(user=profile_).first()
    if typer=="activity":
        activities = Activity.objects.filter(user=profile_).order_by("-timestamp")
    elif typer=="following":
        subscriptions = Subscription.objects.filter(user=profile_)
        for subscription in subscriptions:
            if subscription.topic:
                subscription.TYPE="topic"
                following_topics+=1
            else:
                subscription.TYPE="blog"
                following_blogs+=1
    elif typer=="infobio":
        posts = Post.objects.filter(owner=profile_)
        for post in posts:
            total_posts+=1
            for vote in post.vote_set.all():
                if vote.vote:
                    rating+=1
                else:
                    rating-=1
    elif typer=="admin":
        if not request.user.profile.is_admin:
            raise Http404
    elif typer=="settings":
        styles=request.user.style_set.all()
    context={"user":request.user, "styles":styles, "profile":profile_, "profile_":profile_1,"type":typer, "contents":activities,"following":subscriptions,"fb":following_blogs,"ft":following_topics, "rating":rating, "totpos":total_posts}
    return render(request, "user_interface/profile.html", context)

@login_required
def new_style(request):
    """Add a new style."""
    if request.method != "POST":
        form=StyleForm()
    else:
        form=StyleForm(data=request.POST)
        if form.is_valid():
            new_style=form.save(commit=False)
            new_style.user = request.user
            new_style.save()
            Activity.objects.create(user=request.user, action_type="C", action_obj="S", name=new_style.name)
            return redirect('users:profile', request.user, 'settings')
    context = {'form': form, 'user':request.user}
    return render(request, 'styles/new_style.html', context)

@login_required
def edit_style(request, style_id):
    """Edit an existing style"""
    style=Style.objects.get(pk=style_id)
    if style.user != request.user and not request.user.is_superuser:
        raise Http404
    if request.method != "POST":
        form=StyleForm(instance=style)
    else:
        form=StyleForm(instance=style, data=request.POST)
        if form.is_valid():
            obj=form.save(commit=False)
            obj.save()
            Activity.objects.create(user=request.user, action_type="E", action_obj="S", name=obj.name)
            return redirect('users:profile', request.user, 'settings')
    context = {'form': form, 'style': style, 'user':request.user}
    return render(request, 'styles/edit_style.html', context)

@login_required
def delete_style(request, style_id):
    """Delete a style."""
    if request.method == "POST":
        style=Style.objects.get(pk=style_id)
        if style.user != request.user and not request.user.is_superuser:
            raise Http404
        Activity.objects.create(user=request.user, action_type="D", action_obj="S", name=style.name)
        style.delete()
        return redirect('users:profile', request.user, 'settings')

@login_required
def select_style(request, style_id):
    """Select a style."""
    if request.method == "POST":
        style=Style.objects.get(pk=style_id)
        if style.user != request.user and not request.user.is_superuser:
            raise Http404
        request.user.profile.style=style
        request.user.profile.save()
        return redirect('users:profile', request.user, 'settings')

@login_required
def new_profile(request):
    """Add a new profile."""
    profile=Profile.objects.filter(user=request.user).first()
    if request.method != "POST":
        form=ProfileForm(instance=profile)
    else:
        form=ProfileForm(instance=profile, data=request.POST)
        if form.is_valid():
            obj=form.save(commit=False)
            obj.is_admin=False
            obj.save()
            return redirect('blogs:index')
    context = {'form': form}
    return render(request, 'user_interface/new_profile.html', context)
@login_required
def edit_profile(request):
    """Edit a profile."""
    profile=Profile.objects.filter(user=request.user).first()
    if profile.user != request.user:
        raise Http404
    if request.method != "POST":
        form=ProfileForm(instance=profile)
    else:
        form=ProfileForm(instance=profile, data=request.POST,files=request.FILES)
        if form.is_valid():
            obj=form.save(commit=False)
            obj.save()
            return redirect('users:profile',username=request.user.username,typer="infobio")
    context = {'form': form,"user": request.user}
    return render(request, 'user_interface/edit_profile.html', context)

@login_required
def delete_user(request):
    request.user.delete()
    return redirect("blogs:index")

@login_required
def ban_user(request, target,tpe):
    target=User.objects.get(username=target)
    if target.is_superuser:
        raise Http404
    if tpe=="False":
        tpe=False
    else:
        tpe=True
    profile=request.user.profile
    if not profile.is_admin:
        raise Http404

    target.profile.is_banned=tpe
    target.profile.save()
    return redirect("users:profile",target.username,"admin")

@login_required
def promote_user(request, target):
    target=User.objects.get(username=target)
    if not request.user.is_superuser:
        raise Http404

    target.profile.is_admin=True
    target.profile.save()
    return redirect("users:profile",target.username,"admin")

@login_required
def demote_user(request, target):
    target=User.objects.get(username=target)
    if not request.user.is_superuser or target.is_superuser:
        raise Http404

    target.profile.is_admin=False
    target.profile.save()
    return redirect("users:profile",target.username,"admin")

def cookies(request):
    return render(request, 'info/cookies.html', {})

def banned(request):
    return render(request, 'user_interface/banned.html', {})