from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
import json
from django.views.decorators.csrf import csrf_exempt
from app1.models import *
from django.contrib.auth import authenticate
import datetime
import base64

def custom_authenticate(auth_info):
	print(auth_info)
	if(auth_info):
		username , password = base64.b64decode(auth_info).decode().split(':')
		res = authenticate(username=username,password=password)
		print(res)
		if(res is not None):
			return True
	else:
		return False

# Create your views here.------------------------------------
@csrf_exempt
def test(request):
	print(request.META)
	custom_authenticate(request.META['HTTP_AUTHORIZATION'])
	return HttpResponse(str(request.user))

def listUsers(request):
	users = User.objects.all()
	return render(request,'user.html',{'user':users})
	
def addUser(request):
	print(request.FILES)
	user_name = request.POST['user_name']
	password = request.POST['password']
	email = request.POST['email']
	avatar = request.FILES['avatar']

	user = User.objects.create_user(username=user_name,password=password,email=email)
	user.profile.avatar = avatar
	user.save()
	return HttpResponse("add")

@csrf_exempt
def authenticateUser(request):
	user_name = request.POST['username']
	password = request.POST['password']
	print(user_name,password)
	user = authenticate(username=user_name,password=password)		#It is hashed so less worries abt security
	print(user)
	if(user is not None):
		return HttpResponse("200")
	else:
		return HttpResponse("404")

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
#------------------------------------------------------------------------------------
#App side
#------------------------------------------------------------------------------------
@csrf_exempt
def login(request):
	print("login")
	auth_info = request.META['HTTP_AUTHORIZATION']
	username , password = base64.b64decode(auth_info).decode().split(':')
	res = authenticate(username=username,password=password)
	if(res is not None):
		u={}
		user = User.objects.get(username = username)
		u['username'] = user.username
		u['email'] = user.email
		u['avatar'] = '/media/' + str(user.profile.avatar)
		u['group'] = str(user.groups.all()[0])

		return JsonResponse(u,safe=False)
	else:
		return HttpResponse("404")



@csrf_exempt
def add_article(request):
	print(request.META)
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		print(request.POST)
		user = User.objects.get(username=request.POST['user_name'])
		desc = request.POST['desc']
		image = request.FILES['image']

		article = Article.objects.create(user=user,description=desc)
		article.image = image
		article.save()
		return HttpResponse("added article")
	else:
		return HttpResponse("Authentication error!!!")

@csrf_exempt
def delete_article(request):
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		try:
			article_id = request.POST['article_id']
			article = Article.objects.get(id=article_id)
			article.delete()
			print("tried")
			return HttpResponse(200)
			#all ok(200)
		except:
			print("and failed")
			return HttpResponse(500)
			#internel server error(500) couldnot delete
	else:
		return HttpResponse("Authentication error!!!")


@csrf_exempt
def get_articles(request):
	print("returned articles")
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		articles = Article.objects.all()
		article_list = []
		for a in articles:
			temp={}
			temp['article_id'] = a.id
			temp['username'] = str(a.user)
			# temp['user_profile'] = a.profile.avatar
			temp['profile_picture_url'] = "/media/"+str(User.objects.all()[1].profile.avatar)
			temp['desc'] = a.description
			temp['image'] = "/media/"+str(a.image)
			temp['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			article_list.append(temp)

		return JsonResponse(article_list,safe=False)
	else:
		return HttpResponse("Authentication error!!!")


@csrf_exempt
def add_event(request):
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		could_not_add = []
		print("--------------------------------------------------------")
		print(request.POST)

		print("--------------------------------------------------------")

		
		title = request.POST['title']
		description = request.POST['description']
		assigned_by = request.POST['assign_by']
		date = request.POST['date']
		e = request.POST['event_leader']
		event_lead = User.objects.get(username=e)

		datetime_obj = datetime.datetime.strptime(date,"%d-%m-%Y")

		selected_team = list(map(str,request.POST['selected_team'][1:-1].split(",")))
		selected_team_as_string = ','.join(selected_team)


		organizers = list(map(str,request.POST['organizers'][1:-1].split(',')))
		

		event = Event.objects.create(
			title=title,
			description=description,
			assigned_by=assigned_by,
			datetime = datetime_obj,
			selected_team = selected_team_as_string,
			event_leader = event_lead
			)
		event.save()

		#now adding Users in ManyToManyField organizers
		for organizer_name in organizers:
			organizer_object=None
			organizer_object = User.objects.get(username=str(organizer_name.strip()))
			#strip any spaces from username
			if(organizer_object is not None):
				event.organizers.add(organizer_object)
				event.save()
			else:
				could_not_add.append(organizer_name.strip())		
				return JsonResponse(406,safe=False)
		
		# print(could_not_add)
		# return JsonResponse({"could_not_add":could_not_add},safe=False)
		return JsonResponse(200,safe=False)

	else:
		return HttpResponse("Authentication error!!!")



@csrf_exempt
def get_my_events(request):

	print("my_events")
	print(request.POST)
	
	user_name = request.POST['user_name']

	events = User.objects.get(username=user_name).event_set.all()

	event_list_to_send = []
	for event in events:
		temp={}
		temp['event_id'] = event.id
		temp['event_leader'] = event.event_leader.username
		temp['event_title'] = event.title
		temp['description'] = event.description
		temp['date'] = event.datetime

		team_list=[]
		team = event.selected_team.split(',')
		for t in team:
			team_list.append(t.strip())

		temp['team_name'] = team_list
		temp['assigned_by'] = event.assigned_by
		temp['investment_amount'] = event.amount_invested
		temp['investment_return'] = event.amount_recieved
		organizers_list = []
		for organizer in event.organizers.all():
			temp2={}
			temp2['user_id'] = organizer.id
			temp2['username'] = organizer.username
			temp2['profile_picture_url'] = '/media/'+str(organizer.profile.avatar)

			organizers_list.append(temp2)

		temp['organizers'] = organizers_list

		event_list_to_send.append(temp)

	return JsonResponse(event_list_to_send,safe=False)

@csrf_exempt
def get_all_events(request):
	print(request.POST)
	events = Event.objects.all()

	event_list_to_send = []
	for event in events:
		temp={}
		temp['event_id'] = event.id
		temp['event_leader'] = event.event_leader.username
		temp['event_title'] = event.title
		temp['description'] = event.description
		temp['date'] = event.datetime

		team_list=[]
		team = event.selected_team.split(',')
		for t in team:
			team_list.append(t.strip())

		temp['team_name'] = team_list
		temp['assigned_by'] = event.assigned_by
		temp['investment_amount'] = event.amount_invested
		temp['investment_return'] = event.amount_recieved
		organizers_list = []
		for organizer in event.organizers.all():
			temp2={}
			temp2['user_id'] = organizer.id
			temp2['username'] = organizer.username
			temp2['profile_picture_url'] = '/media/'+str(organizer.profile.avatar)

			organizers_list.append(temp2)

		temp['organizers'] = organizers_list

		event_list_to_send.append(temp)
		print(event_list_to_send)

	return JsonResponse(event_list_to_send,safe=False)

@csrf_exempt
def get_event_details(request):
	event_id = request.POST['event_id']
	print("---------------Event-id = "+event_id)
	event = Event.objects.get(id=event_id)
	temp={}
	temp['event_id'] = event.id
	temp['event_leader'] = event.event_leader.username
	temp['event_title'] = event.title
	temp['description'] = event.description
	temp['date'] = event.datetime

	team_list=[]
	team = event.selected_team.split(',')
	for t in team:
		team_list.append(t.strip())

	temp['team_name'] = team_list
	temp['assigned_by'] = event.assigned_by
	temp['investment_amount'] = event.amount_invested
	temp['investment_return'] = event.amount_recieved
	organizers_list = []
	for organizer in event.organizers.all():
		temp2={}
		temp2['user_id'] = organizer.id
		temp2['username'] = organizer.username
		temp2['profile_picture_url'] = '/media/'+str(organizer.profile.avatar)
		organizers_list.append(temp2)

	temp['organizers'] = organizers_list

	return JsonResponse(temp,safe=False)

@csrf_exempt
def add_users_to_event(request):
	event_id = request.POST['event_id']

	organizers_to_add = list(map(str,request.POST['organizers_to_add'][1:-1].split(',')))

	try:
		event = Event.objects.get(id=event_id)
		for o in organizers_to_add:
			organizer = User.objects.get(username=str(o.strip()))
			if(organizer is not None):
				event.organizers.add(organizer)
				event.save()
		return HttpResponse(200)
	except:
		return HttpResponse(500)

@csrf_exempt
def remove_users_from_event(request):
	event_id = request.POST['event_id']
	organizers_to_remove = request.POST['organizers_to_remove']

	try:
		event = Event.objects.get(id=event_id)
		for o in organizers_to_remove:
			organizer = User.objects.get(username=o)
			event.organizers.remove(organizer)
			event.save()
		return HttpResponse(200)
	except:
		return HttpResponse(500)



#get details of the investment for a specific event
def get_event_investment(request):
	event_id=request.POST['event_id']
	investments=Investment.objects.filter(id=event_id)
	investment_list=[]
	for investment in investments:
		temp={}
		temp['investment_on']=investment.investment_on
		temp['amount']=investment.amount

		investment_list.append(temp)

	return JsonResponse(investment_list,safe=False)

#add investments to an event
def add_investment(request):
	event_id=request.POST['event_id']
	investments=request.POST['investments']
	
	i_to_delete = Investment.objects.filter(id=event_id)
	i_to_delete.delete()

	total_invested = 0

	for investment in investments:
		total_invested += int(investment.amount)
		new_investment=Investment.objects.create(id=event_id,investment_on=investment.investment_on,amount=investment.amount)
		new_investment.save()

	e=Event.objects.get(id=event_id)
	e.amount_invested = total_invested
	e.save()

	print(request.data)
	return HttpResponse("added investment")

@csrf_exempt
def delete_event(request):
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		try:
			print(request.POST)
			event_id = request.POST['event_id']
			event = Event.objects.get(id=event_id)
			event.delete()
			print("event deleted")
			return HttpResponse(200)
		except:
			print("and failed")
			return HttpResponse(500)
	else:
		return HttpResponse("Authentication error!!!")