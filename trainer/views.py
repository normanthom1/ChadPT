from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from django.forms import modelformset_factory

from .forms import CustomUserCreationForm, WorkoutPlanForm, UserUpdateForm, LocationForm, CustomAuthenticationForm, WorkoutSessionForm, ExerciseForm
from .models import UserPreference, WeightHistory, WorkoutSession, WarmUp, CoolDown, Exercise, Location, Query, CustomUser, WorkoutSession, Exercise
from .lists_and_dictionaries import (
    QUOTES
)
from .helper_functions import replace_text, generate_random_id, safe_join, convert_text_to_json, workout_payload_text, generate_exercise_query

from dotenv import load_dotenv
from pathlib import Path
import os
import random
import json
import google.generativeai as genai
import requests
import re
import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'

if dotenv_path.exists():
    load_dotenv(dotenv_path)


class CustomLoginView(LoginView):
    """
    Custom login view that uses a custom authentication form
    and template for user login.
    """
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'


def homepage(request):
    """
    Renders the homepage with available locations.
    If the user is logged in, includes user-specific preferences and workout data.
    """
    locations = Location.objects.all()

    # Select a random quote
    selected_quote = random.choice(QUOTES)
    context = {'locations': locations}

    weight_data = []
    weight_history = []

    if request.user.is_authenticated:
        # Retrieve or create UserPreference before using it
        user = request.user
        preferences, created = UserPreference.objects.get_or_create(user=user)
        
        # Now you can safely use preferences in other queries
        weight_history = WeightHistory.objects.filter(user=preferences).order_by('-date')[:20]
        weight_data = [
            {
                'date': entry['date'],
                'weight': float(entry['weight']) if isinstance(entry['weight'], Decimal) else entry['weight'],
                'bmi': float(entry['bmi']) if isinstance(entry['bmi'], Decimal) else entry['bmi'],
            }
            for entry in weight_data
        ]
        workout_sessions = WorkoutSession.objects.filter(user=preferences).order_by('-date')[:20]
        preferred_location = preferences.preferred_location
        
        # Get the next workout session for the user (if available)
        next_workout = WorkoutSession.objects.filter(user=preferences, date__gt=datetime.date.today()).order_by('date').first()
        # next_workout_exercises = next_workout.exercises.all() if next_workout else []
        next_workout_exercises = Exercise.objects.filter(workout=next_workout)
        # print(f'exercise length {len(next_workout_exercises)}')

        for ex in next_workout_exercises:
            print(ex.name)

        preferred_location = preferences.preferred_location
            # Join the fitness goals into a comma-separated string
        if preferences.fitness_goals:  # Check if fitness_goals is not empty or None
            preferences.fitness_goals = ', '.join(preferences.fitness_goals)
        if preferences.workout_preferences:  # Check if fitness_goals is not empty or None
            preferences.workout_preferences = ', '.join(preferences.workout_preferences)

        ###################Personal Details Form#######################
        # Initialize the personal details form
        preferences, created = UserPreference.objects.get_or_create(user=request.user)
        # Prepare user details
        user_details = {
            'firstname': preferences.firstname,
            'lastname': preferences.lastname,
            'dob': preferences.dob,
            'current_injuries': preferences.current_injuries,
            'workout_preferences': ', '.join(preferences.workout_preferences or []),
            'preferred_location': preferences.preferred_location.name if preferences.preferred_location else 'Not specified',
            'workouts_per_week': preferences.workouts_per_week,
            'preferred_workout_time': preferences.preferred_workout_time,
            'fitness_goals': ', '.join(preferences.fitness_goals or []),
            'specific_muscle_groups': preferences.specific_muscle_groups,#', '.join(preferences.specific_muscle_groups or []),
            'cardio_preferences': preferences.cardio_preferences,#', '.join(preferences.cardio_preferences or []),
            'recovery_and_rest': preferences.recovery_and_rest#', '.join(preferences.recovery_and_rest or []),
        }    

        context.update({
            "user": user,
            "preferences": preferences,
            "weight_history": weight_history,
            "workout_sessions": workout_sessions,
            "preferred_location": preferred_location,
            "selected_quote": selected_quote,
            "weight_data": weight_data,
            "next_workout": next_workout,
            'next_workout_exercises': next_workout_exercises,
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


def signup(request):
    """
    Handles user registration. On successful registration, logs the user in
    and redirects to the workout generation page.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('generate_workout')
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {
        'form': form,
        'form_title': 'Sign Up',
        'form_id': 'sign-up-form',
    })


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
def send_user_data_to_gemini(request):
    """
    Handles the form submission to send user workout preferences to Gemini API, generate a workout plan,
    parse the response, and save the generated workouts in the database.
    """
    if request.method == "POST":
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            user = request.user
            preferences = get_object_or_404(UserPreference, user=user)
            weight_history = WeightHistory.objects.filter(user=preferences).order_by('-date')[:20]
            workout_sessions = WorkoutSession.objects.filter(user=preferences).order_by('-date')[:15]

            # Get preferred workout type, location, and length from form or defaults
            preferred_workout_type = form.cleaned_data.get('preferred_workout_type') or ', '.join(preferences.workout_preferences)
            preferred_location = form.cleaned_data.get('preferred_location') or preferences.preferred_location
            workout_length = form.cleaned_data.get('workout_length') or preferences.preferred_workout_time
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
                preferred_location,
                weight_history,
                workout_sessions,
            )
            # Send request to Gemini API
            api_key = os.getenv('GEMINI_API')
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(payload_text)
            try:
                # Parse JSON response and save workouts to database
                workout_data = convert_text_to_json(response.text)
                generate_group_id = generate_random_id()
                Query.objects.create(
                    group_id = generate_group_id,
                    user = CustomUser.objects.filter(email=request.user.email).first(),
                    query = payload_text
                )
                   
                for workout in workout_data:
                    workout_session = WorkoutSession.objects.create(
                        group_id=generate_group_id,
                        user=preferences,
                        location=preferred_location,
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
                            description=exercise.get('description'),
                            recommended_weight=exercise.get('recommended_weight'),
                            actual_weight=exercise.get('recommended_weight')
                        )

                return redirect('upcoming_workouts', group_id=generate_group_id)

            except requests.exceptions.RequestException as e:
                return JsonResponse({"error": f"Error sending request to Gemini: {str(e)}"}, status=500)

    else:
        form = WorkoutPlanForm()

    return render(request, 'form_template.html', {
        'form': form,
        'form_title': 'Workout',
        'form_id': 'workout-form',
    })

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
def replace_workout(request, workout_id):
    if request.method == "POST":
        user = request.user
        preferences = get_object_or_404(UserPreference, user=user)
        # Delete the specified workout and its related data
        workout = get_object_or_404(WorkoutSession, id=workout_id)
        workout_date = workout.date
        group_id = workout.group_id
        workout.delete()  # This cascades to delete WarmUp, CoolDown, and Exercises
        
        # Retrieve the original query
        original_query = get_object_or_404(Query, group_id=group_id).query

        # Call Gemini API to get a new workout
        api_key = os.getenv('GEMINI_API')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        # print(original_query)
        response = model.generate_content(replace_text(original_query, workout_date)) 
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


        return redirect('upcoming_workouts', group_id=group_id)

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

@login_required
def update_workout_session(request, pk):
    # Get the workout session or return a 404 error if not found
    workout = get_object_or_404(WorkoutSession, id=pk)

    # Initialize the WorkoutSessionForm with the current workout instance
    workout_form = WorkoutSessionForm(request.POST or None, instance=workout)

    # Create a formset for updating the actual_weight of exercises
    ExerciseFormSet = modelformset_factory(Exercise, form=ExerciseForm, extra=0)
    exercise_formset = ExerciseFormSet(request.POST or None, queryset=workout.exercises.all())

    # Handle form submission
    if request.method == "POST":
        if workout_form.is_valid() and exercise_formset.is_valid():
            # Save workout session
            workout_form.save()

            # Save each exercise's actual_weight
            exercise_formset.save()

            return redirect('workout_calendar')  # Redirect to the calendar or other desired view

    context = {
        'workout_form': workout_form,
        'exercise_formset': exercise_formset,
        'workout': workout,
    }
    return render(request, 'update_workout_session.html', context)


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

            # Return the updated personal details partial as HTML response
            return render(request, 'partials/personal_details.html', {
                'user_details': user_preference  # Ensure user details are passed to the partial
            })
        else:
            messages.error(request, 'There was an error updating your profile.')

    else:
        # When it's a GET request (or cancel), render the update form
        personal_details_form = UserUpdateForm(instance=user_preference)

        return render(request, 'partials/update_personal_details_form.html', {
            'personal_details_form': personal_details_form,
        })




def personal_details(request):
    user_preference, created = UserPreference.objects.get_or_create(user=request.user)
    return render(request, 'partials/personal_details.html', {
        'user_details': user_preference,
    })


def create_workout_form_view(request):
    if request.method == "POST":
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            user = request.user
            preferences = get_object_or_404(UserPreference, user=user)
            weight_history = WeightHistory.objects.filter(user=preferences).order_by('-date')[:20]
            workout_sessions = WorkoutSession.objects.filter(user=preferences).order_by('-date')[:15]

            # Get preferred workout type, location, and length from form or defaults
            preferred_workout_type = form.cleaned_data.get('preferred_workout_type') or ', '.join(preferences.workout_preferences)
            preferred_location = form.cleaned_data.get('preferred_location') or preferences.preferred_location
            workout_length = form.cleaned_data.get('workout_length') or preferences.preferred_workout_time
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
                preferred_location,
                weight_history,
                workout_sessions,
            )
            print(payload_text)
            api_key = os.getenv('GEMINI_API')
            print(api_key)
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(payload_text)
            print(response.text)
            workout_data = convert_text_to_json(response.text)
            group_id = generate_random_id()
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
