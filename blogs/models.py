from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Topic(models.Model):
    """Topic, which a user creates"""
    name = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, null=True,on_delete=models.SET_NULL)
    def __str__(self):
        """Returns model's text variant"""
        return self.name
class Blog(models.Model):
    """Blog, which a user creates"""
    topic = models.ManyToManyField(Topic, through='BlogTopicRelation')
    name = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        """Return model's text variant"""
        return self.name
class BlogTopicRelation(models.Model):
    """Relation of a blog and a topic"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    percentage = models.FloatField()
    class Meta:
        unique_together = [["topic", "blog"]]
    def __str__(self):
        """Returns model's text variant"""
        return f"{self.topic.name} - {self.blog.name}:{round(self.percentage,2)}%"
class Post(models.Model):
    """Post, which a user creates"""
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="subordinates")
    name = models.CharField(max_length=200)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.BooleanField()
    hidden = models.BooleanField()

    def clean(self):
        if self.post and self.blog and not self.news:
            raise ValidationError("Cannot use both blog and post for post owner, use one of them")
        elif not self.blog and not self.post and not self.news:
            raise ValidationError("Please, provide one field for post owner")
        elif (self.post or self.blog) and self.news:
            raise ValidationError("A news cannot belong to a blog or a post")

    def __str__(self):
        """Return model's text variant"""
        rating=0
        for vote in self.vote_set.all():
            if vote.vote:
                rating+=1
            else:
                rating-=1
        return self.name+f": {rating}"
class Media(models.Model):
    "A file linked to a post"
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    file_field=models.FileField(upload_to="post_media/")
    name = models.CharField(max_length=200)
    class Meta:
        verbose_name_plural="media"
    def __str__(self):
        """Return model's text variant"""
        return self.name

class Vote(models.Model):
    """Vote, with which user votes a post"""
    vote = models.BooleanField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        unique_together=[["post", "user"]]
    def __str__(self):
        return str(self.vote)
class Reaction(models.Model):
    """Reaction, with which user can react on a post"""
    plain = models.CharField(max_length=3, null=True, blank=True)
    image = models.ImageField(upload_to='post_reactions/', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    def clean(self):
        if self.image and self.plain:
            raise ValidationError("Cannot use both image and plain text for reaction, use one of them")
        elif not self.image and not self.plain:
            raise ValidationError("Please, provide one field for reaction")
    def __str__(self):
        return "Reaction placeholder"
class PostReaction(models.Model):
    """Reaction, with which user reacted on a post"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    class Meta:
        unique_together = [["post", "user", "reaction"]]
    def __str__(self):
        return "Added reaction placeholder"

class Subscription(models.Model):
    """Subscription, with which user subscribes to something"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    def clean(self):
        if self.blog and self.topic:
            raise ValidationError("A Subscription cannot be both to blog and topic")
        elif not self.blog and not self.topic:
            raise ValidationError("A Subscription must have a recieving side")
    class Meta:
        unique_together = [["user", "topic"],["user", "blog"]]
    def __str__(self):
        if self.topic:
            return f"Subscription of user {self.user} to topic {self.topic}"
        else:
            return f"Subscription of user {self.user} to blog {self.blog}"