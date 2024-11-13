from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse

from .forms import CustomUserCreationForm, WorkoutPlanForm, UserUpdateForm, LocationForm, CustomAuthenticationForm
from .models import UserPreference, WeightHistory, WorkoutSession, WarmUp, CoolDown, Exercise, Location

from dotenv import load_dotenv
from pathlib import Path
import os
import random
import json
import google.generativeai as genai
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'

if dotenv_path.exists():
    load_dotenv(dotenv_path)


def generate_random_id():
    """Generates a random 20-digit ID."""
    return ''.join([str(random.randint(0, 9)) for _ in range(20)])


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
    context = {'locations': locations}

    if request.user.is_authenticated:
        user = request.user
        preferences, created = UserPreference.objects.get_or_create(user=user)
        weight_history = WeightHistory.objects.filter(user=preferences).order_by('-date')[:20]
        workout_sessions = WorkoutSession.objects.filter(user=preferences).order_by('-date')[:20]
        preferred_location = preferences.preferred_location

        context.update({
            "user": user,
            "preferences": preferences,
            "weight_history": weight_history,
            "workout_sessions": workout_sessions,
            "preferred_location": preferred_location,
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

    return render(request, 'form_template.html', {
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


def safe_join(field):
    """
    Safely joins a serialized list field into a string.
    If the field is already a list, returns a comma-separated string.
    """
    if isinstance(field, str):
        try:
            field = eval(field)
        except Exception:
            pass
    return ', '.join(field) if isinstance(field, list) else field


def convert_text_to_json(text):
    """
    Converts a given text to a JSON object after removing backticks and unnecessary prefixes.
    """
    clean_text = text.strip('`').strip()
    if clean_text.lower().startswith("json"):
        clean_text = clean_text[4:].strip()

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None
    

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

            # Construct payload text for Gemini API request
            payload_text = (
                f"Imagine you are a personal trainer. Create a unique and challenging workout plan for the one {plan_duration_value} "
                f"tailored to the individual's current fitness goals and workout frequency. Avoid repetition of past exercises while "
                f"ensuring a focus on under-targeted muscle groups based on workout history and user preference. The workout should "
                f"start on {start_date}\n\n"
                f"--- Personal Info ---\n"
                + (f"Fitness Goals: {', '.join(preferences.fitness_goals)}\n" if preferences.fitness_goals else "")
                + f"Preferred Workout Type: {preferred_workout_type}\n"
                + f"Workout should not take longer than: {workout_length} minutes\n"
                + (f"Preferred Workout Intensity: {preferences.preferred_workout_intensity}\n" if preferences.preferred_workout_intensity else "")
                + (f"Fitness Level: {preferences.fitness_level}\n" if preferences.fitness_level else "")
                + f"Workouts Per Week: {preferences.workouts_per_week}\n"
                + (f"Current injuries to consider: {preferences.current_injuries}\n" if preferences.current_injuries else "")
                + (f"Specific Muscle Groups to Focus on: {safe_join(preferences.specific_muscle_groups)}\n" if preferences.specific_muscle_groups else "")
                + (f"Cardio Preferences: {safe_join(preferences.cardio_preferences)}\n" if preferences.cardio_preferences else "")
                + (f"Recovery and Rest: {safe_join(preferences.recovery_and_rest)}\n" if preferences.recovery_and_rest and plan_duration_value == 'One Week' else "")
                + f"\n--- Workout Location & Available Equipment ---\n"
                + f"Location: {preferred_location.name}\n"
                + "Equipment:\n"
                + "\n".join([f"  - {equipment.equipment}" for equipment in preferred_location.equipment.all()])
                + f"\n\n--- Weight History ---\n"
                + "\n".join([f"  - Date: {entry.date}, Weight: {entry.weight} kg, BMI: {entry.bmi}" for entry in weight_history])
                + "\n\n--- Past Workouts ---\n"
                + "\n".join(
                    [
                        f"  - Date: {session.date}\n    Type: {session.workout_type}\n    Duration: {session.time_taken} mins\n    Difficulty: {session.difficulty_rating}\n"
                        "    Exercises:\n"
                        + "\n".join(
                            [
                                f"      - {exercise.name}: Sets {exercise.sets}, Reps {exercise.reps}, Weight: {exercise.actual_weight or 'Bodyweight'}"
                                for exercise in session.exercises.all()
                            ]
                        )
                        for session in workout_sessions
                    ]
                )
                + f"\n\n--- Structured Workout Plan ---\n"
                f"Format the entire response as valid JSON as follows:\n"
                "[{{\n"
                "  \"name\": \"Workout Name\",\n"
                "  \"goal\": \"Goal of the workout\",\n"
                "  \"date\": \"28-10-2024\",\n"
                "  \"exercises\": [\n"
                "    {{\n"
                "      \"name\": \"Exercise Name\",\n"
                "      \"sets\": \"3\",\n"
                "      \"reps\": \"10 per leg\",\n"
                "      \"description\": \"Exercise description\"\n"
                "    }}\n"
                "  ],\n"
                "  \"warm_up\": \"Warm-up details\",\n"
                "  \"cool_down\": \"Cool-down details\",\n"
                "  \"important_considerations\": \"Important considerations\",\n"
                "  \"explanation\": \"Detailed explanation of the workout\"\n"
                "}}]\n"
                "Ensure each exercise has a \"name\", \"sets\", \"reps\", and \"description\"."
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
                            description=exercise.get('description')
                        )

                # return redirect('workout_plan_result')
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


def upcoming_workouts_view(request, group_id):
    """
    Display the list of workouts created in a group, showing details of each workout.
    """
    # Query the workout sessions based on group_id
    workouts = WorkoutSession.objects.filter(group_id=group_id).order_by('date')
    
    # Retrieve exercises, warm-ups, and cool-downs associated with each workout
    workouts_data = []
    for workout in workouts:
        exercises = Exercise.objects.filter(workout=workout)
        warm_up = WarmUp.objects.filter(workout=workout).first()
        cool_down = CoolDown.objects.filter(workout=workout).first()

        workouts_data.append({
            'name': workout.name,
            'goal': workout.goal,
            'date': workout.date,
            'description': workout.description,
            'warm_up': warm_up.description if warm_up else "No warm-up",
            'cool_down': cool_down.description if cool_down else "No cool-down",
            'exercises': [
                {
                    'name': exercise.name,
                    'sets': exercise.sets,
                    'reps': exercise.reps,
                    'description': exercise.description,
                    'recommended_weight': exercise.recommended_weight
                } for exercise in exercises
            ]
        })

    return render(request, 'upcoming_workouts.html', {
        'workouts_data': workouts_data,
    })



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