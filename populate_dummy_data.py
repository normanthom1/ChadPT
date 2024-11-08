# populate_dummy_data.py

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from datetime import timedelta, date
import random
from trainer.models import Equipment, Location, UserPreference, WeightHistory, WorkoutSession, WarmUp, CoolDown, Exercise, CardioExercise

# Define the CustomUser model
User = get_user_model()

# List of users to populate
user_data = [
    {
        "email": "alice.smith@example.com",
        "username": "alice_smith",
        "password": "password123",
        "first_name": "Alice",
        "last_name": "Smith"
    },
    {
        "email": "bob.jones@example.com",
        "username": "bob_jones",
        "password": "password123",
        "first_name": "Bob",
        "last_name": "Jones"
    },
    {
        "email": "charlie.brown@example.com",
        "username": "charlie_brown",
        "password": "password123",
        "first_name": "Charlie",
        "last_name": "Brown"
    },
]

# Populate users
for data in user_data:
    try:
        # Use email to look up existing users and set unique username
        user, created = User.objects.get_or_create(
            email=data["email"],
            defaults={
                "username": data["username"],  # unique username for each user
                "first_name": data["first_name"],
                "last_name": data["last_name"],
            }
        )
        
        if created:
            # Set password securely if the user is newly created
            user.set_password(data["password"])
            user.save()
            print(f"Created new user: {user.username}")
        else:
            print(f"User with email {data['email']} already exists: {user.username}")

    except IntegrityError as e:
        print(f"Error creating user {data['email']}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Dummy data for Equipment
equipment_data = [
    {"equipment": "Dumbbell", "equipment_type": "Weights"},
    {"equipment": "Treadmill", "equipment_type": "Cardio"},
    {"equipment": "Exercise Bike", "equipment_type": "Cardio"},
    {"equipment": "Barbell", "equipment_type": "Weights"},
    {"equipment": "Kettlebell", "equipment_type": "Weights"},
]

for data in equipment_data:
    equipment, created = Equipment.objects.get_or_create(**data)
    if created:
        print(f"Created equipment: {equipment}")

# Dummy data for Locations
location_data = [
    {"name": "Gym A", "location_type": "Indoor", "address": "123 Main St"},
    {"name": "Park B", "location_type": "Outdoor", "address": "456 Park Ave"},
    {"name": "Fitness Center C", "location_type": "Indoor", "address": "789 Fitness Rd"},
]

for data in location_data:
    location, created = Location.objects.get_or_create(**data)
    if created:
        print(f"Created location: {location}")

# Dummy data for UserPreferences
preferences_data = [
    {
        "user": user_data[0]["email"],  # Linking to user by email
        "firstname": "Alice",
        "lastname": "Smith",
        "dob": date(1990, 5, 20),
        "workout_preferences": ["Crossfit", "Yoga"],
        "preferred_workout_time": "Morning",
        "fitness_goals": ["Increase strength", "Improve endurance"],
        "workouts_per_week": 4
    },
    {
        "user": user_data[1]["email"],
        "firstname": "Bob",
        "lastname": "Jones",
        "dob": date(1985, 3, 15),
        "workout_preferences": ["Running", "HIIT"],
        "preferred_workout_time": "Evening",
        "fitness_goals": ["Lose weight"],
        "workouts_per_week": 3
    },
]

for data in preferences_data:
    user = User.objects.get(email=data.pop("user"))
    preference, created = UserPreference.objects.get_or_create(user=user, defaults=data)
    if created:
        print(f"Created user preference for: {preference}")

# Dummy data for WeightHistory
for user_pref in UserPreference.objects.all():
    for i in range(5):  # Creating 5 weight entries
        WeightHistory.objects.create(
            user=user_pref,
            date=date.today() - timedelta(days=i * 30),  # Monthly entries
            weight=random.uniform(60, 100),  # Random weight
            bmi=random.uniform(18.5, 30)  # Random BMI within healthy range
        )
        print(f"Created weight history for {user_pref.user.email}")

# Dummy data for WorkoutSession
for user_pref in UserPreference.objects.all():
    for i in range(3):  # Creating 3 workout sessions for each user
        workout = WorkoutSession.objects.create(
            user=user_pref,
            date=date.today() - timedelta(days=i * 7),  # Weekly workouts
            location=random.choice(Location.objects.all()),  # Random location
            description="Full body workout session.",
            time_taken=timedelta(hours=1, minutes=random.randint(0, 59)),
            difficulty_rating=random.randint(1, 5),
            enjoyment_rating=random.randint(1, 5),
            workout_type=random.choice(["Strength", "Cardio", "Flexibility"]),
            muscle_groups=random.sample(["Chest", "Back", "Legs", "Arms", "Core"], 3)  # Random muscle groups
        )
        print(f"Created workout session for {user_pref.user.email}: {workout}")

        # Create WarmUp and CoolDown for each session
        warm_up = WarmUp.objects.create(workout=workout, description="Dynamic stretching and light cardio.")
        cool_down = CoolDown.objects.create(workout=workout, description="Static stretching and relaxation.")
        print(f"Created warm-up and cool-down for workout on {workout.date}")

        # Create Exercises and CardioExercises for each session
        for j in range(2):  # 2 strength exercises
            Exercise.objects.create(
                workout=workout,
                name=f"Strength Exercise {j + 1}",
                recommended_weight=random.uniform(5, 100),
                actual_weight=random.uniform(5, 100),
                reps=random.randint(8, 15),
                sets=random.randint(3, 5)
            )
            print(f"Created strength exercise for workout on {workout.date}")

        for j in range(2):  # 2 cardio exercises
            CardioExercise.objects.create(
                workout=workout,
                name=f"Cardio Exercise {j + 1}",
                duration=timedelta(minutes=random.randint(15, 60)),  # Duration between 15-60 mins
                distance=random.uniform(1, 10)  # Distance in km
            )
            print(f"Created cardio exercise for workout on {workout.date}")
