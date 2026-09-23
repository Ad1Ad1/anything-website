from django import forms
from .models import Profile, Style

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birthplace', 'pic','private']
        labels = {"bio": "Your bio...", "location":"Your current location(NOT required)", "birthplace":"Your birth place(NOT required)", "pic":"Your profile picture(NOT required)", "private":"Make your profile private?(Hide activity logs and what you are following to average users)"}

class StyleForm(forms.ModelForm):
    class Meta:
        model = Style
        fields = ['name', 'searchbar', 'topics', 'toptopics', 'maintext']
        labels = {"name": "Your style's name...", "searchbar": "Show searchbar on main page?", "topics":"Show topics on main page?", "toptopics":"Show top topics on main page?", "maintext":"Show main text of main page?"}
