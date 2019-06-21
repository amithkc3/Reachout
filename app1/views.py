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

@csrf_exempt	
def add_user(request):
	print(request.POST)
	user_name = request.POST['user_name'].strip()
	password = request.POST['password'].strip()
	email = request.POST['email'].strip()
	account = request.POST['account_type'].strip()
	#avatar = request.FILES['image']

	if len(User.objects.filter(username=user_name)) > 0:
		print("409 Conflict : username already exist...")
		return HttpResponse(409)

	user = User.objects.create_user(username=user_name, password=password, email=email)
	# user.set_password(password)
	# user.profile.avatar = avatar

	if account == "superuser":
		user.is_superuser = True
	elif account == "staff":
		user.is_staff = True

	user.save()
	return HttpResponse(200)

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
		
@csrf_exempt
def all_users(request):
	users = User.objects.all()
	print(users)
	user_list = []

	for user in users:
		temp={}
		temp['id']=user.profile.id
		temp['username'] = user.username
		temp['image'] = '/media/'+str(user.profile.avatar)
		if user.is_superuser:
			temp['account_type'] = "superuser"
		elif user.is_staff:
			temp['account_type'] = "staff"
		else:
			temp['account_type'] = "none"

		user_list.append(temp)
	print(user_list)
	return JsonResponse(user_list,safe=False)
#------------------------------------------------------------------------------------
#App side
#------------------------------------------------------------------------------------
@csrf_exempt
def login(request):
	print("login")
	auth_info = request.META['HTTP_AUTHORIZATION']
	username , password = base64.b64decode(auth_info).decode().split(':')
	print(username + ":" + password)
	res = authenticate(username=username,password=password)
	print(res)
	if(res is not None):
		u={}
		user = User.objects.get(username = username)
		u['username'] = user.username
		u['email'] = user.email
		u['avatar'] = '/media/' + str(user.profile.avatar)

		if user.is_superuser:
			u['account_type'] = "superuser"
		elif user.is_staff:
			u['account_type'] = "staff"
		else:
			u['account_type'] = "none"

		print(u)

		return JsonResponse(u,safe=False)
	else:
		return HttpResponse("500")



@csrf_exempt
def add_article(request):
	print(request.META)
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		print(request.POST)
		user = User.objects.get(username=request.POST['user_name'])
		desc = request.POST['desc']
		image = request.FILES['image']
		time = request.POST['time_stamp']

		time_to_save = datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S")

		article = Article.objects.create(user=user, description=desc, time_stamp=time_to_save)
		print(time_to_save)
		print('-------------------------------')
		article.image = image
		article.save()
		print(article.time_stamp)
		print('-----------------------')
		return HttpResponse(200)
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
			temp['profile_picture_url'] = "/media/"+str(User.objects.get(username=a.user).profile.avatar)
			temp['desc'] = a.description
			temp['image'] = "/media/"+str(a.image)
			#temp['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			temp['time_stamp'] = a.time_stamp.strftime("%Y-%m-%d %H:%M:%S")
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
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		print(request.POST)
		events = Event.objects.all()

		event_list_to_send = []
		for event in events:
			temp={}
			temp['event_id'] = event.id
			leader = event.event_leader
			if leader is None:
				temp['event_leader'] = "Not Available"
			else:
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
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
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
	else:
		return HttpResponse("Authentication error!!!")

@csrf_exempt
def add_users_to_event(request):
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
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
	else:
		return HttpResponse("Authentication error!!!")

@csrf_exempt
def remove_users_from_event(request):
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		print(request.POST)

		event_id = request.POST['event_id']

		organizers_to_remove = list(map(str,request.POST['organizers_to_remove'][1:-1].split(',')))

		try:
			event = Event.objects.get(id=event_id)
			for o in organizers_to_remove:
				organizer = User.objects.get(username=str(o.strip()))
				if(organizer is not None):
					event.organizers.remove(organizer)
					event.save()
			return HttpResponse(200)
		except:
			return HttpResponse(500)
	else:
		return HttpResponse("Authentication error!!!")

#get details of the investment for a specific event
@csrf_exempt
def get_event_investment(request):
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		event_id=request.POST['event_id']
		event = Event.objects.get(id=event_id)

		investments=Investment.objects.filter(event_id=event)

		responseData = {}

		responseData['amount_invested'] = event.amount_invested
		responseData['amount_recieved'] = event.amount_recieved

		investment_list=[]
		for investment in investments:
			temp={}
			temp['investment_on']=investment.investment_on
			temp['amount']=investment.amount

			investment_list.append(temp)

		responseData['investment_list'] = investment_list

		return JsonResponse(responseData,safe=False)
	else:
		return HttpResponse("Authentication error!!!")

@csrf_exempt
def add_investment(request):
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		try:
			print(request.POST)

			event_id = request.POST['event_id']
			reason_on = list(map(str,request.POST['investment_on'][1:-1].split(',')))
			amount_invested = list(map(str,request.POST['amount'][1:-1].split(',')))
			amount_recieved = request.POST['investment_on_return']

			event = Event.objects.get(id=event_id)

			Investment.objects.filter(event_id=event).delete()
			event.amount_invested = 0

			total_invested = 0
			length = len(reason_on)

			for x in range(0,length):
				print(reason_on[x])
				print(amount_invested[x])
				total_invested += int(amount_invested[x])
				new_investment = Investment.objects.create(event_id=event,investment_on=str(reason_on[x]),amount=str(amount_invested[x]))
				new_investment.save()

			event.amount_invested = total_invested
			event.amount_recieved = amount_recieved
			event.save()

			return HttpResponse(200)
		except:
			return HttpResponse(200)
	else:
		return HttpResponse("Authentication error!!!")

@csrf_exempt
def delete_event(request):
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		try:
			print(request.POST)
			event_id = request.POST['event_id']
			event = Event.objects.get(id=event_id)
			event.delete()

			# Delete all the investment data for the event
			Investment.objects.filter(event_id=event).delete()

			print("event deleted")
			return HttpResponse(200)
		except:
			print("and failed")
			return HttpResponse(500)
	else:
		return HttpResponse("Authentication error!!!")

@csrf_exempt
def get_my_articles(request):
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		try:
			user_name = request.POST['user_name']
			
			articles = User.objects.get(username=user_name).article_set.all()

			article_list = []
			for a in articles:
				temp={}
				temp['article_id'] = a.id
				temp['username'] = str(a.user)
				temp['profile_picture_url'] = "/media/" + str(User.objects.get(username=user_name).profile.avatar)
				temp['desc'] = a.description
				temp['image'] = "/media/" + str(a.image)
				temp['time_stamp'] = a.time_stamp.strftime("%Y-%m-%d %H:%M:%S")
				article_list.append(temp)

			return JsonResponse(article_list, safe=False)
		except:
			return HttpResponse(500)
	else:
		return HttpResponse("Authentication error!!!")

@csrf_exempt
def update_user_details(request):
	print(request.POST)
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		requested_username = request.POST['requested_user'].strip()
		user_name = request.POST['username'].strip()
		first_name = request.POST['first_name'].strip()
		last_name = request.POST['last_name'].strip()
		phone = request.POST['phone'].strip()
		email = request.POST['email'].strip()
		address = request.POST['address'].strip()
		bio = request.POST['bio'].strip()

		user = User.objects.get(username=requested_username)

		if len(User.objects.exclude(username=requested_username).filter(username=user_name)) > 0:
			print("409 Conflict : username already exist...")
			return HttpResponse(409)

		user.username = user_name
		user.first_name = first_name
		user.last_name = last_name
		user.email = email
		user.profile.phone = phone
		user.profile.location = address
		user.profile.bio = bio
		user.save()

		u={}
		u['username'] = user.username
		u['email'] = user.email
		u['avatar'] = '/media/' + str(user.profile.avatar)
		if user.is_superuser:
			u['account_type'] = "superuser"
		elif user.is_staff:
			u['account_type'] = "staff"
		else:
			u['account_type'] = "none"

		print(u)

		return JsonResponse(u,safe=False)
	else:
		return HttpResponse(401)

@csrf_exempt
def get_user_details(request):
	print(request.POST)
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		user_name = request.POST['username'].strip()
	
		user = User.objects.get(username=user_name)

		u={}
		u['username'] = user.username
		u['first_name'] = user.first_name
		u['last_name'] = user.last_name
		u['email'] = user.email
		u['phone'] = user.profile.phone
		u['address'] = user.profile.location
		u['bio'] = user.profile.bio
		u['avatar'] = '/media/' + str(user.profile.avatar)
		if user.is_superuser:
			u['account_type'] = "superuser"
		elif user.is_staff:
			u['account_type'] = "staff"
		else:
			u['account_type'] = "none"

		print(u)

		return JsonResponse(u,safe=False)
	else:
		return HttpResponse(401)

@csrf_exempt
def update_user_profile_picture(request):
	print(request.POST)
	if(custom_authenticate(request.META['HTTP_AUTHORIZATION'])):
		user_name = request.POST['user_name'].strip()
		image = request.FILES['image']
	
		user = User.objects.get(username=user_name)

		user.profile.avatar = image
		user.save()
		return HttpResponse(200)
	else:
		return HttpResponse(401)