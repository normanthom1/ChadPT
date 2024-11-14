from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse

from .forms import CustomUserCreationForm, WorkoutPlanForm, UserUpdateForm, LocationForm, CustomAuthenticationForm
from .models import UserPreference, WeightHistory, WorkoutSession, WarmUp, CoolDown, Exercise, Location, Query, CustomUser

from dotenv import load_dotenv
from pathlib import Path
import os
import random
import json
import google.generativeai as genai
import requests
import re

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'

if dotenv_path.exists():
    load_dotenv(dotenv_path)


def replace_text(text, new_date):
    # Replace the date in the format YYYY-MM-DD
    text = re.sub(r'The workout should start on \d{4}-\d{2}-\d{2}', f'The workout should start on {new_date}', text)
    
    # Replace 'one day tailored' with 'one week tailored' if it exists in the text
    text = re.sub(r'one week tailored', 'one day tailored', text)
    
    return text

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
from django.shortcuts import render
import random

def homepage(request):
    """
    Renders the homepage with available locations.
    If the user is logged in, includes user-specific preferences and workout data.
    """
    locations = Location.objects.all()
    quotes = [
        {"quote": "The only bad workout is the one that didn’t happen.", "author": None},
        {"quote": "Take care of your body. It’s the only place you have to live.", "author": "Jim Rohn"},
        {"quote": "Exercise is a celebration of what your body can do, not a punishment for what you ate.", "author": None},
        {"quote": "The pain you feel today will be the strength you feel tomorrow.", "author": None},
        {"quote": "Push yourself, because no one else is going to do it for you.", "author": None},
        {"quote": "Sweat is fat crying.", "author": None},
        {"quote": "Success usually comes to those who are too busy to be looking for it.", "author": "Henry David Thoreau"},
        {"quote": "Fitness is not about being better than someone else. It’s about being better than you used to be.", "author": None},
        {"quote": "Motivation is what gets you started. Habit is what keeps you going.", "author": "Jim Ryun"},
        {"quote": "The body achieves what the mind believes.", "author": None},
        {"quote": "What hurts today makes you stronger tomorrow.", "author": "Jay Cutler"},
        {"quote": "Your body can stand almost anything. It’s your mind that you have to convince.", "author": None},
        {"quote": "Train insane or remain the same.", "author": None},
        {"quote": "The only way to define your limits is by going beyond them.", "author": "Arthur C. Clarke"},
        {"quote": "The only bad workout is the one you didn’t do.", "author": None},
        {"quote": "Strength does not come from physical capacity. It comes from an indomitable will.", "author": "Mahatma Gandhi"},
        {"quote": "Success is usually the culmination of controlling failure.", "author": "Sylvester Stallone"},
        {"quote": "You don’t have to be extreme, just consistent.", "author": None},
        {"quote": "Don’t limit your challenges, challenge your limits.", "author": None},
        {"quote": "Nothing will work unless you do.", "author": "Maya Angelou"}
        # Add more quotes as desired
    ]

    # Select a random quote
    selected_quote = random.choice(quotes)
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
            # Join the fitness goals into a comma-separated string
        if preferences.fitness_goals:  # Check if fitness_goals is not empty or None
            preferences.fitness_goals = ', '.join(preferences.fitness_goals)
        if preferences.workout_preferences:  # Check if fitness_goals is not empty or None
            preferences.workout_preferences = ', '.join(preferences.workout_preferences)

        context.update({
            "user": user,
            "preferences": preferences,
            "weight_history": weight_history,
            "workout_sessions": workout_sessions,
            "preferred_location": preferred_location,
            "selected_quote": selected_quote,
            "weight_data": weight_data,
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
                f"Imagine you are a personal trainer. Create a unique and challenging workout plan for one {plan_duration_value} "
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
                "  \"muscle group\": \"Muscle group worked\",\n"
                "  \"location\": \"Location of workout\",\n"
                "  \"date\": \"28-10-2024\",\n"
                "  \"exercises\": [\n"
                "    {{\n"
                "      \"name\": \"Exercise Name\",\n"
                "      \"sets\": \"3\",\n"
                "      \"reps\": \"10 per leg\",\n"
                "      \"recommended_weight\": \"10 kg\",\n"
                "      \"description\": \"Exercise description\"\n"
                "    }}\n"
                "  ],\n"
                "  \"warm_up\": \"Warm-up details\",\n"
                "  \"cool_down\": \"Cool-down details\",\n"
                "  \"important_considerations\": \"Important considerations\",\n"
                "  \"explanation\": \"Detailed explanation of the workout\"\n"
                "}}]\n"
                # "Ensure each exercise has a name, sets, reps, \"location\", \"muscle groups worked\", and \"description\"."
            )

            # Send request to Gemini API
            api_key = os.getenv('GEMINI_API')
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(payload_text)
            print(response.text)



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
                            recommended_weight=exercise.get('recommended_weight')
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
        print("HERE")
        print(workout_date)
        print(replace_text(original_query, workout_date))

        
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


from django.shortcuts import render, get_object_or_404, redirect
from .models import WorkoutSession, Exercise




# def replace_exercise(request, workout_id, exercise_id):
#     # Retrieve the specific workout session and the exercise that we want to replace
#     workout = get_object_or_404(WorkoutSession, id=workout_id)
#     exercise = get_object_or_404(Exercise, id=exercise_id, workout=workout)  # Ensure the exercise belongs to the workout

#     if request.method == 'POST':
#         # Update the exercise with form data (example: exercise name, sets, reps)
#         exercise.name = request.POST.get('name', exercise.name)
#         exercise.sets = request.POST.get('sets', exercise.sets)
#         exercise.reps = request.POST.get('reps', exercise.reps)
#         exercise.recommended_weight = request.POST.get('recommended_weight', exercise.recommended_weight)
#         # exercise.actual_weight = request.POST.get('actual_weight', exercise.actual_weight)
#         exercise.description = request.POST.get('description', exercise.description)
        
#         # Save the updated exercise
#         exercise.save()
        
#         # Redirect back to the workout detail page after updating
#         return redirect('workout_detail', workout_id=workout.id)
    
#     # If GET request, render the form with the current exercise details pre-filled
#     return render(request, 'replace_exercise.html', {
#         'workout': workout,
#         'exercise': exercise
#     })

def generate_exercise_query(exercise_data):
    # Generate a query string to send to the model based on the exercise data
    payload_text = (
        f"Replace exercise '{exercise_data['name']}', with sets: "
        f"{exercise_data['sets']}, reps: {exercise_data['reps']}, "
        f"the replacement exercise should target similar muscle groups. "
        "Format the entire response as JSON as follows:\n"
        "[\n"
        "    {\n"
        "        \"name\": \"Exercise Name\",\n"
        "        \"sets\": \"3\",\n"
        "        \"reps\": \"10 per leg\",\n"
        "        \"recommended_weight\": \"10 kg\",\n"
        "        \"description\": \"Exercise description\"\n"
        "    }\n"
        "]\n"
    )
    return payload_text

@csrf_exempt
def replace_exercise(request, workout_id, exercise_id):
    # Retrieve the specific workout session and the exercise that we want to replace
    workout = get_object_or_404(WorkoutSession, id=workout_id)
    exercise = get_object_or_404(Exercise, id=exercise_id, workout=workout)  # Ensure the exercise belongs to the workout

    if request.method == 'POST':
        # Collect details of the current exercise to send to the API
        exercise_data = {
            'name': exercise.name,
            'sets': exercise.sets,
            'reps': exercise.reps,
            'recommended_weight': exercise.recommended_weight,
            'description': exercise.description
        }

        # Configure API connection
        api_key = os.getenv('GEMINI_API')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        print(generate_exercise_query(exercise_data))

        # Call the API to get a similar exercise based on the current one
        response = model.generate_content(generate_exercise_query(exercise_data))
        new_exercise_data = convert_text_to_json(response.text)

        # Delete the old exercise
        exercise.delete()

        # Create and save the new exercise based on the API response
        Exercise.objects.create(
            workout=workout,
            name=new_exercise_data.get('name'),
            sets=new_exercise_data.get('sets'),
            reps=new_exercise_data.get('reps'),
            recommended_weight=new_exercise_data.get('recommended_weight'),
            description=new_exercise_data.get('description')
        )

        # Redirect back to the workout detail page
        return redirect('upcoming_workouts', group_id=workout.group_id)

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