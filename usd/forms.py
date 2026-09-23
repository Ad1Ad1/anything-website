from django import forms
from .models import USDCitizenRequest, Petition, VoteU

class UCRForm(forms.ModelForm):
    class Meta:
        model = USDCitizenRequest
        fields = ["q0answer", "q1answer","q2answer"]
        labels = {"q0answer": "Where are you from?", "q1answer":"Tell a little about yourself...","q2answer":"What do you aim to do in this community?"}

class UCRRejectionForm(forms.ModelForm):
    class Meta:
        model = USDCitizenRequest
        fields = ["due_to"]
        labels = {"due_to":"Due to what are you rejecting this user?"}
        widgets={"due_to":forms.Textarea(attrs={"cols": 60})}

class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ["text"]
        labels = {"text":"Idea Request text..."}

class VoteForm(forms.ModelForm):
    class Meta:
        model = VoteU
        fields=[]
        labels={}