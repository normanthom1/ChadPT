from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from django.forms import modelformset_factory
from decimal import Decimal
from django.template.loader import render_to_string
from django.http import Http404

from .forms import WorkoutPlanForm, UserUpdateForm, LocationForm, CustomAuthenticationForm, ExerciseForm, UserDetailsForm, PreferencesForm
from .models import UserPreference, WeightHistory, WorkoutSession, WarmUp, CoolDown, Exercise, Location, Query, CustomUser, WorkoutSession, Exercise
from .lists_and_dictionaries import (
    QUOTES,
    GOAL_CHOICES,
    DAYS_OF_WEEK_CHOICES,
    WORKOUT_TYPE_PREFERENCE_CHOICES,
    EATING_HABITS_CHOICES,
    FITNESS_LEVEL_CHOICES
)
from .helper_functions import (
    replace_text,
    generate_random_id,
    safe_join,
    convert_text_to_json,
    workout_payload_text,
    generate_exercise_query,
    personal_details_dict
)

from dotenv import load_dotenv
from pathlib import Path
import os
import random
import json
import google.generativeai as genai
import requests
import re
import datetime

from datetime import date


BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'

if dotenv_path.exists():
    load_dotenv(dotenv_path)


from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.middleware.csrf import get_token

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get('HX-Request'):  # Check if the request is made by HTMX
            form = self.get_form()

            # Get the CSRF token for the form
            csrf_token = get_token(request)

            # Render the form manually, including CSRF token
            html = f"""
            <div class="container mb-5">
                <form method="post" action="{request.path}">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                    {form.as_p()}
                    <button type="submit" class="btn btn-block btn-warning btn-sm">Login</button>
                </form>
            </div>
            """
            return HttpResponse(html)  # Return HTML response directly

        return super().get(request, *args, **kwargs)



def homepage(request):
    """
    Renders the homepage with available locations.
    If the user is logged in, includes user-specific preferences and workout data.
    """
    locations = Location.objects.all()
    selected_quote = random.choice(QUOTES)
    context = {"locations": locations, "selected_quote": selected_quote}

    if request.user.is_authenticated:
        # Retrieve or create UserPreference
        user = request.user
        preferences, created = UserPreference.objects.get_or_create(user=user)

        # Retrieve weight history
        weight_history = WeightHistory.objects.filter(user=preferences).order_by("-date")[:20]
        weight_data = [
            {
                "date": entry.date,
                "weight": float(entry.weight) if isinstance(entry.weight, Decimal) else entry.weight,
            }
            for entry in weight_history
        ]

        # Retrieve workout sessions and next workout
        workout_sessions = WorkoutSession.objects.filter(user=preferences).order_by("-date")[:20]
        next_workout = WorkoutSession.objects.filter(user=preferences, date__gt=date.today()).order_by("date").first()
        next_workout_exercises = Exercise.objects.filter(workout=next_workout) if next_workout else []

        user_details = personal_details_dict(preferences)

        # Update context with user-specific data
        context.update({
            "user": user,
            "preferences": preferences,
            "weight_history": weight_history,
            "weight_data": weight_data,
            "workout_sessions": workout_sessions,
            "next_workout": next_workout,
            "next_workout_exercises": next_workout_exercises,
            "user_details": user_details,
        })

    return render(request, "homepage.html", context)


def location_detail(request, location_id):
    """
    Retrieves and renders the details of a location, including available equipment.
    """
    location = get_object_or_404(Location, id=location_id)
    equipment = location.equipment.all()

    context = {
        'location': location,
        'equipment': equipment,
    }

    return render(request, "partials/location_detail.html", context)



from formtools.wizard.views import SessionWizardView
from django.shortcuts import render
from datetime import date

FORMS = [("user_details", UserDetailsForm),
         ("preferences", PreferencesForm),
         ("location", LocationForm)]

TEMPLATES = {
    "user_details": "forms/user_details.html",
    "preferences": "forms/preferences.html",
    "location": "forms/location.html",
}

class CustomUserWizard(SessionWizardView):
    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        data = {key: form.cleaned_data for key, form in zip(self.get_form_list(), form_list)}

        # Create user and related models
        user = CustomUser.objects.create_user(
            email=data['user_details']['email'],
            firstname=data['user_details']['firstname'],
            lastname=data['user_details']['lastname'],
            dob=data['user_details']['dob']
        )

        preferences = UserPreference.objects.create(
            user=user,
            gender=data['preferences']['gender'],
            height=data['user_details']['height'],
            workout_type_preference=data['preferences']['workout_type_preference'],
            fitness_goals=data['preferences']['fitness_goals'],
            fitness_level=data['preferences']['fitness_level'],
            eating_habits=data['preferences']['eating_habits'],
            workout_days=data['preferences']['workout_days'],
            preferred_workout_duration=data['location']['preferred_workout_duration']
        )

        # Handle location
        if data['location']['preferred_location'] == 'new':
            new_location = Location.objects.create(
                name=data['location']['new_location_name'],
                location_type=data['location']['new_location_type'],
                address=data['location']['new_location_address']
            )
            new_location.equipment.set(data['location']['new_location_equipment'])
            preferences.preferred_location = new_location
        else:
            preferences.preferred_location = data['location']['existing_location']

        preferences.save()

        # Create initial weight history
        WeightHistory.objects.create(
            user=preferences,
            date=date.today(),
            weight=data['user_details']['weight']
        )

        return render(self.request, "forms/done.html", {"user": user})



@login_required
def update_profile(request):
    """
    Allows the logged-in user to update their profile details.
    """
    user_preference, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            print(form.errors)
    else:
        form = UserUpdateForm(instance=user_preference)

    return render(request, 'form_template.html', {
        'form': form,
        'form_title': 'Update Personal Details',
        'form_id': 'update-personal-details-form',
    })


@login_required
def workout_plan(request):
    """
    Renders a personalized workout plan for the logged-in user based on their preferences and history.
    """
    api_key = os.getenv('GEMINI_API')
    user = request.user
    preferences = get_object_or_404(UserPreference, user=user)
    weight_history = WeightHistory.objects.filter(user=preferences).order_by('-date')[:20]
    workout_sessions = WorkoutSession.objects.filter(user=preferences).order_by('-date')[:20]
    locations = preferences.preferred_location

    context = {
        "user": user,
        "preferences": preferences,
        "weight_history": weight_history,
        "workout_sessions": workout_sessions,
        "locations": locations,
    }

    return render(request, "workout_plan.html", context)


def workout_plan_result(request):
    """
    Displays the result of the generated workout plan.
    """
    workout_plan = request.session.get('workout_plan')
    return render(request, 'workout_plan_result.html', {'workout_plan': workout_plan})


@csrf_exempt
def upcoming_workouts_view(request, group_id):
    workouts = WorkoutSession.objects.filter(group_id=group_id).order_by('date')
    workouts_data = []
    for workout in workouts:
        exercises = Exercise.objects.filter(workout=workout)
        warm_up = WarmUp.objects.filter(workout=workout).first()
        cool_down = CoolDown.objects.filter(workout=workout).first()

        workouts_data.append({
            'id': workout.id,
            'name': workout.name,
            'goal': workout.goal,
            'date': workout.date,
            'group_id': workout.group_id,
            'description': workout.description,
            'warm_up': warm_up.description if warm_up else "No warm-up",
            'cool_down': cool_down.description if cool_down else "No cool-down",
            'exercises': [
                {
                    'id': exercise.id,
                    'name': exercise.name,
                    'sets': exercise.sets,
                    'reps': exercise.reps,
                    'description': exercise.description,
                    'recommended_weight': exercise.recommended_weight
                } for exercise in exercises
            ]
        })

    return render(request, 'upcoming_workouts.html', {'workouts_data': workouts_data, 'group_id': group_id})

@csrf_exempt
def replace_workout(request, group_id, workout_id):
    try:
        workout = WorkoutSession.objects.get(pk=workout_id)
        print(f"WORKOUT - ID:{workout.id}")
    except WorkoutSession.DoesNotExist:
        raise Http404("Workout does not exist")
    print('replacing workouts')
    if request.method == "POST":
        try:
            user = request.user
            print(f"User: {user}")
            preferences = get_object_or_404(UserPreference, user=user)
            print(f"User Preferences found: {preferences}")
            user = request.user
            # Delete the specified workout and its related data
            workout = get_object_or_404(WorkoutSession, id=workout_id)
            workout_date = workout.date
            group_id = workout.group_id
            print(group_id)
            workout.delete()  # This cascades to delete WarmUp, CoolDown, and Exercises
            print('workout deleted')
            
            # Retrieve the original query
            original_query = get_object_or_404(Query, group_id=group_id).query

            print(original_query)
            # Call Gemini API to get a new workout
            api_key = os.getenv('GEMINI_API')
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(replace_text(original_query, workout_date)) 
            print(response.text)
            # Parse the response and save new workout data
            workout_data = convert_text_to_json(response.text)
            # print(response.text)  # You would need a JSON parsing function here
            for workout in workout_data:
                workout_session = WorkoutSession.objects.create(
                    group_id=group_id,
                    user=preferences,
                    location=preferences.preferred_location,
                    name=workout.get('name'),
                    goal=workout.get('goal'),
                    date=workout.get('date'),
                    description=workout.get('explanation'),
                    workout_type=workout.get('workout_type'),
                )

                WarmUp.objects.create(workout=workout_session, description=workout.get('warm_up'))
                CoolDown.objects.create(workout=workout_session, description=workout.get('cool_down'))

                for exercise in workout.get('exercises', []):
                    Exercise.objects.create(
                        workout=workout_session,
                        name=exercise.get('name'),
                        sets=exercise.get('sets'),
                        reps=exercise.get('reps'),
                        description=exercise.get('description')
                    )


            print('REDIRECT')


            workout_session = get_object_or_404(WorkoutSession, id=workout_session.id)
            # exercises = workout_session.exer
            print(f'Workout obtained {workout_session} ')
            exercises = workout_session.exercises.all()
            print(exercises)
            return render(request, 'partials/workout_partial.html', {
                'workout': workout_session,
                'exercises': exercises,

            })
            # return redirect('upcoming_workouts', group_id=workout_session.group_id)
        

        except Exception as e:
            print(f"Error during workout replacement: {e}")
            return JsonResponse({'status': 'failed', 'error': str(e)}, status=500)

    return JsonResponse({'status': 'failed'}, status=400)



@csrf_exempt
def replace_exercise(request, workout_id, exercise_id):
    workout = get_object_or_404(WorkoutSession, id=workout_id)
    exercise = get_object_or_404(Exercise, id=exercise_id, workout=workout)  # Ensure the exercise belongs to the workout

    if request.method == 'POST':
        # Collect details of the current exercise to send to the API
        exercise_data = {
            'id': exercise.id,
            'name': exercise.name,
            'sets': exercise.sets,
            'reps': exercise.reps,
            'recommended_weight': exercise.recommended_weight,
            'description': exercise.description
        }

        # Call the API to get a similar exercise based on the current one
        api_key = os.getenv('GEMINI_API')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(generate_exercise_query(exercise_data))
        new_exercise_data = convert_text_to_json(response.text)

        # Delete the old exercise
        exercise.delete()

        print(new_exercise_data)

        # Create and save the new exercise based on the API response
        new_exercise = Exercise.objects.create(
            workout=workout,
            name=new_exercise_data[0].get('name'),
            sets=new_exercise_data[0].get('sets'),
            reps=new_exercise_data[0].get('reps'),
            recommended_weight=new_exercise_data[0].get('recommended_weight'),
            description=new_exercise_data[0].get('description')
        )

        # Return the updated exercise to replace the old one using HTMX
        return render(request, 'partials/exercise_partial.html', {
            'exercise': new_exercise,  # Pass the actual new exercise instance
            'workout': workout
        })

    # Render the replace exercise form for GET requests
    return render(request, 'replace_exercise.html', {
        'workout': workout,
        'exercise': exercise
    })


def workout_detail_view(request, workout_id):
    # Retrieve the workout session and all associated exercises
    workout = get_object_or_404(WorkoutSession.objects.prefetch_related('exercises'), id=workout_id)
    exercises = workout.exercises.all()  # Access exercises through the related name
    
    return render(request, 'workout_detail.html', {'workout': workout, 'exercises': exercises})

def location_create(request):
    """
    Handles creating a new location entry.
    Displays a form for location creation and redirects to a location list on successful form submission.
    """
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('location_list')
    else:
        form = LocationForm()

    return render(request, 'form_template.html', {
        'form': form,
        'form_title': 'Add Location',
        'form_id': 'location-form',
        'action': 'Create',
    })


def location_update(request, pk):
    """
    Handles updating an existing location entry.
    Displays a form for updating location details and redirects to a location list on successful form submission.
    """
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('location_list')
    else:
        form = LocationForm(instance=location)

    return render(request, 'form_template.html', {
        'form': form,
        'form_title': 'Edit Location',
        'form_id': 'location-update-form',
        'action': 'Update',
    })



def update_personal_details(request):
    user_preference, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        post_data = request.POST.copy()  # Create a mutable copy of the POST data

        # Ensure multi-select fields are passed as lists
        multi_select_fields = ['specific_muscle_groups', 'cardio_preferences', 'recovery_and_rest']
        for field in multi_select_fields:
            post_data.setlist(field, request.POST.getlist(field))

        # Pass cleaned data to the form
        personal_details_form = UserUpdateForm(post_data, instance=user_preference)

        if personal_details_form.is_valid():
            personal_details_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            user_details = personal_details_dict(user_preference)

            # Return the updated personal details partial as HTML response
            return render(request, 'partials/personal_details.html', {
                'user_details': user_details  # Ensure user details are passed to the partial
            })
        else:
            messages.error(request, 'There was an error updating your profile.')

    else:
        # When it's a GET request (or cancel), render the update form
        personal_details_form = UserUpdateForm(instance=user_preference)

        return render(request, 'partials/update_personal_details_form.html', {
            'personal_details_form': personal_details_form,
        })


###################################

def personal_details(request):
    preferences, created = UserPreference.objects.get_or_create(user=request.user)
    user_details = preferences
    return render(request, 'partials/personal_details.html', {'user_details': user_details})

import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect
from .forms import UserDetailsForm
from .models import UserPreference

def edit_field(request, field_name):
    logger.debug(f"Editing field: {field_name}")
    preferences = UserPreference.objects.get(user=request.user)
    
    # Create a form instance with the user data
    form = UserDetailsForm(request.POST or None, instance=preferences)
    
    if request.method == 'POST':
        # Ensure the field exists in the form and update it
        if field_name in form.fields:
            form.fields[field_name].initial = request.POST.get(field_name)
        
        # Disable all other fields except the one being edited
        for field in form.fields:
            if field != field_name:
                form.fields[field].disabled = True
        
        # Validate and save the form
        if form.is_valid():
            form.save()
            # Optionally, return a success response (or redirect)
            return render(request, 'partials/edit_field.html', {'form': form, 'field_name': field_name})
        else:
            # Handle form errors (if any)
            return render(request, 'partials/edit_field.html', {'form': form, 'field_name': field_name, 'errors': form.errors})

    # GET request: just display the form for the specific field
    return render(request, 'partials/edit_field.html', {'form': form, 'field_name': field_name})






from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.shortcuts import render, redirect
from .models import UserPreference
from .forms import UserDetailsForm  # Make sure you import the appropriate form

logger = logging.getLogger(__name__)

def update_field(request, field_name):
    logger.debug(f"Updating field: {field_name}")
    # Fetch the PersonalDetails instance
    personal_details = UserPreference.objects.get(user=request.user)
    # Adjust according to your logic
    print(personal_details.name)

    # Dynamically fetch the field name to update
    if request.method == 'POST':
        # Ensure you're using a form that dynamically updates based on the field_name
        form = UserDetailsForm(request.POST, instance=personal_details)
        
        if form.is_valid():
            # Update the specific field
            setattr(personal_details, field_name, form.cleaned_data[field_name])
            personal_details.save()

            # If the field was updated successfully, redirect or update view as needed
            return render(request, 'partials/update_field.html', {'form': form, 'field_name': field_name})

    else:
        # Instantiate the form with the current instance for GET requests
        form = UserDetailsForm(instance=personal_details)

    # Render the template with the form
    return render(request, 'partials/update_field.html', {'form': form, 'field_name': field_name})




#########################################

def create_workout_form_view(request):
    if request.method == "POST":
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            user = request.user
            preferences = get_object_or_404(UserPreference, user=user)
            weight_history = WeightHistory.objects.filter(user=preferences).order_by('-date')[:20]
            workout_sessions = WorkoutSession.objects.filter(user=preferences).order_by('-date')[:15]
            if workout_sessions is None:
                raise ValueError("workout_data is None")
            else:
                print(workout_sessions)


            # Get preferred workout type, location, and length from form or defaults
            preferred_workout_type = form.cleaned_data.get('preferred_workout_type') or ', '.join(preferences.workout_preferences)
            preferred_location = form.cleaned_data.get('preferred_location') or preferences.preferred_location.name
            
            location = Location.objects.get(name=preferred_location)
            print(f'Preffered Location:{location}')
            workout_length = form.cleaned_data.get('workout_length') or preferences.preferred_workout_duration
            start_date = form.cleaned_data.get('start_date')
            
            # Determine plan duration in days
            plan_duration_value = form.cleaned_data.get('plan_duration')
            plan_duration = 1 if plan_duration_value == 'day' else 7

            # Construct p = ayload text for Gemini API request
            payload_text = workout_payload_text(
                plan_duration_value,
                start_date,
                preferences,
                preferred_workout_type,
                workout_length,
                location,
                weight_history,
                workout_sessions,
            )
            #print(payload_text)
            api_key = os.getenv('GEMINI_API')
            print(api_key)
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            print("#################payload_text###############")
            print(payload_text)
            response = model.generate_content(payload_text)
            #print(response.text)
            workout_data = convert_text_to_json(response.text)
            # print(workout_data)
            group_id = generate_random_id()
            Query.objects.create(
                group_id=group_id,
                user=preferences,
                query=payload_text
            )
            # if workout_sessions:
            for workout in workout_data:
                workout_session = WorkoutSession.objects.create(
                    group_id=group_id,
                    user=preferences,
                    name=workout['name'],
                    goal=workout['goal'],
                    date=workout['date'],
                    description=workout['explanation']
                )
                WarmUp.objects.create(workout=workout_session, description=workout['warm_up'])
                CoolDown.objects.create(workout=workout_session, description=workout['cool_down'])
                for exercise in workout['exercises']:
                    Exercise.objects.create(workout=workout_session, **exercise)
            return redirect('upcoming_workouts', group_id=group_id)
    else:
        form = WorkoutPlanForm()
    
    return render(request, 'partials/create_workout_form.html', {'form': form})
