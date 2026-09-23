from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import Topic, Blog, Post, Media, Vote, Reaction, PostReaction, Subscription
from users.models import Activity, Profile, Writer
from .forms import TopicForm, UserSearchForm, TopicSearchForm, BlogForm, BlogTopicFormSet, PostForm, VoteForm, ReactionForm, PostReactionForm, SubscriptionForm
from .sorters import radix_sort
from pathlib import Path
from os.path import splitext
from django.core.paginator import Paginator
import math
import sys
#Helper functions
def process_comment_tree(post, request):
    imgs=[".bin", ".jpg", ".jpeg", ".webp", ".png", ".gif"]
    vids=[".mp4", ".webm", ".ogg"]
    sounds=[".mp3", ".wav", ".m4a"]
    medias=post.media_set.all()
    medict={}
    for mediaa in medias:
        ext=Path(mediaa.file_field.name).suffix.lower()
        if ext in imgs:
            medict[mediaa]="img"
        elif ext in vids:
            medict[mediaa]="vid"
        elif ext in sounds:
            medict[mediaa]="snd"
        else:
            medict[mediaa]="dfl"
            mediaa.download_url = mediaa.file_field.storage.url(mediaa.file_field.name,parameters={'ResponseContentDisposition': 'attachment'})
    post.medias=medict
    rating=0
    for vote in post.vote_set.all():
        if vote.user==request.user:
            post.user_vote=vote.vote
        if vote.vote:
            rating+=1
        else:
            rating-=1
    post.rating=rating
    rs={}
    urs=[]
    for reaction in post.postreaction_set.all():
        rt=False
        try:
            rs[reaction.reaction]
            rt=True
        except:
            rt=False
        if rt:
            rs[reaction.reaction]+=1
        else:
            rs[reaction.reaction]=1
        if reaction.user==request.user:
            urs.append(reaction.reaction)
    post.reactions=rs
    post.user_reactions=urs
    post.subords=post.subordinates.all()
    for comment in post.subords:
        process_comment_tree(comment, request)
def convert_neg_frac(num):
    if num<0:
        return 1/(abs(num)+1)
    else:
        return num+1
def prepare_float(floating_ps):
    for num in range(len(floating_ps)):
        floating_ps[num]*=(10**6)
        floating_ps[num]=int(floating_ps[num])
    return floating_ps

# Create your views here.
def index(request):
    """Main page of blogs"""
    topics = Topic.objects.order_by('date')
    style=None
    if request.user.is_authenticated and request.user.profile.style!=None:
        style=request.user.profile.style
    raw_topics=[]
    raw_topic_nums=[]
    for topic in Topic.objects.all():
        raw_topics.append(topic)
        total_rating=0
        relations = topic.blogtopicrelation_set.order_by("-percentage")
        if len(relations.all())!=0:
            for relation in relations:
                blog=relation.blog
                for post in blog.post_set.all():
                    rating=0
                    for vote in post.vote_set.all():
                        if vote.vote:
                            rating+=1
                        else:
                            rating-=1
                    rating=convert_neg_frac(rating)
                    val=rating*relation.percentage
                    total_rating+=rating
        raw_topic_nums.append(total_rating)

    sorted_topic_nums, sort_indices=radix_sort(prepare_float(raw_topic_nums))
    sorted_topic_nums.reverse()
    sort_indices.reverse()
    res=[None]*len(raw_topics)
    for x in range(len(raw_topics)):
        res[x]=raw_topics[sort_indices[x]]

    top10res=res
    if len(top10res)>10:
        top10res=top10res[:10]

    results=Topic.objects.none()
    form=None
    if style and style.searchbar or True:
        form = TopicSearchForm(request.GET)

        if form.is_valid():
            query=form.cleaned_data.get("name")
            if query:
                results=Topic.objects.filter(name__icontains=query)

    if len(results)>10:
        results=results[:10]
    paginator = Paginator(res, 10) 
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {'page':page, 'form':form, 'searchresults':results, 'form':form, 'topics': res, "toptopics":top10res, 'topicsshow':style.topics if style else False, "searchbarshow":style.searchbar if style else False, "maintextshow":style.maintext if style else True, "toptopicsshow":style.toptopics if style else False}
    return render(request, 'blogs/index.html', context)

def topics(request):
    """Page of blogs that shows all topics"""
    topics = Topic.objects.order_by('date')
    paginator = Paginator(topics, 10) 
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {'page':page, 'topics': topics}
    return render(request, 'blogs/topics.html',context)

def topic(request, topic_id):
    """A page of blogs that shows a topic and blogs, related to it, ordered by percentage"""
    topic=Topic.objects.get(id=topic_id)
    relations = topic.blogtopicrelation_set.order_by("-percentage")
    subscriptions = topic.subscription_set.all()
    something_found = False
    for subscription in subscriptions:
        if subscription.user == request.user:
            something_found = True
            topic.user_subscription = subscription
    topic.user_subscribed = something_found
    paginator = Paginator(relations, 10) 
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {"page":page, "topic": topic, "relations": relations}
    return render(request, "blogs/topic.html", context)

def topic_top(request, topic_id):
    """A page of blogs that shows topic's posts most related and mostly favored in it"""
    topic=Topic.objects.get(id=topic_id)
    relations = topic.blogtopicrelation_set.order_by("-percentage")
    raw_posts=[]
    raw_post_nums=[]
    if len(relations.all())!=0:
        for relation in relations:
            blog=relation.blog
            for post in blog.post_set.all():
                raw_posts.append(post)
                rating=0
                for vote in post.vote_set.all():
                    if vote.vote:
                        rating+=1
                    else:
                        rating-=1
                rating=convert_neg_frac(rating)
                val=(rating*relation.percentage)/(((timezone.now()-post.date).total_seconds()/3600+2)**1.5)
                raw_post_nums.append(val)
        sorted_post_nums, sort_indices=radix_sort(prepare_float(raw_post_nums))
        sorted_post_nums.reverse()
        sort_indices.reverse()
        res=[None]*len(raw_posts)
        for x in range(len(raw_posts)):
            res[x]=raw_posts[sort_indices[x]]
        if len(res)>20:
            res=res[:20]
    else:
        res=[]
    for post in res:
        process_comment_tree(post, request)
    context = {'posts':res, 'reactions':Reaction.objects.all(), "topic":topic}
    return render(request, 'blogs/top.html', context)
@login_required
def user_top(request):
    """A page of blogs that shows all the top content from all the topics and blogs, to which user subscribed"""
    subscriptions = Subscription.objects.filter(user=request.user)
    swust = [] #Stuff, which user subscribed to(SwUSt)
    swust_types = []
    for subscription in subscriptions:
        if subscription.topic:
            swust.append(subscription.topic)
            swust_types.append("topic")
        else:
            swust.append(subscription.blog)
            swust_types.append("blog")
    posts_from_swust = []
    relations_from_swust=[]
    raw_post_nums=[]
    for x in range(len(swust)):
        OBJ = swust[x]
        if swust_types[x]=="topic":
            relations = OBJ.blogtopicrelation_set.all()
            for relation in relations:
                blog = relation.blog
                for post in blog.post_set.all():
                    if post not in posts_from_swust:
                        posts_from_swust.append(post)
                        relations_from_swust.append(relation.percentage)
                    else:
                        indx=posts_from_swust.index(post)
                        if relation.percentage > relations_from_swust[indx]:
                            relations_from_swust[indx] = relation.percentage
        elif swust_types[x]=="blog":
            for post in OBJ.post_set.all():
                if post not in posts_from_swust:
                    posts_from_swust.append(post)
                    relations_from_swust.append(100)
                else:
                    indx=posts_from_swust.index(post)
                    relations_from_swust[indx]=100

    if len(relations_from_swust)!=0:
        for post_indx in range(len(posts_from_swust)):
            post=posts_from_swust[post_indx]
            perc=relations_from_swust[post_indx]
            rating=0
            for vote in post.vote_set.all():
                if vote.vote:
                    rating+=1
                else:
                    rating-=1
            rating=convert_neg_frac(rating)
            val=(rating*perc)/(((timezone.now()-post.date).total_seconds()/3600+2)**1.5)
            raw_post_nums.append(val)
        sorted_post_nums, sort_indices=radix_sort(prepare_float(raw_post_nums))
        sorted_post_nums.reverse()
        sort_indices.reverse()
        res=[None]*len(posts_from_swust)
        for x in range(len(posts_from_swust)):
            res[x]=posts_from_swust[sort_indices[x]]
        if len(res)>20:
            res=res[:20]
    else:
        res=[]
    for post in res:
        process_comment_tree(post, request)
    context = {'posts':res, 'reactions':Reaction.objects.all()}
    return render(request, 'blogs/user_top.html', context)
def blog(request, blog_id):
    """A page of blogs that shows a blog and all its posts"""
    blog = Blog.objects.get(id=blog_id)
    relations = blog.blogtopicrelation_set.order_by("-percentage")
    for relation in relations.all():
        relation.percentage=round(relation.percentage,2)
    posts = blog.post_set.order_by("-date")
    for post in posts:
        process_comment_tree(post, request)
    subscriptions = blog.subscription_set.all()
    something_found = False
    for subscription in subscriptions:
        if subscription.user == request.user:
            something_found = True
            blog.user_subscription = subscription
    blog.user_subscribed = something_found
    writers=[writer.user for writer in blog.writer_set.all()]
    paginator = Paginator(posts, 10) 
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {'page':page, 'blog': blog, 'relations':relations, 'reactions':Reaction.objects.all(), "pagetype":"none", "writers":writers}
    return render(request, 'blogs/blog.html', context)
@login_required
def subscribers(request, stype, obj_id):
    """View subscribers for a blog/topic"""
    if stype=="blog":
        OBJ=Blog.objects.get(id=obj_id)
    elif stype=="topic":
        OBJ=Topic.objects.get(id=obj_id)
    subscriptions = OBJ.subscription_set.order_by("-date")
    context = {"object":OBJ, "type":stype, "subscribers":subscriptions}
    return render(request, 'blogs/subscribers.html', context)
@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != "POST":
        form=TopicForm()
    else:
        form=TopicForm(data=request.POST)
        if form.is_valid():
            new_topic=form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            Activity.objects.create(user=request.user, action_type="C", action_obj="T", name=new_topic.name)
            return redirect('blogs:topics')
    context = {'form': form}
    return render(request, 'blogs/new_topic.html', context)
@login_required
def edit_topic(request, topic_id):
    topic=Topic.objects.get(pk=topic_id)
    if topic.owner != request.user and not request.user.is_superuser:
        raise Http404
    if request.method != "POST":
        form=TopicForm(instance=topic)
    else:
        form=TopicForm(instance=topic, data=request.POST)
        if form.is_valid():
            obj=form.save(commit=False)
            obj.save()
            Activity.objects.create(user=request.user, action_type="E", action_obj="T", name=obj.name)
            return redirect('blogs:topics')
    context = {'form': form, 'topic': topic}
    return render(request, 'blogs/edit_topic.html', context)
@login_required
def delete_topic(request, topic_id):
    """Delete a topic."""
    if request.method == "POST":
        topic = Topic.objects.get(pk=topic_id)
        if topic.owner != request.user and not request.user.is_superuser:
            raise Http404
        for rel in topic.blogtopicrelation_set.all():
            blog=rel.blog
            for rel2 in blog.blogtopicrelation_set.all():
                if len(blog.blogtopicrelation_set.all())-1==0:
                    Activity.objects.create(user=request.user, action_type="D", action_obj="B", name=f"CASCADE DELETION: {blog.name}")
                    blog.delete()
                if not rel2.topic==topic:
                    rel2.percentage+=(rel.percentage/(len(blog.blogtopicrelation_set.all())-1))
                    rel2.save()
        Activity.objects.create(user=request.user, action_type="D", action_obj="T", name=topic.name)
        topic.delete()
        return redirect('blogs:topics')
@login_required
def new_blog(request):
    """Add a new blog"""
    if request.method == "POST":
        form = BlogForm(request.POST)
        formset = BlogTopicFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            ex=True
            perc=0
            for formy in formset.forms:
                if formy.cleaned_data.get('percentage')==None:
                    parc=0
                else:
                    parc=formy.cleaned_data.get('percentage')
                if not(formy.cleaned_data.get("DELETE")):
                    perc+=parc
            if not(perc>99.999 and perc<100.001):
                ex=False
                formset.non_form_errors().append("Sum of percentages isn't 100%, check your percentages, please!")
            if ex:
                bloggy = form.save(commit=False)
                bloggy.owner = request.user
                bloggy.everyone_access = False
                bloggy.save()
                formset.instance = bloggy
                formset.save()
                Activity.objects.create(user=request.user, action_type="C", action_obj="B", name=bloggy.name)
                return redirect("blogs:blog", blog_id=bloggy.pk)
    else:
        form = BlogForm()
        formset = BlogTopicFormSet()

    context = {'form': form, 'formset': formset}
    return render(request, 'blogs/new_blog.html', context)
@login_required
def edit_blog(request, blog_id):
    """Edit a blog"""
    blog=Blog.objects.get(pk=blog_id)
    if blog.owner != request.user and not request.user.is_superuser:
        raise Http404
    if request.method == "POST":
        form = BlogForm(instance=blog, data=request.POST)
        formset = BlogTopicFormSet(instance=blog, data=request.POST)

        if form.is_valid() and formset.is_valid():
            ex=True
            perc=0
            for formy in formset.forms:
                if formy.cleaned_data.get('percentage')==None:
                    parc=0
                else:
                    parc=formy.cleaned_data.get('percentage')
                if not(formy.cleaned_data.get("DELETE")):
                    perc+=parc
            if perc>99.999 and perc<100.001:
                bloggy = form.save()
                formset.instance = bloggy
                formset.save()
                Activity.objects.create(user=request.user, action_type="E", action_obj="B", name=bloggy.name)
                return redirect("blogs:blog", blog_id=bloggy.pk)
            else:
                formset.non_form_errors().append("Sum of percentages isn't 100%, check your percentages, please!")
    else:
        form = BlogForm(instance=blog)
        formset = BlogTopicFormSet(instance=blog)

    context = {'form': form, 'formset': formset, 'blog': blog}
    return render(request, 'blogs/edit_blog.html', context)
@login_required
def delete_blog(request, blog_id):
    """Delete a blog."""
    if request.method == "POST":
        blog=Blog.objects.get(pk=blog_id)
        if blog.owner != request.user and not request.user.is_superuser:
            raise Http404
        Activity.objects.create(user=request.user, action_type="D", action_obj="B", name=blog.name)
        blog.delete()
        return redirect('blogs:topics')

@login_required
def blog_settings(request, blog_id):
    """View and edit blog settings"""
    blog=Blog.objects.get(pk=blog_id)
    if blog.owner != request.user and not request.user.is_superuser:
        raise Http404
    context = {'blog': blog, "writers": blog.writer_set.all()}
    return render(request, 'blogs/blog_settings.html', context)

@login_required
def search_writers(request, blog_id):
    """Search for users to add as writers"""
    blog=Blog.objects.get(pk=blog_id)
    if blog.owner != request.user and not request.user.is_superuser:
        raise Http404
    form = UserSearchForm(request.GET)
    results=User.objects.none()

    if form.is_valid():
        query=form.cleaned_data.get("username")
        if query:
            results=User.objects.filter(username__icontains=query)

    context = {'form':form, 'blog':blog, "results":results, "writers": blog.writer_set.all(), "writers_users": [writer.user for writer in blog.writer_set.all()]}
    return render(request, 'blogs/add_writer.html', context)

@login_required
def add_writer(request, blog_id, user_id):
    """Add user as writer"""
    blog=Blog.objects.get(pk=blog_id)
    if blog.owner != request.user and not request.user.is_superuser:
        raise Http404
    user=User.objects.get(pk=user_id)
    Writer.objects.create(user=user, blog=blog)
    return redirect("blogs:blog_settings", blog_id)

@login_required
def delete_writer(request, blog_id, writer_id):
    """Delete user as writer"""
    writer=Writer.objects.get(pk=writer_id)
    blog=writer.blog
    if blog.owner != request.user and not request.user.is_superuser:
        raise Http404
    writer.delete()
    return redirect("blogs:blog_settings", blog.id)

@login_required
def promote_writer(request, blog_id, writer_id):
    """Promote writer to owner"""
    writer=Writer.objects.get(pk=writer_id)
    blog=writer.blog
    if blog.owner != request.user and not request.user.is_superuser:
        raise Http404
    blog.owner=writer.user
    blog.save()
    writer.delete()
    objs = Subscription.objects.filter(user=writer.user, blog=blog)
    exists = objs.exists()
    if exists:
        obj = objs.first()
        obj.delete()
    return redirect("blogs:blog", blog.id)

class Dummy:
    id=0
    def __init__(self,req_user):
        self.owner=req_user
@login_required
def new_post(request, blog_id, comment_id, is_news):
    """Add a new post for a blog"""
    if is_news=="False":
        is_news=False
    else:
        is_news=True
    if not is_news:
        if blog_id!=0:
            blog = Blog.objects.get(id=blog_id)
            comment=0
            blog_=blog
        else:
            comment=Post.objects.get(id=comment_id)
            blog_found=None
            curr_post=comment
            while not blog_found:
                blog_found=curr_post.blog
                if blog_found:
                    pass
                else:
                    curr_post=curr_post.post
            if curr_post.news:
                raise Http404
            blog=blog_found
            blog_=Dummy(comment.owner)
    else:
        comment=0
        blog=Dummy(request.user)
        blog_=Dummy(request.user)
    MediaFormSet = inlineformset_factory(
        Post, Media, fields=('name', 'file_field'), extra=0, can_delete=True
    )
    if not is_news:
        if blog.owner != request.user and comment_id==0 and request.user not in [writer.user for writer in blog.writer_set.all()]:
            raise Http404
    else:
        if Profile.objects.get(user=request.user).is_admin==False:
            raise Http404
    if request.method != "POST":
        form=PostForm()
        formset=MediaFormSet()
    else:
        form=PostForm(request.POST)
        formset = MediaFormSet(request.POST, request.FILES)
        if is_news:
            form.instance.news=True
        else:
            form.instance.news=False
            if comment_id != 0:
                form.instance.post = Post.objects.get(id=comment_id)
                form.instance.blog = None
            else:
                form.instance.blog = blog
                form.instance.post = None

        form.instance.owner = request.user
        if form.is_valid() and formset.is_valid():
            new_post=form.save()
            formset.instance=new_post
            formset.save()
            if not is_news:
                Activity.objects.create(user=request.user, action_type="C", action_obj="P", name=new_post.name)
                return redirect('blogs:blog', blog_id=blog.id)
            else:
                return redirect('usd:view_usd_page')
        else:
            print("FORM ERRORS:", form.errors)
            print("FORMSET ERRORS:", formset.errors)
    context= {"blog":blog, "form":form, "formset":formset, "post_id":comment_id, "blog_2":blog_, "comment":comment, "is_news":is_news, "is_news_str":str(is_news)}
    return render(request, "blogs/new_post.html", context)
@login_required
def edit_post(request, post_id):
    """Edit a post"""
    post = Post.objects.get(id=post_id)
    if not post.news:
        if post.owner != request.user and not request.user.is_superuser:
            raise Http404
        blog_found=None
        curr_post=post
        while not blog_found:
            blog_found=curr_post.blog
            curr_post=curr_post.post
        blog=blog_found
    else:
        if not Profile.objects.get(user=request.user).is_admin:
            raise Http404
        blog=None
    MediaFormSet = inlineformset_factory(
        Post, Media, fields=('name', 'file_field'), extra=0, can_delete=True
    )
    if request.method != "POST":
        form=PostForm(instance=post)
        formset = MediaFormSet(instance=post)
    else:
        form=PostForm(instance=post, data=request.POST)
        formset = MediaFormSet(instance=post, data=request.POST, files=request.FILES)
        if form.is_valid() and formset.is_valid():
            posty=form.save()
            formset.instance=posty
            formset.save()
            if not post.news:
                Activity.objects.create(user=request.user, action_type="E", action_obj="P", name=posty.name)
                return redirect('blogs:blog', blog_id=blog.id)
            else:
                return redirect('usd:view_usd_page')
    context= {"blog":blog, "form":form, "post":post, "formset":formset}
    return render(request, "blogs/edit_post.html", context)
@login_required
def delete_post(request, post_id):
    """Delete a post."""
    if request.method == "POST":
        post=Post.objects.get(pk=post_id)
        if not post.news:
            if post.owner != request.user and not request.user.is_superuser:
                raise Http404
            blog_found=None
            curr_post=post
            while not blog_found:
                blog_found=curr_post.blog
                curr_post=curr_post.post
            Activity.objects.create(user=request.user, action_type="D", action_obj="P", name=post.name)
        else:
            if not Profile.objects.get(user=request.user).is_admin:
                raise Http404
        post.delete()
        if not post.news:
            return redirect('blogs:blog', blog_id=blog_found.pk)
        else:
            return redirect('usd:view_usd_page')
@login_required
def vote(request, post_id, vtype):
    if vtype=='False':
        vtype=False
    else:
        vtype=True
    blog_found=None
    post=Post.objects.get(id=post_id)
    if not post.news:
        curr_post=post
        while not blog_found:
            blog_found=curr_post.blog
            curr_post=curr_post.post
    exists = Vote.objects.filter(user=request.user, post=post).exists()
    if exists:
        obj = Vote.objects.filter(user=request.user, post=post).first()
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
            return redirect('blogs:topics')
    else:
        form=VoteForm(request.POST)
        new_vote=form.save(commit=False)
        new_vote.vote=vtype
        new_vote.post=post
        new_vote.user=request.user
        new_vote.save()
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('blogs:topics')
@login_required
def react(request, post_id, reaction):
    post = Post.objects.get(id=post_id)
    filtered = Reaction.objects.filter(pk=reaction).first()
    filtered2 = PostReaction.objects.filter(post=post, user=request.user, reaction=filtered)
    exists = filtered2.exists()
    if exists:
        obj = filtered2.first()
        obj.delete()
    else:
        form = PostReactionForm(request.POST)
        new_preaction = form.save(commit=False)
        new_preaction.reaction=filtered
        new_preaction.user = request.user
        new_preaction.post = post
        new_preaction.save()
    blog_found=None
    curr_post=post
    while not blog_found:
        blog_found=curr_post.blog
        curr_post=curr_post.post
        if blog_found==None and curr_post==None:
            break
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return redirect('blogs:blog', blog_id=blog_found.id)
@login_required
def new_reaction(request):
    """Add a new reaction."""
    redirect_to = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/topics/'
    if request.method!="POST":
        form=ReactionForm()
    else:
        form=ReactionForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_reaction=form.save(commit=False)
            new_reaction.owner=request.user
            new_reaction.save()
            return redirect(redirect_to)
    context = {"form":form, "blog":blog, "next_url":redirect_to}
    return render(request, "blogs/new_reaction.html", context)
REFRR=None
@login_required
def edit_reaction(request, react_id):
    """Edit a reaction"""
    global REFRR
    react=Reaction.objects.get(id=react_id)
    redirect_to = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/topics/'
    if react.owner != request.user:
        raise Http404
    if request.method!="POST":
        form=ReactionForm(instance=react)
    else:
        form=ReactionForm(instance=react, data=request.POST, files=request.FILES)
        if form.is_valid():
            reaction=form.save(commit=False)
            reaction.owner=request.user
            reaction.save()
            return redirect(redirect_to)
    REFRR=redirect_to
    context = {"form":form, "blog":blog, "reaction":react,"next_url":redirect_to}
    return render(request, "blogs/edit_reaction.html", context)
@login_required
def delete_reaction(request, react_id):
    """Delete a reaction."""
    global REFRR
    if request.method == "POST":
        reaction=Reaction.objects.get(pk=react_id)
        if reaction.owner != request.user:
            raise Http404
        reaction.delete()
        if REFRR:
            return HttpResponseRedirect(REFRR)
        return redirect('blogs:topics')
@login_required
def subscribe(request, obj_id, obj_type, stype):
    if stype=="False":
        stype=False
    else:
        stype=True
    if obj_type=="blog":
        blog = Blog.objects.get(id=obj_id)
        objs = Subscription.objects.filter(user=request.user, blog=blog)
        exists = objs.exists()
    else:
        topic = Topic.objects.get(id=obj_id)
        objs = Subscription.objects.filter(user=request.user, topic=topic)
        exists = objs.exists()
    if exists:
        obj = objs.first()
        obj.delete()
    else:
        form=SubscriptionForm(request.POST)
        form.instance.user = request.user
        if obj_type=="blog":
            form.instance.blog=blog
        else:
            form.instance.topic=topic
        form.save()
    if obj_type=="blog":
        return redirect('blogs:blog', blog_id=blog.id)
    else:
        return redirect('blogs:topic', topic_id=topic.id)