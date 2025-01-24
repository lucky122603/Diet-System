from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
import requests
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'index.html')
            
def signup(request):
    if request.method == 'POST':
        fname = request.POST.get('fullName')
        uname = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('confirmPassword')

        if password != cpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        my_user = User.objects.create_user(uname, email, password)
        my_user.save()

        # Create a UserProfile for the new user
        profile = UserProfile(user=my_user, full_name=fname, email=email)
        profile.save()

        messages.success(request, "User created successfully!")
        return redirect('signin')

    return render(request, 'signup.html')


from django.contrib.auth import authenticate, login

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using username (or email) and password
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)  # Log the user in
            return redirect('home')  # Redirect to home page
            
        else:
              # Show error message
            return HttpResponse("Invalid Credentials")
            
    
    return render(request, 'signin.html')



@login_required
def home(request):
    user = request.user  # Get the currently logged-in user
    
    # Get the profile associated with the user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Pass the profile to the template
    context = {'profile': profile}
    return render(request, 'home.html', context)

from django.contrib.auth.models import User
from .models import UserProfile

from django.contrib.auth.models import User
from .models import UserProfile

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def edit(request):
    user = request.user  # Get the currently logged-in user

    # Check if the user exists in the database
    try:
        profile, created = UserProfile.objects.get_or_create(user=user)
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('signin')  # Redirect to signin if profile not found

    if request.method == "POST":
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Update UserProfile details
        profile.full_name = full_name
        profile.email = email
        profile.save()

        # Update User model's details (if needed)
        user.email = email
        if password:  # Update password if provided
            user.set_password(password)
        user.save()

        # Re-login the user after password change
        if password:
            from django.contrib.auth import login
            login(request, user)

        messages.success(request, "Profile updated successfully!")
        return redirect('home')  # Redirect to home after success

    context = {'profile': profile}
    return render(request, 'edit.html', context)

def userinfo(request):
    if request.method == 'GET':
        return render(request, 'userinfo.html')
    

def calculate_tdee(age, height, weight, gender, activity_level):
    # BMR Calculation for Male
    if gender == 'male':
        bmr = 66 + (13.75 * weight) + (5 * height) - (6.75 * age)
    # BMR Calculation for Female
    else:
        bmr = 655 + (9.56 * weight) + (1.85 * height) - (4.68 * age)

    # TDEE Calculation based on activity level
    if activity_level == '1':
        tdee = bmr * 1.2  # Sedentary
    elif activity_level == '2':
        tdee = bmr * 1.55  # Active
    else:
        tdee = bmr * 1.9  # Very Active
    
    return tdee

def user_info(request):
    if request.method == 'GET':
        # Extract form data from GET request
        age = int(request.GET.get('age'))
        height = int(request.GET.get('height'))
        weight = int(request.GET.get('weight'))
        gender = request.GET.get('gender')
        activity_level = request.GET.get('activity')
        
        # Calculate TDEE (Total Daily Energy Expenditure)
        tdee = calculate_tdee(age, height, weight, gender, activity_level)
        
        # Example: Nutrient breakdown based on TDEE (just an approximation)
        # Assuming 40% Carbs, 30% Protein, 30% Fats
        carbs = tdee * 0.4 / 4  # 1g of Carbs = 4 kcal
        proteins = tdee * 0.3 / 4  # 1g of Protein = 4 kcal
        fats = tdee * 0.3 / 9  # 1g of Fat = 9 kcal
        
        # Pass the values to the template
        context = {
            'carbs': round(carbs),
            'proteins': round(proteins),
            'fats': round(fats),
        }

        return render(request, 'mealplan.html', context)

    return HttpResponse("Invalid request method.")

# Mealplan View
import requests
from .models import UserInfo
def mealplan(request):
    print(f"Request params: {request.GET}")
    # Get user inputs from the request
    age = request.GET.get('age',30)
    height = request.GET.get('height',170)
    weight = request.GET.get('weight',70)
    gender = request.GET.get('gender','Male')
    activity = request.GET.get('activity',None)
    allergy = request.GET.get('allergy',None)
    dietary_preferences = request.GET.get('dietary-preferences',None)
    health_issues = request.GET.get('health-issues',None)

    if not age or not height or not weight or not gender or not activity:
        messages.error(request, "Please provide all required fields.")
        return redirect('mealplan') 
    
    user = UserInfo.objects.create(
            age=age,
            height=height,
            weight=weight,
            gender=gender,
            activity_level=activity,
            allergy=allergy,
            dietary_preferences=dietary_preferences,
            health_issues=health_issues
        )
    user.save()
    # API call to Spoonacular/Edamam
    api_url = "https://api.spoonacular.com/mealplanner/generate"
    params = {
        "apiKey": "2a92e58f72e7449daead08588939b215",
        "targetCalories": 2000,  # Example, customize based on user input
        "diet": dietary_preferences,
        "exclude": allergy,
        "timeFrame": "day",
    }

    response = requests.get(api_url, params=params)
    meal_data = response.json()

    # Debugging: log the API response
    print(meal_data)  # Check if 'meals' and 'nutrients' keys exist

    # Ensure the response contains the required keys
    if 'meals' not in meal_data or 'nutrients' not in meal_data:
        return render(request, 'mealplan.html', {
            'meals': [], 
            'nutrients': {
                'protein': 0,
                'fat': 0,
                'carbohydrates': 0
            },
            'error': 'Could not fetch meal data. Please try again.'
        })

    # Pass data to the template
    return render(request, 'mealplan.html', {
        'meals': meal_data['meals'], 
        'nutrients': meal_data['nutrients']
    
    })
    return render(request, 'mealplan.html')
