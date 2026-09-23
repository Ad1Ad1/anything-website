from django.shortcuts import render,redirect

from users.models import Activity,Profile
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from .models import USDCitizenRequest, Petition, VoteU
from blogs.models import Post,Reaction
from blogs.views import process_comment_tree

from .forms import UCRForm, UCRRejectionForm,VoteForm,PetitionForm
Vote=VoteU
@login_required
def view_usd_page(request):
	req=USDCitizenRequest.objects.filter(user=request.user)
	requesty=None
	state=None
	news=[]
	profile=Profile.objects.filter(user=request.user).first()

	if profile.is_citizen:
		news=list(Post.objects.filter(news=True).order_by("date")[:5])
		news.reverse()
		for post in news:
			process_comment_tree(post, request)
	if req:
		req=req.order_by("-timestamp")
		requesty=req.first()
		state=requesty.state
	context={"news":news,"user":request.user,"requesty":requesty,'reactions':Reaction.objects.all(), "state":state, "profile":profile}
	return render(request,"usd/usd.html",context)
def news(request):
	req=USDCitizenRequest.objects.filter(user=request.user)
	news=[]
	profile=Profile.objects.filter(user=request.user).first()

	if profile.is_citizen:
		news=Post.objects.filter(news=True).order_by("-date")
		for post in news:
			process_comment_tree(post, request)
	else:
		raise Http404
	context={"news":news,"user":request.user, "profile":profile,'reactions':Reaction.objects.all()}
	return render(request,"usd/news.html",context)
@login_required
def new_request_citizenship(request):

	if request.method != "POST":
		form=UCRForm()
	else:
		form=UCRForm(data=request.POST)
		if form.is_valid():
			new_request_citizenship=form.save(commit=False)
			new_request_citizenship.user = request.user
			new_request_citizenship.state = "N"
			new_request_citizenship.save()
			Activity.objects.create(user=request.user, action_type="S", action_obj="U", name="USD citizenship request")
			return redirect('usd:view_usd_page')
	context = {'form': form}
	return render(request, 'usd/new_request_citizenship.html', context)
@login_required
def view_moderator_ucr(request):
	profile=Profile.objects.filter(user=request.user).first()
	if not profile.is_admin:
		raise Http404
	reqs=USDCitizenRequest.objects.order_by("-timestamp")
	processed=[]
	unprocessed=[]
	for req in reqs:
		if req.state=="N":
			unprocessed.append(req)
		else:
			processed.append(req)
	context={"profile":profile, "processed":processed, "unprocessed":unprocessed}
	return render(request, 'usd/moderator_ucr.html',context)

@login_required
def accept_citizenship_request(request,req):
	profile=Profile.objects.filter(user=request.user).first()
	obj=USDCitizenRequest.objects.get(pk=req)
	if not profile.is_admin:
		raise Http404
	obj.state="A"
	obj.save()
	pr2=Profile.objects.get(user=obj.user)
	pr2.is_citizen=True
	pr2.save()
	return redirect('usd:view_moderator_ucr')

@login_required
def reject_citizenship_request(request,req):
    if not request.user.profile.is_admin:
        raise Http404
    req=USDCitizenRequest.objects.get(pk=req)

    if request.method != "POST":
        form=UCRRejectionForm()
    else:
        form=UCRRejectionForm(data=request.POST)
        if form.is_valid():
            req.due_to=form.cleaned_data['due_to']
            req.state="R"
            req.save()
            return redirect('usd:view_moderator_ucr')

    context = {'form': form, "req":req}
    return render(request, 'usd/reject_request_citizenship.html', context)

@login_required
def revert_citizenship_request_action(request,req):
	profile=Profile.objects.filter(user=request.user).first()
	obj=USDCitizenRequest.objects.get(pk=req)
	if not profile.is_admin:
		raise Http404
	obj.state="N"
	obj.due_to=""
	obj.save()
	pr2=Profile.objects.get(user=obj.user)
	pr2.is_citizen=False
	pr2.save()
	return redirect('usd:view_moderator_ucr')
@login_required
def petitions(request):
	profile=Profile.objects.get(user=request.user)
	if not profile.is_citizen:
		raise Http404
	all_ps=Petition.objects.order_by("-date")
	for p in all_ps:
		rating=0
		for vote in p.voteu_set.all():
			if vote.user==request.user:
				p.user_vote=vote.vote
			if vote.vote:
				rating+=1
			else:
				rating-=1
		p.rating=rating
	context={"user":request.user, "petitions":all_ps, "profile":profile}
	return render(request,'usd/petitions.html',context)
@login_required
def vote(request, petition_id, vtype):
    if vtype=='False':
        vtype=False
    else:
        vtype=True
    petition=Petition.objects.get(id=petition_id)
    exists = Vote.objects.filter(user=request.user, petition=petition).exists()
    if exists:
        obj = Vote.objects.filter(user=request.user, petition=petition).first()
        if vtype==obj.vote:
            obj.delete()
        else:
            form=VoteForm(data=request.POST, instance=obj)
            obj2=form.save(commit=False)
            obj2.vote=vtype
            obj2.save()
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return HttpResponseRedirect(referer)
            return redirect('usd:petitions')
    else:
        form=VoteForm(request.POST)
        new_vote=form.save(commit=False)
        new_vote.vote=vtype
        new_vote.petition=petition
        new_vote.user=request.user
        new_vote.save()
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('usd:petitions')
@login_required
def new_petition(request):
    """Add a new petition."""
    if request.method != "POST":
        form=PetitionForm()
    else:
        form=PetitionForm(data=request.POST)
        if form.is_valid():
            new_p=form.save(commit=False)
            new_p.owner = request.user
            new_p.save()
            Activity.objects.create(user=request.user, action_type="C", action_obj="E", name=new_p.text[:50])
            return redirect('usd:petitions')
    context = {'form': form}
    return render(request, 'usd/new_petition.html', context)
@login_required
def delete_petition(request, petition_id):
    """Delete a petition."""
    profile=Profile.objects.get(user=request.user)
    if not profile.is_admin:
    	raise Http404
    petition = Petition.objects.get(pk=petition_id)
    petition.delete()
    return redirect('usd:petitions')