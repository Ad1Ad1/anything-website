from django import forms
from .models import Topic, Blog, Post, BlogTopicRelation, Vote, Reaction, PostReaction, Subscription
from users.models import User

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']
        labels = {"name": "Your topic's name..."}

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['name']
        labels = {'name': "Your blogs's name..."}

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields=[]
        labels={}

BlogTopicFormSet = forms.inlineformset_factory(Blog, BlogTopicRelation, fields=["topic", "percentage"], extra=0, can_delete=True)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["name", "text", "hidden"]
        labels = {"name": "Your post's name...", "text":"", "hidden":"Is this post a note?"}
        widgets = {"text": forms.Textarea(attrs={"cols": 80})}

class PostReactionForm(forms.ModelForm):
    class Meta:
        model = PostReaction
        fields = []
        labels = {}

class ReactionForm(forms.ModelForm):
    class Meta:
        model = Reaction
        fields = ["plain", "image"]
        labels = {"plain":"Your emoji's plaintext interpretation","image":"Your emoji's image interpretation"}

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = []
        labels = {}

class UserSearchForm(forms.Form):
    username = forms.CharField(
        label="Username to search for...",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter username...'})
    )

class TopicSearchForm(forms.Form):
    name = forms.CharField(
        label="Topic to search for...",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter topic name...'})
    )