from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
import uuid

# Create your models here.


class Write(models.Model):
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True)
    # For re-write (Share) functionality
    rewrite = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name='rewrites', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # content is allowed to be plan for rewrites
    content = RichTextField(null=True, blank=True)
    image = models.ImageField(blank=True, null=True)
    vote_rank = models.IntegerField(blank=True, null=True, default=0)
    comment_count = models.IntegerField(blank=True, null=True, default=0)
    share_count = models.IntegerField(blank=True, null=True, default=0)
    created = models.DateTimeField(auto_now_add=True)
    votes = models.ManyToManyField(
        User, related_name='write_user', blank=True, through='Vote')
    id = models.UUIDField(default=uuid.uuid4,  unique=True,
                          primary_key=True, editable=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        try:
            content = self.content[0:80]
        except Exception:
            content = 'Write: ' + str(self.rewrite.content[0:80])
        return content

    @property
    def shares(self):
        queryset = self.rewrite.all()
        return queryset

    @property
    def comments(self):
        # Still need a way to get all sub elements
        queryset = self.write_set.all()
        return queryset


class Vote(models.Model):

    CHOICES = (
        ('upvote', 'upvote'),
        ('downvote', 'downvote'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    write = models.ForeignKey(
        Write, on_delete=models.CASCADE, null=True, blank=True)
    value = models.CharField(max_length=20, choices=CHOICES)
    id = models.UUIDField(default=uuid.uuid4,  unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return str(self.user) + ' ' + str(self.value) + '"' + str(self.write) + '"'
