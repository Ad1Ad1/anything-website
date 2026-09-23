from django.contrib import admin
from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Blog, Topic, Post, BlogTopicRelation, Media, Vote, Reaction, PostReaction, Subscription

class BlogTopicFormSet(BaseInlineFormSet):
    """Validating the sum of Blog-topic relations"""
    def clean(self):
        super().clean()
        total_percentage = 0
        topics = False

        for f in self.forms:
            if not f.cleaned_data or f.cleaned_data.get('DELETE', False):
                continue
            
            total_percentage += f.cleaned_data.get('percentage', 0)
            topics = True

        if topics:
            if not (99.999 < total_percentage < 100.001):
                raise ValidationError(
                    f"Invalid sum of percentages: {round(total_percentage, 3)}%"
                )

class BlogTopicInline(admin.TabularInline):
    model = BlogTopicRelation
    formset = BlogTopicFormSet
    extra = 1

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    inlines = [BlogTopicInline]

admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Media)
admin.site.register(Vote)
admin.site.register(Reaction)
admin.site.register(PostReaction)
admin.site.register(Subscription)