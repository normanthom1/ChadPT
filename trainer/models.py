from django.db import models
from multiselectfield import MultiSelectField
from .lists_and_dictionaries import (
    EQUIPMENT_GROUP_CHOICES, 
    EQUIPMENT_CHOICES, 
    GOAL_CHOICES, 
    WORKOUT_TYPE_PREFERENCE_CHOICES,  
    FITNESS_LEVEL_CHOICES, 
    WORKOUT_TIME_CHOICES,
    GENDER_CHOICES,
    WORKOUT_TYPE_PREFERENCE_CHOICES,
    GOAL_CHOICES,
    DAYS_OF_WEEK_CHOICES,
    EATING_HABITS_CHOICES
)

from decimal import Decimal
from datetime import date
from django.conf import settings
from .managers import CustomUserManager  # Import the custom manager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    # first_name = models.CharField(max_length=30)
    # last_name = models.CharField(max_length=30)
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
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        help_text="Select your gender."
    )
    dob = models.DateField()
    height = models.IntegerField(
        validators=[
            MinValueValidator(50),
            MaxValueValidator(300)
        ],
        help_text="Enter height in centimeters. Must be between 50 and 300.")
    workout_type_preference = models.CharField(
        max_length=20,
        choices=WORKOUT_TYPE_PREFERENCE_CHOICES,
        # default='functional',
        help_text='Select your workout type preference.'
    )

    fitness_goals = MultiSelectField(
        choices=GOAL_CHOICES,
        help_text='What would you like Chad to help you with?'
    )

    fitness_level = models.CharField(
        max_length=12,
        choices=FITNESS_LEVEL_CHOICES,
        default='Beginner',
        blank=True,
    )

    eating_habits = models.CharField(
        max_length=10,
        choices=EATING_HABITS_CHOICES,
        default='average',  # Default to 'Average'
    )

    workout_days = MultiSelectField(choices=DAYS_OF_WEEK_CHOICES, 
                                    default=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
                                    blank=True)

    preferred_location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        related_name='users'
    )
    
    preferred_workout_duration = models.CharField(
        max_length=5,  # Maximum length for minute values like '10', '150'
        choices=WORKOUT_TIME_CHOICES,
    )

    @property
    def age(self):
        """
        Calculate the user's age based on their date of birth (dob).
        """
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - (
                (today.month, today.day) < (self.dob.month, self.dob.day)
            )
        return None

    @property
    def bmi(self):
        """
        Calculate the user's BMI based on their most recent weight and height.
        """
        try:
            # Get the most recent weight entry
            latest_weight_entry = self.weight_history.first()
            if not latest_weight_entry or not self.height:
                return None
            
            weight = latest_weight_entry.weight  # in kg
            height_in_meters = self.height / 100  # convert cm to meters

            # Calculate BMI
            return round(float(weight) / (height_in_meters ** 2), 2)
        except Exception as e:
            print(f"Error calculating BMI: {e}")
            return None

    def __str__(self):
        return f"{self.user} Preferences"
    
class WeightHistory(models.Model):
    user = models.ForeignKey(UserPreference, on_delete=models.CASCADE, related_name='weight_history')
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # in kg

    @property
    def bmi(self):
        """
        Calculate the BMI for this weight entry using the user's height.
        """
        if not self.user.height:
            return None  # Height is required for BMI calculation
        
        try:
            height_in_meters = self.user.height / 100  # Convert height from cm to meters
            return round(float(self.weight) / (height_in_meters ** 2), 2)
        except Exception as e:
            print(f"Error calculating BMI for WeightHistory ID {self.id}: {e}")
            return None

    class Meta:
        ordering = ['-date']

class Query(models.Model):
    group_id = models.CharField(max_length=20)
    user = models.ForeignKey(UserPreference, on_delete=models.CASCADE, related_name='user_query')
    query = models.CharField(max_length=2000)


class WorkoutSession(models.Model):
    group_id = models.CharField(max_length=20)
    user = models.ForeignKey(UserPreference, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=100, null=True)
    goal = models.CharField(max_length=400, null=True)
    # considerations = models.CharField(max_length=400, null=True)
    explanation = models.CharField(max_length=400, null=True)
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='workouts')
    description = models.TextField()  # e.g., "Complete each exercise in traditional sets"
    # time_taken = models.DurationField(null=True)  # stores time taken for the workout
    # difficulty_rating = models.PositiveIntegerField(null=True)
    # enjoyment_rating = models.PositiveIntegerField(null=True)
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

