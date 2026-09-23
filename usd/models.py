from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class USDCitizenRequest(models.Model):
	"""Ukrainian Scratch Department Citizen Request, which a user sends and moderator processes"""
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	types = [("A","Accepted"),("R", "Rejected"),("N", "Not processed yet")]
	state = models.CharField(max_length=1, choices=types)
	timestamp = models.DateTimeField(auto_now_add=True)
	due_to=models.TextField(blank=True)
	q0answer=models.CharField(max_length=50)
	q1answer=models.CharField(max_length=100)
	q2answer=models.CharField(max_length=20)
	def __str__(self):
		return f"{self.user}'s request for USD citizenship - {self.get_state_display()}"

class Petition(models.Model):
    """Petition, which a user creates"""
    text = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return model's text variant"""
        if len(self.text)>50:
        	return self.text[:50]+"..."
        else:
        	return self.text

class VoteU(models.Model):
    """Vote, with which user votes a petition"""
    vote = models.BooleanField()
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        unique_together=[["petition", "user"]]
    def __str__(self):
        return str(self.vote)