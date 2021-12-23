from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.models import User
from users.models import UserProfile
from .models import Write, Vote
from .utils import update_comment_counts, update_rewrite_counts


def update_write(sender, instance, created, **kwargs):
    # If a post is created & is a comment, them update the parent

    if created and instance.parent:
        update_comment_counts(instance.parent, 'add')

    if instance.rewrite:
        parent = instance.rewrite
        update_rewrite_counts(parent, 'add')


def delete_write_comments(sender, instance, **kwargs):
    # If a post is created & is a comment, them update the parent

    try:
        if instance.parent:
            update_comment_counts(instance.parent, 'delete')
    except Exception as e:
        print('write associated with comment was deleted')

    try:
        if instance.rewrite:
            update_rewrite_counts(instance.rewrite, 'delete')
    except Exception as e:
        print('rewrite associated with comment was deleted')


post_save.connect(update_write, sender=Write)
post_delete.connect(delete_write_comments, sender=Write)


def vote_updated(sender, instance, **kwargs):
    try:
        write = instance.write
        up_votes = len(write.votes.through.objects.filter(
            write=write, value='upvote'))
        down_votes = len(write.votes.through.objects.filter(
            write=write, value='downvote'))
        write.vote_rank = (up_votes - down_votes)
        write.save()
    except Exception as e:
        print('write the vote was associated with was already deleted')


post_save.connect(vote_updated, sender=Write)
post_delete.connect(vote_updated,  sender=Vote)
