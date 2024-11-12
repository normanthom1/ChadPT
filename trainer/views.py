from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import CustomUserCreationForm, WorkoutPlanForm, UserUpdateForm, LocationForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser, UserPreference, WeightHistory, WorkoutSession, Location
import os
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
import requests
from django.http import JsonResponse
from django.contrib import messages


BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'

if dotenv_path.exists():
    load_dotenv(dotenv_path)

# api_key = os.getenv('GEMINI_API')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('generate_workout')  # Redirect to your home page or dashboard
    else:
        form = CustomUserCreationForm()
    # return render(request, 'signup.html', {'form': form})
    return render(request, 'form_template.html', {
        'form': form,
        'form_title': 'Sign Up',
        'form_id': 'sign-up-form',
    })




@login_required
def update_profile(request):
    # Get or create UserPreference instance for the logged-in user
    user_preference, created = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')  # Adjust to your profile view or redirect target
    else:
        form = UserUpdateForm(instance=user_preference)

    # return render(request, 'update_profile.html', {'form': form})
    return render(request, 'form_template.html', {
        'form': form,
        'form_title': 'Update Personal Details',
        'form_id': 'update-personal-details-form',
    })


@login_required
def workout_plan(request):
    api_key = os.getenv('GEMINI_API')  # Fetching the environment variable
    print(api_key)
    user = request.user  # Get the logged-in user
    preferences = get_object_or_404(UserPreference, user=user)
    weight_history = WeightHistory.objects.filter(user=preferences).order_by('-date')[:20]  # Get recent 3 entries
    workout_sessions = WorkoutSession.objects.filter(user=preferences).order_by('-date')[:20]  # Get recent 3 workouts
    locations = preferences.preferred_location

    # Preparing context for the text generation
    context = {
        "user": user,
        "preferences": preferences,
        "weight_history": weight_history,
        "workout_sessions": workout_sessions,
        "locations": locations,
    }

    return render(request, "workout_plan.html", context)


def workout_plan_result(request):
    workout_plan = request.session.get('workout_plan')
    return render(request, 'workout_plan_result.html', {'workout_plan': workout_plan})


# Helper function to handle serialized strings
def safe_join(field):
    # Check if the field is a string that looks like a serialized list
    if isinstance(field, str):
        try:
            # Attempt to evaluate the string to a list
            field = eval(field)
        except:
            pass  # If eval fails, keep the field as-is
    # Join list items if the field is now a list
    return ', '.join(field) if isinstance(field, list) else field



@csrf_exempt
def send_user_data_to_gemini(request):
    if request.method == "POST":
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            user = request.user
            preferences = get_object_or_404(UserPreference, user=user)
            weight_history = WeightHistory.objects.filter(user=preferences).order_by('-date')[:20]
            workout_sessions = WorkoutSession.objects.filter(user=preferences).order_by('-date')[:15]
            
            # Preffered Workout Type
            preferred_workout_type = form.cleaned_data.get('preferred_workout_type')           
            if not preferred_workout_type:
                preferred_workout_type = {', '.join(preferences.workout_preferences)}
            else:
                preferred_workout_type = preferred_workout_type

            # Preffered preferred_location
            preferred_location = form.cleaned_data.get('preferred_location') 
            if not preferred_workout_type:
                preferred_workout_type = preferences.preferred_location
            else:
                preferred_location = preferred_location

            # Preffered time
            workout_length = form.cleaned_data.get('workout_length') 
            if not workout_length:
                workout_length = preferences.preferred_workout_time
            else:
                workout_length = workout_length

            payload_text = (
                f"Imagine you are a personal trainer. Create a unique and challenging workout plan for the one {form.cleaned_data.get('plan_duration')} "
                f"tailored to the individual's current fitness goals and workout frequency. Avoid repetition of past exercises while ensuring a focus on "
                f"under-targeted muscle groups based on workout history and user preference.\n\n"
                
                # Personal Info Section
                f"--- Personal Info ---\n" +
                (f"Fitness Goals: {', '.join(preferences.fitness_goals)}\n" if preferences.fitness_goals else "") +
                f"Preferred Workout Type: {preferred_workout_type}\n"
                f"Workout should not take longer than: {workout_length} minutes\n"+
                (f"Preferred Workout Intensity: {preferences.preferred_workout_intensity}\n" if preferences.preferred_workout_intensity else "") +
                (f"Fitness Level: {preferences.fitness_level}\n" if preferences.fitness_level else "") +
                f"Workouts Per Week: {preferences.workouts_per_week}\n" +
                (f"Current injuries to consider: {preferences.current_injuries}\n" if preferences.current_injuries else "") +
                (f"Specific Muscle Groups to Focus on: {safe_join(preferences.specific_muscle_groups)}\n" if preferences.specific_muscle_groups else "") +
                (f"Cardio Preferences: {safe_join(preferences.cardio_preferences)}\n" if preferences.cardio_preferences else "") +
                (f"Recovery and Rest: {safe_join(preferences.recovery_and_rest)}\n" if preferences.recovery_and_rest and form.cleaned_data.get('plan_duration') == 'One Week' else "")
                
                # Workout Location & Equipment
                + f"\n--- Workout Location & Available Equipment ---\n"
                + f"Location: {preferred_location.name}\n"
                + "Equipment:\n"
                + "\n".join([f"  - {equipment.equipment}" for equipment in preferred_location.equipment.all()]) +
                
                # Weight History Section
                f"\n\n--- Weight History ---\n" +
                "\n".join([f"  - Date: {entry.date}, Weight: {entry.weight} kg, BMI: {entry.bmi}" for entry in weight_history]) +
                
                # Past Workouts Section
                "\n\n--- Past Workouts ---\n"
                + "\n".join(
                    [
                        f"  - Date: {session.date}\n    Type: {session.workout_type}\n    Duration: {session.time_taken} mins\n    Difficulty: {session.difficulty_rating}\n"
                        "    Exercises:\n" +
                        "\n".join(
                            [
                                f"      - {exercise.name}: Sets {exercise.sets}, Reps {exercise.reps}, Weight: {exercise.actual_weight or 'Bodyweight'}"
                                for exercise in session.exercises.all()
                            ]
                        )
                        for session in workout_sessions
                    ]
                ) +
                # Structured Workout Plan
                f"\n\n--- Structured Workout Plan ---\n"
                f"Please return the workout details with the following structure:\n"
                f"{{\n"
                f"  \"name\": \"Workout Name\",\n"
                f"  \"goal\": \"Goal of the workout\",\n"
                f"  \"exercises\": [\n"
                f"    {{\n"
                f"      \"name\": \"Exercise Name\",\n"
                f"      \"sets\": 3,\n"
                f"      \"reps\": 12,\n"
                f"      \"description\": \"Exercise description\"\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"warm_up\": \"Warm-up details\",\n"
                f"  \"cool_down\": \"Cool-down details\",\n"
                f"  \"important_considerations\": \"Important considerations\",\n"
                f"  \"explanation\": \"Detailed explanation of the workout\"\n"
                f"}}\n"
                f"Ensure that each exercise has a \"name\", \"sets\", \"reps\", and \"description\". If any field is not relevant, leave it empty or null.\n"
            )

            # Send request to Gemini API
            api_key = os.getenv('GEMINI_API')
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(payload_text)
        

            try:
                print("###### RESPONSE #####")
                print(response)
                print(response.text)
                print(type(response))
                # response = 'hi'#response = model.generate_content(payload_text)
                # response = requests.post(gemini_url, data={"payload": payload_text}, headers=headers)
                if response.status_code == 200:
                    request.session['workout_plan'] = response.text  # Directly save text if response is plain text
                    return redirect('workout_plan_result')
                else:
                    return JsonResponse({"error": "Failed to generate workout plan", "details": response.text}, status=response.status_code)
            except requests.exceptions.RequestException as e:
                return JsonResponse({"error": f"Error sending request to Gemini: {str(e)}"}, status=500)

    else:
        form = WorkoutPlanForm()

    # return render(request, 'generate_workout.html', {'form': form})
    return render(request, 'form_template.html', {
        'form': form,
        'form_title': 'Workout',
        'form_id': 'workout-form',
    })

# View for creating a new location
def location_create(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('location_list')  # Redirect to a location list or detail page after saving
    else:
        form = LocationForm()
    # return render(request, 'location_form.html', {'form': form, 'action': 'Create'})
    return render(request, 'form_template.html', {
        'form': form,
        'form_title': 'Add Location',
        'form_id': 'location-form',
        'action': 'Create',
    })



# View for updating an existing location
def location_update(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('location_list')  # Redirect to a location list or detail page after saving
    else:
        form = LocationForm(instance=location)
    # return render(request, 'location_form.html', {'form': form, 'action': 'Update'})
    return render(request, 'form_template.html', {
        'form': form,
        'form_title': 'Edit Location',
        'form_id': 'location-update-form',
        'action': 'Update',
    })


