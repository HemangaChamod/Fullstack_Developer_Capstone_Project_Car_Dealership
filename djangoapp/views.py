# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from .models import CarMake, CarModel
from .populate import initiate
from django.http import JsonResponse
from .restapis import get_request, analyze_review_sentiments, post_review


from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
# from .populate import initiate

# Get an instance of a logger
logger = logging.getLogger(__name__)

@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('userName')
            password = data.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"userName": username, "status": "Authenticated"})
            else:
                return JsonResponse({"userName": username, "status": "Invalid credentials"})
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return JsonResponse({"status": "Error", "message": str(e)}, status=400)
    else:
        return JsonResponse({"status": "Invalid request method"}, status=405)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...

@csrf_exempt
def logout_request(request):
    if request.method == "POST":
        try:
            logout(request)
            return JsonResponse({"userName": ""})
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return JsonResponse({"status": "Error", "message": str(e)}, status=400)
    else:
        return JsonResponse({"status": "Invalid request method"}, status=405)

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...
@csrf_exempt
def registration(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data['userName']
            password = data['password']
            first_name = data['firstName']
            last_name = data['lastName']
            email = data['email']

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({"userName": username, "error": "Already Registered"})

            # Create new user
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )

            # Log in the new user
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return JsonResponse({"status": "Error", "message": str(e)}, status=400)
    else:
        return JsonResponse({"status": "Invalid request method"}, status=405)


# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
# ...



def get_cars(request):
    count = CarModel.objects.count()
    print("CarModel count:", count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })
    return JsonResponse({"CarModels": cars})


# Get all dealerships or dealerships by state
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


# Get details for a single dealer
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Get reviews for a dealer and analyze sentiment
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response.get('sentiment', 'neutral')
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

def add_review(request):
    if request.user.is_anonymous == False:
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status": 200, "message": "Review submitted successfully"})
        except:
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
