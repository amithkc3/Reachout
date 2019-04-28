from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
import json
from django.views.decorators.csrf import csrf_exempt
from app1.models import *
from django.contrib.auth import authenticate


# Create your views here.------------------------------------
@csrf_exempt
def test(request):
	print(request.user)
	# u = User.objects.all()
	# print(str(u[1].profile.avatar))
	# return JsonResponse({'users':str(u[1].profile.avatar)})
	return HttpResponse("as")

def check(request):
	return HttpResponse("As")


def listUsers(request):
	users = User.objects.all()
	return render(request,'user.html',{'user':users})
	
def addUser(request):
	print(request.FILES)

	user_name = request.POST['user_name']
	password = request.POST['password']
	email = request.POST['email']
	avatar = request.FILES['avatar']

	user = User.objects.create(username=user_name,password=password,email=email)
	user.profile.avatar = avatar
	user.save()
	return HttpResponse("add")


def authenticateUser(request):
	user_name = request.POST['userName']
	password = request.POST['password']
	print(user_name,password)
	user = authenticate(username=user_name,password=password)		#It is hashed so less worries abt security

	if(user is not None):
		return HttpResponse("Yeaaaah")
	else:
		return HttpResponse("forgot password!!!")

@csrf_exempt
def add_article(request):
	print(request.POST)

	user = User.objects.get(username=request.POST['user_name'])
	desc = request.POST['desc']
	image = request.FILES['image']

	article = Article.objects.create(user=user,description=desc)
	article.image = image
	article.save()
	return HttpResponse("added article")

@csrf_exempt
def get_articles(request):
	articles = Article.objects.all()
	article_list = []
	for a in articles:
		temp={}
		temp['id'] = a.id
		temp['user'] = str(a.user)
		temp['desc'] = a.description
		temp['image'] = "/media/"+str(a.image)
		article_list.append(temp)

	return JsonResponse(article_list,safe=False)


@csrf_exempt
def add_event(request):
	
	could_not_add = []

	print(request)

	title = request.POST['title']
	description = request.POST['description']
	assigned_By = request.POST['assigned_by']
	datetime = request.POST['datetime']
	organizers = request.POST['organizers']

#changed assigned_by to assigned_By
	event = Event.objects.create(
		title=title,
		description=description,
		assigned_By=assigned_By,
		datetime=datetime)

	for organizer_name in organizers:
		try:
			organizer_object = User.objects.get(username=organizer_name)
			if(organizer_object):
				event.organizers.add(organizer)
				event.save()
		except:
			could_not_add.append(organizer_name)

	return JsonResponse({"could_not_add":could_not_add},safe=False)

def all_users(request):
	users = User.objects.all()
	print(users)
	user_list = []

	for user in users:
		temp={}
		temp['id']=user.profile.id
		temp['username'] = user.username
		temp['image'] = '/media/'+str(user.profile.avatar)

		user_list.append(temp)

	return JsonResponse(user_list,safe=False)

#get details of the investment for a specific event
def get_event_investment(request):
	event_id=request.POST['event_id']
	investments=Investment.objects.get(id=event_id)
	investment_list=[]
	for investment in investments:
		temp={}
		temp['investment_on']=investment.investment_on
		temp['amount']=investment.amount

		investment_list.append(temp)

	return JsonResponse(investment_list,safe=False)

#add investments to an event
def add_investment(request):
	# event_id=request.POST['event_id']
	# investments=request.POST['investments']
	
	# for investment in investments:
	# 	new_investment=Investment.objects.create(id=event_id,investment_on=investment.investment_on,amount=investment.amount)
	# 	new_investment.save()
	print(request.data)
	return HttpResponse("added investment")









