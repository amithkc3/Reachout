from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def user_directory_path(instance, filename):
	print(instance)
	return 'static/images/avatars/user_{0}/{1}'.format(instance.id, filename)

def article_images(instance,filename):
	return 'static/images/articles/article_{0}/{1}'.format(instance.id,filename)

#extending user model
class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to=user_directory_path,null=True,blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
    	Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Article(models.Model):
	id = models.AutoField(primary_key=True),
	user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
	description = models.TextField()
	image = models.ImageField(upload_to=article_images,null=True,blank=True)


class Event(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=100)
	description = models.TextField()
	assiged_By = models.CharField(max_length=100)
	datetime = models.DateTimeField()
	organizers = models.ManyToManyField(User)
