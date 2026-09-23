from django.db import models
from django.contrib.auth.models import User
from blogs.models import Blog
# Create your models here.
class Activity(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True)
	types = [("C","Created"),("E", "Edited"),("D", "Deleted"),("S","Sent")]
	obj_types = [("P", "Post"),("T", "Topic"),("B", "Blog"),("U", "USD Citizenship request"),("E","Petition"),("S", "Style")]
	action_type = models.CharField(max_length=1, choices=types)
	action_obj = models.CharField(max_length=1, choices=obj_types)
	name = models.CharField(max_length=200)
	class Meta:
		verbose_name_plural="activities"
	def __str__(self):
		return f"{self.timestamp} - a {self.get_action_obj_display()} with name {self.name} was {self.get_action_type_display()}"

class Style(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	time_created=models.DateTimeField(auto_now_add=True)
	name=models.CharField(max_length=50)
	searchbar = models.BooleanField(default=False)
	topics = models.BooleanField(default=False)
	maintext = models.BooleanField(default=True)
	toptopics = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.user.username}'s style {self.name}"

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	time_created = models.DateTimeField(auto_now_add=True)
	bio = models.TextField(blank=True)
	location = models.CharField(max_length=50, blank=True)
	birthplace = models.CharField(max_length=50, blank=True)
	private = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)
	is_citizen = models.BooleanField(default=False)
	is_banned = models.BooleanField(default=False)
	style = models.ForeignKey(Style, on_delete=models.SET_NULL, blank=True, null=True)
	pic = models.ImageField(upload_to='profile_photos/', blank=True,default='profile_photos/default_picture.jpg')

	def __str__(self):
		return f"{self.user.username}'s profile"

class Writer(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	time_created=models.DateTimeField(auto_now_add=True)
	blog=models.ForeignKey(Blog, on_delete=models.CASCADE)
	class Meta:
		unique_together=[["user", "blog"]]

	def __str__(self):
		return f"{self.user.username} - Cowriter to blog {self.blog.name}"