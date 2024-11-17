from django.db import models
from .lists_and_dictionaries import (
    EQUIPMENT_GROUP_CHOICES, 
    EQUIPMENT_CHOICES, 
    FITNESS_GOAL_CHOICES, 
    WORKOUT_PREFERENCE_CHOICES, 
    WORKOUT_INTENSITY_CHOICES, 
    FITNESS_LEVEL_CHOICES, 
    MUSCLE_GROUP_CHOICES, 
    CARDIO_PREFERENCE_CHOICES, 
    RECOVERY_AND_REST_CHOICES, 
    WORKOUT_TIME_CHOICES,
    QUOTES
)
from django.conf import settings
from .managers import CustomUserManager  # Import the custom manager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()  # Set the custom manager

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Equipment(models.Model):
    """
    Represents various types of equipment available for workouts, allowing
    users to select from predefined options or enter custom equipment. This
    model helps categorize and manage fitness equipment within the application.
    """
    # Field for predefined equipment, with an option to add custom equipment
    equipment = models.CharField(
        max_length=100,
        choices=[(eq[0], eq[0]) for eq in EQUIPMENT_CHOICES],
        blank=True,
        unique=True,
        help_text="Select predefined equipment or leave blank to enter custom equipment."
    )
    custom_equipment = models.CharField(
        max_length=100,
        blank=True,
        help_text="Enter custom equipment if not listed above."
    )
    # Equipment type (group) with predefined choices
    equipment_type = models.CharField(
        max_length=100,
        choices=EQUIPMENT_GROUP_CHOICES,
        blank=False
    )

    def __str__(self):
        return self.custom_equipment if self.custom_equipment else self.equipment

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"

    def save(self, *args, **kwargs):
        if self.custom_equipment:
            self.equipment = ""
        super().save(*args, **kwargs)

class Location(models.Model):
    """
    Represents workout locations, including the type of location, available equipment,
    and a physical address.
    """
    name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=50)
    address = models.CharField(max_length=255, blank=True, null=True)
    equipment = models.ManyToManyField(Equipment, blank=True, related_name='locations')

    def __str__(self):
        return self.name


class UserPreference(models.Model):
    """
    Stores user-specific workout preferences, including preferred workout location,
    type, intensity, and fitness goals.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    dob = models.DateField()
    workout_preferences = models.JSONField(blank=True, null=True)  # e.g., ["Crossfit", "Tabata", "Interval Training"]
    # Adjusting the preferred_workout_time field to match workout_length in model
    # User preference for workout time (length) in minutes
    preferred_workout_time = models.CharField(
        max_length=5,  # Maximum length for minute values like '10', '150'
        choices=WORKOUT_TIME_CHOICES,
        blank=True,
        null=True,
    )
    fitness_goals = models.JSONField(blank=True, null=True)  # e.g., ["Increase strength", "Improve endurance"]
    workouts_per_week = models.PositiveIntegerField(blank=True, null=True)
    current_injuries = models.CharField(max_length=50, blank=True, null=True)
    preferred_workout_intensity = models.CharField(
        max_length=10,
        choices=WORKOUT_INTENSITY_CHOICES,
        default='Moderate',
        blank=True,
    )
    fitness_level = models.CharField(
        max_length=12,
        choices=FITNESS_LEVEL_CHOICES,
        default='Beginner',
        blank=True,
    )
    preferred_location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        related_name='users',
        blank=True,
    )
    specific_muscle_groups = models.CharField(
        max_length=100,
        choices=MUSCLE_GROUP_CHOICES,
        blank=True,
        null=True,
    )
    cardio_preferences = models.CharField(
        max_length=50,
        choices=CARDIO_PREFERENCE_CHOICES,
        blank=True,
        null=True,
    )
    recovery_and_rest = models.CharField(
        max_length=20,
        choices=RECOVERY_AND_REST_CHOICES,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

class WeightHistory(models.Model):
    user = models.ForeignKey(UserPreference, on_delete=models.CASCADE, related_name='weight_history')
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # in kg
    bmi = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        ordering = ['-date']

class Query(models.Model):
    group_id = models.CharField(max_length=20)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_query')
    query = models.CharField(max_length=2000)


class WorkoutSession(models.Model):
    group_id = models.CharField(max_length=20)
    user = models.ForeignKey(UserPreference, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=100, null=True)
    goal = models.CharField(max_length=400, null=True)
    considerations = models.CharField(max_length=400, null=True)
    explanation = models.CharField(max_length=400, null=True)
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='workouts')
    description = models.TextField()  # e.g., "Complete each exercise in traditional sets"
    time_taken = models.DurationField(null=True)  # stores time taken for the workout
    difficulty_rating = models.PositiveIntegerField(null=True)
    enjoyment_rating = models.PositiveIntegerField(null=True)
    workout_type = models.CharField(null=True, max_length=50)  # e.g., "Strength Training"
    muscle_groups = models.JSONField(null=True)  # e.g., ["Chest", "Back", "Legs"]
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Workout on {self.date} - {self.user.firstname}"

class WarmUp(models.Model):
    workout = models.OneToOneField(WorkoutSession, on_delete=models.CASCADE, related_name='warm_up')
    description = models.TextField()  # e.g., "Light cardio and dynamic stretching"

class CoolDown(models.Model):
    workout = models.OneToOneField(WorkoutSession, on_delete=models.CASCADE, related_name='cool_down')
    description = models.TextField()  # e.g., "Static stretching and light cardio"


class Exercise(models.Model):
    workout = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=100)
    recommended_weight = models.CharField(max_length=30, blank=True, null=True)
    actual_weight = models.CharField(max_length=30, blank=True, null=True)
    reps = models.TextField(null=True)
    sets = models.TextField(null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return f"{self.name} for {self.workout}"

class CardioExercise(models.Model):
    workout = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='cardio_exercises')
    name = models.CharField(max_length=100)
    duration = models.DurationField()  # e.g., for running
    distance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # e.g., distance for sprints

