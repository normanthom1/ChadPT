# populate_dummy_data.py

from django.contrib.auth import get_user_model
from datetime import timedelta, date
import random
from trainer.models import Equipment, Location, UserPreference, WeightHistory, WorkoutSession, WarmUp, CoolDown, Exercise, CardioExercise

User = get_user_model()

# Create or get the user
try:
    user, created = User.objects.get_or_create(
        email="tom@gmail.com",
        defaults={"username": "tom_user", "first_name": "Tom", "last_name": "User"}
    )
    if created:
        user.set_password("secure_password123")
        user.save()
        print(f"Created new user: {user.username}")
    else:
        print(f"User with email tom@gmail.com already exists.")
except Exception as e:
    print(f"Error creating or fetching user: {e}")

# Create User Preferences for Tom
try:
    preferences, created = UserPreference.objects.get_or_create(
        user=user,
        defaults={
            "firstname": "Tom",
            "lastname": "User",
            "dob": date(1987, 6, 15),
            "workout_preferences": ["Crossfit", "HIIT"],
            "preferred_workout_time": "1 hour",
            "fitness_goals": ["Build muscle", "Increase endurance"],
            "workouts_per_week": 5,
        }
    )
    if created:
        print("Created user preferences for Tom.")
    else:
        print("User preferences for Tom already exist.")
except Exception as e:
    print(f"Error creating user preferences: {e}")

# Dummy data for Equipment
equipment_data = [
    {"equipment": "Dumbbell", "equipment_type": "Weights"},
    {"equipment": "Treadmill", "equipment_type": "Cardio"},
    {"equipment": "Exercise Bike", "equipment_type": "Cardio"},
    {"equipment": "Barbell", "equipment_type": "Weights"},
    {"equipment": "Kettlebell", "equipment_type": "Weights"},
    {"equipment": "Rowing Machine", "equipment_type": "Cardio"},
]

for data in equipment_data:
    equipment, created = Equipment.objects.get_or_create(**data)
    if created:
        print(f"Created equipment: {equipment}")

# Dummy data for Locations
location_data = [
    {"name": "Crossfit Gym A", "location_type": "Crossfit Gym", "address": "123 Workout St"},
    {"name": "Park B", "location_type": "Playground", "address": "456 Park Ave"},
    {"name": "F45 Gym C", "location_type": "F45 Gym", "address": "789 Fitness Rd"},
]

for data in location_data:
    location, created = Location.objects.get_or_create(**data)
    if created:
        print(f"Created location: {location}")

# Set initial weight and height for BMI calculation
initial_weight = 75.0  # kg, example starting weight
height_m = 1.75  # meters, example height for BMI calculation

# Calculate BMI
def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)

# Generate weekly WeightHistory entries over the specified timeframe
weight_checkin_date = date(2024, 9, 2)  # Starting in early September
end_date = date(2024, 10, 31)
current_weight = initial_weight

while weight_checkin_date <= end_date:
    try:
        # Slightly adjust weight to simulate natural fluctuations
        current_weight += random.uniform(-0.5, 0.5)
        bmi = calculate_bmi(current_weight, height_m)

        WeightHistory.objects.create(
            user=preferences,
            date=weight_checkin_date,
            weight=round(current_weight, 2),
            bmi=bmi
        )
        print(f"Added weight history entry for {weight_checkin_date}: {current_weight} kg, BMI: {bmi}")

        # Move to the next weekly check-in
        weight_checkin_date += timedelta(weeks=1)
    except Exception as e:
        print(f"Error creating weight history for date {weight_checkin_date}: {e}")

# Dummy data for Workout Sessions with a structured weekly workout plan
workout_start_date = date(2024, 9, 2)  # Starting in early September
current_date = workout_start_date

while current_date <= end_date:
    if current_date.weekday() < 5:  # 5 workouts per week (Monday to Friday)
        try:
            workout_type = [
                "Strength & Power",
                "High-Intensity Intervals",
                "CrossFit Circuit",
                "Endurance & Plyometrics",
                "Cardio & Core Stability"
            ][current_date.weekday() % 5]  # Rotate workout types based on day

            workout = WorkoutSession.objects.create(
                user=preferences,
                date=current_date,
                location=random.choice(Location.objects.all()),
                description=f"{workout_type} routine",
                time_taken=timedelta(hours=1, minutes=random.randint(0, 59)),
                difficulty_rating=random.randint(3, 5),
                enjoyment_rating=random.randint(3, 5),
                workout_type=workout_type,
                muscle_groups=random.sample(["Chest", "Back", "Legs", "Arms", "Core"], 3)
            )
            print(f"Created {workout_type} workout for Tom on {workout.date}")

            # Warm-Up
            warm_up = WarmUp.objects.create(workout=workout, description="5-10 minutes of light cardio and dynamic stretching")
            print(f"Added warm-up for workout on {workout.date}")

            # Cool-Down
            cool_down = CoolDown.objects.create(workout=workout, description="10 minutes of static stretching for full-body relaxation")
            print(f"Added cool-down for workout on {workout.date}")

            # Exercises based on workout type
            if workout_type == "Strength & Power":
                Exercise.objects.create(workout=workout, name="Bench Press", recommended_weight=70, actual_weight=65, reps=8, sets=4)
                Exercise.objects.create(workout=workout, name="Deadlift", recommended_weight=80, actual_weight=75, reps=8, sets=4)
                Exercise.objects.create(workout=workout, name="Weighted Squats", recommended_weight=85, actual_weight=80, reps=8, sets=4)

            elif workout_type == "High-Intensity Intervals":
                Exercise.objects.create(workout=workout, name="Box Jumps", reps=15, sets=5)
                Exercise.objects.create(workout=workout, name="Kettlebell Swings", recommended_weight=20, actual_weight=18, reps=15, sets=5)
                CardioExercise.objects.create(workout=workout, name="Jump Rope", duration=timedelta(minutes=5))

            elif workout_type == "CrossFit Circuit":
                Exercise.objects.create(workout=workout, name="Overhead Press", recommended_weight=35, actual_weight=30, reps=12, sets=4)
                Exercise.objects.create(workout=workout, name="Bent-Over Rows", recommended_weight=60, actual_weight=55, reps=12, sets=4)
                Exercise.objects.create(workout=workout, name="Hanging Leg Raises", reps=15, sets=4)

            elif workout_type == "Endurance & Plyometrics":
                Exercise.objects.create(workout=workout, name="Squat Jumps", reps=15, sets=4)
                Exercise.objects.create(workout=workout, name="Bulgarian Split Squats", reps=12, sets=4, recommended_weight=15, actual_weight=15)
                CardioExercise.objects.create(workout=workout, name="Running", duration=timedelta(minutes=20), distance=5)

            elif workout_type == "Cardio & Core Stability":
                CardioExercise.objects.create(workout=workout, name="Rowing Machine", duration=timedelta(minutes=30), distance=6)
                Exercise.objects.create(workout=workout, name="Plank with Shoulder Taps", reps=30, sets=3)
                Exercise.objects.create(workout=workout, name="Russian Twists", reps=20, sets=3)

        except Exception as e:
            print(f"Error creating {workout_type} workout for date {current_date}: {e}")

    current_date += timedelta(days=1)  # Move to the next day
