
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login , logout
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from .form import CommentForm
from .models import Hotel, Review, User, Contact, UserProfile, Amenity
from django.contrib.auth.decorators import login_required # type: ignore
import requests

def index(request):
    hotels = Hotel.objects.all()
    reviews = Review.objects.select_related('user').all().order_by('-created_at')[:10]  # Fetch recent comments

    # Initialize an empty context for search results
    context = {
        'hotels': hotels,
        'reviews': reviews,
        'query': None,
        'search_results': None,
        'no_results': False
    }

    # Handle the search form
    if request.method == 'GET' and 'query' in request.GET:
        query = request.GET.get('query')
        if query:
            # Search in hotel name or description, you can add more fields using Q objects
            search_results = Hotel.objects.filter(
                Q(name__icontains=query) | Q(location__icontains=query)
            )
            context['query'] = query
            context['search_results'] = search_results

            # Check if there are no results
            if not search_results.exists():
                context['no_results'] = True

    return render(request, 'hotels/index.html', context)

def login(request):
    if request.method =="POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  # Use auth_login to avoid conflict
            messages.success(request, 'Login suceessfull!')
            return redirect("index")  # Redirect to the index page after successful login
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")  # Redirect back to the login page if authentication fails

    return render(request, 'hotels/index.html')
    
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        ConfirmPassword = request.POST['ConfirmPassword']

        if password != ConfirmPassword:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
    
        user = User.objects.create_user(username, password)
        user.save()
        auth_login(request, user)
        messages.success(request, 'Your account has been created!')
        return HttpResponseRedirect(reverse("profile_update"))
    else:
        return render(request,"hotels/profile_update.html")

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout suceessfull!')
    return HttpResponseRedirect(reverse("index"))


def hotel_list(request):
    if request.method =='GET':
        if request.user.is_authenticated:
            hotels = recommend_hotels(request.user)
        else: 
            hotels = Hotel.objects.all()
    return render(request, 'hotels/room.html', {'hotels': hotels})


"""def hotel_list(request):
    city = request.GET.get('city', 'Berlin')
    checkin = request.GET.get('checkin', '2024-10-02')
    checkout = request.GET.get('checkout', '2024-10-04')
    
    url = "https://booking-com.p.rapidapi.com/v1/hotels"
    headers = {
        'x-rapidapi-key': "9b7a74b5a0msh5b47c621eec6e8ep15ed70jsn8e8675677d2f",
        'x-rapidapi-host': "booking-com.p.rapidapi.com"
    }
    
    params = {
        'locale': 'en-gb',
        'units': 'metric',
        'dest_id': city,
        'checkin_date': checkin,
        'checkout_date': checkout,
        'adults_number': '2',
        'room_number': '1',
        'filter_by_currency': 'USD',
        'order_by': 'price'
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        hotels = response.json().get('result', [])
    else:
        hotels = []
    print(hotels)  # This will print the API response to your console
    return render(request, 'hotels/room.html',{'hotels': hotels})"""

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    reviews = Review.objects.filter(hotel=hotel)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.hotel = hotel
            review.user = request.user  # Set the user
            review.rating = form.cleaned_data['rating']  # Save the rating
            review.save()
            return redirect('hotel_detail', hotel_id=hotel.id)
    else:
        form = CommentForm()

    context = {
        'hotel': hotel,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'hotels/hotel_detail.html', context)

#@login_required
def user_preferences(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Example preferences data from a form
        amenities = request.POST.getlist('amenities')  # assuming checkboxes
        location = request.POST.get('location')
        rating = request.POST.get('rating')

        # Update preferences as a JSON object
        profile.preferences = {
            'amenities': amenities,
            'location': location,
            'rating': rating
        }

        profile.save()
        return redirect('profile_update')

    return render(request, 'profile_update.html', {'profile': profile})

def show_preferences(request):
    profile = request.user.userprofile
    preferences = profile.preferences

    # Access specific preferences
    amenities = preferences.get('amenities', [])
    location = preferences.get('location', '')
    rating = preferences.get('rating', '')

    context = {
        'amenities': amenities,
        'location': location,
        'rating': rating,
    }

    return render(request, 'show_preferences.html', context)


def recommend_hotels(user):
    preferences = user.userprofile.preferences

    # Safely get the 'amenities' preference, defaulting to an empty string if not set
    amenities = preferences.get('amenities', '')

    # Only filter by amenities if they are provided
    if amenities:
        recommended_hotels = Hotel.objects.filter(amenities__icontains=amenities)
    else:
        recommended_hotels = Hotel.objects.all()  # Fallback to returning all hotels or a different logic

    return recommended_hotels

"""def recommendations(request):
    if request.method == 'GET':
        city = request.GET.get('city')  # Get the city from query parameters or user input
        checkin = request.GET.get('checkin')  # Check-in date from user input
        checkout = request.GET.get('checkout')  # Check-out date from user input

        # Replace 'YOUR_API_KEY' with your actual RapidAPI key
        url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
        headers = {
            'x-rapidapi-key': "9b7a74b5a0msh5b47c621eec6e8ep15ed70jsn8e8675677d2f",
            'x-rapidapi-host': "booking-com.p.rapidapi.com"
        }
        
        # Parameters for the hotel search request
        params = {
            'locale': 'en-gb',
            'units': 'metric',
            'dest_type': 'Ogun',  # Type of destination
            'dest_id': 'Ogun-State',  # City name or ID
            'checkin_date': 'checkin',  # Example: '2024-10-02'
            'checkout_date': 'checkout',  # Example: '2024-10-04'
            'adults_number': '2',  # Example: number of adults
            'room_number': '1',  # Number of rooms
            'filter_by_currency': 'USD',
            'order_by': 'price',  # Sort by price
            'include_adjacency': 'true'  # Option to include nearby hotels
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            hotels = response.json().get('result', [])  # Parse the JSON response for 'result'
        else:
            hotels = None  # Handle error or return an empty list

        context = {
            'hotels': hotels,  # Pass the hotel data to the template
            'city': city,
            'checkin': checkin,
            'checkout': checkout
        }

        return render(request, 'hotels/room.html', context)

    return render(request, 'hotels/room.html')

def recommendations(request):
    city = request.GET.get('city', 'default_city')
    checkin = request.GET.get('checkin', '2024-10-16')
    checkout = request.GET.get('checkout', '2024-10-23')

    # API request to get hotels data
    url = 'https://booking-com.p.rapidapi.com/v1/hotels/locations'
    headers = {
        'x-rapidapi-key': '9b7a74b5a0msh5b47c621eec6e8ep15ed70jsn8e8675677d2f',
        'x-rapidapi-host': 'booking-com.p.rapidapi.com'
    }
    params = {
        'locale': 'en-gb',
        'name': city,
        'checkin': checkin,
        'checkout': checkout
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        hotels = response.json()
    else:
        hotels = []

    # Pass the data to the template
    return render(request, 'hotels/room.html', {'hotels': hotels})
"""

def recommendations(request):
    city = request.GET.get('city', 'Nigria')
    user_preferences = {
        'amenities': ['wifi', 'pool'],
        'rating': 4
    }
    recommended_hotels = recommend_hotels(city, user_preferences)
    
    context = {
        'hotels': recommended_hotels
    }
    
    return render(request, 'hotels/recommendations.html', context)
 

def recommendations(request):
    if request.user.is_authenticated:
        hotels = recommend_hotels(request.user)
    else:
        hotels = Hotel.objects.all()  # Default to showing all hotels if not logged in
    return render(request, 'hotels/room.html', {'hotels': hotels})


def about(request):
    return render(request, 'hotels/about.html')

def service(request):
    return render(request, 'hotels/service.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
 
        print(f"Submitted Email: {email}")
        # Error messages
        errors = []
        if not name:
            errors.append('Name is required')
            
        if not email:
            errors.append('Email is required')
        else:
            try:
                validate_email(email)
                print("Email validation passed")
            except ValidationError:
                errors.append('Valid email is required')
                print("Email validation failed")

        if not subject:
            errors.append('Subject is required')

        if not message:
            errors.append('Message is required')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'hotels/contact.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message
            })
        
        # Fetch admin emails
        admin_emails = [user.email for user in User.objects.filter(is_superuser=True)]

        try:
            send_mail(
                subject,
                message,
                email,  # From email address
                admin_emails,
                fail_silently=False,  # Set to True to silently handle send_mail errors
            )
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')

            # Save contact form data to the Contact model
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}. Failed to send request.")

        return redirect('contact')
    else:
        return render(request, 'hotels/contact.html')
    
def profile_update(request):
    # Get or create the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        location = request.POST.get('location')
        amenities = request.POST.get('amenities')
        rating = request.POST.get('rating')

        # Get the list of amenities as a list of IDs
        amenities_ids = request.POST.getlist('amenities')

        # Handle profile picture upload
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES.get('profile_picture')

        # Update preferences as a JSON object
        profile.preferences = {
            'amenities': amenities,
            'location': location,
            'rating': rating
        }

        # Update the UserProfile instance
        profile.name = name
        profile.email = email
        profile.phone = phone
        profile.address = address
        profile.location = location
        profile.rating = rating

        # Update the many-to-many relationship for amenities
        amenities_objects = Amenity.objects.filter(id__in=amenities_ids)  # Query amenities by their IDs
        profile.amenities.set(amenities_objects)  # Use .set() to update the many-to-many field

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('index')

    # Define the context outside the POST block, to be used for both POST and GET
    context = {
        'profile': profile
    }

    # For GET requests, render the profile update form
    return render(request, 'hotels/profile_update.html', context)


def results(request):
    query = request.GET.get('query')
    if query:
        hotels = Hotel.objects.filter(Q(name__icontains=query)|Q(location__icontains=query))
    else:
        hotels = Hotel.objects.all()
    return render(request, 'hotels/results.html', {'hotels':hotels, 'query':query})