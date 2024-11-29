from datetime import date, timedelta
import random
from django.core.management.base import BaseCommand
from trainer.models import (
    CustomUser,
    UserPreference,
    Location,
    WorkoutSession,
    WarmUp,
    CoolDown,
    Exercise,
)

class Command(BaseCommand):
    help = "Create 20 workouts for a specific user"

    def handle(self, *args, **kwargs):
        # Debugging dates
        today = date(2024, 11, 3)
        end_date = date(2024, 11, 26)
        self.stdout.write(self.style.WARNING(f"Today: {today}, End Date: {end_date}"))

        # # Ensure date range is valid
        # if today >= end_date:
        #     self.stdout.write(self.style.ERROR("Error: The end date must be in the future."))
        #     return

        # Fetch user and preferences
        try:
            user = CustomUser.objects.get(email="tom@gmail.com")
            preferences = UserPreference.objects.get(user=user)
            location = Location.objects.first()  # Default to the first location; adjust if needed
        except (CustomUser.DoesNotExist, UserPreference.DoesNotExist) as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            return

        # Date range for workouts
        days_between = (end_date - today).days
        group_id = f"workout-{random.randint(1000, 9999)}"
        workout_names = [
            "Strength Training", "HIIT", "Cardio", "Yoga", "Pilates", "CrossFit",
            "Cycling", "Swimming", "Running", "Rowing", "Climbing", "Boxing",
            "Martial Arts", "Powerlifting", "Bodybuilding", "Stretching", "Aerobics",
            "Dance", "Hiking", "Sprinting"
        ]

        for i in range(20):
            workout_date = today + timedelta(days=random.randint(1, days_between))
            workout_name = random.choice(workout_names)
            workout_goal = f"Improve {random.choice(['strength', 'endurance', 'flexibility', 'speed', 'agility'])}"

            workout_session = WorkoutSession.objects.create(
                group_id=group_id,
                user=preferences,
                name=workout_name,
                goal=workout_goal,
                explanation=f"Follow the {workout_name} plan.",
                date=workout_date,
                location=location,
                description="Complete the workout with proper form and intensity.",
                workout_type=workout_name,
                muscle_groups=["Legs", "Arms", "Core", "Back", "Chest"],
                complete=False,
            )

            # Add WarmUp
            WarmUp.objects.create(
                workout=workout_session,
                description="5 minutes of light cardio and dynamic stretching."
            )

            # Add CoolDown
            CoolDown.objects.create(
                workout=workout_session,
                description="5 minutes of static stretching and light breathing exercises."
            )

            # Add Exercises
            for j in range(5):  # Create 5 exercises per workout
                Exercise.objects.create(
                    workout=workout_session,
                    name=f"Exercise {j+1}",
                    recommended_weight=f"{random.randint(10, 50)}kg",
                    actual_weight=None,
                    reps=f"{random.randint(8, 15)}",
                    sets=f"{random.randint(3, 5)}",
                    description=f"Perform Exercise {j+1} with controlled movements."
                )

        self.stdout.write(self.style.SUCCESS("20 workouts successfully created!"))
