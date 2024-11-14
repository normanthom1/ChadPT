from django.db import models
from .equipment_groups import EQUIPMENT_GROUP_CHOICES, EQUIPMENT_CHOICES
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
    FITNESS_GOAL_CHOICES = sorted([
        ('increase_strength', 'Increase Strength'),
        ('improve_muscle_gain', 'Improve Muscle Gain'),
        ('increase_endurance', 'Increase Endurance'),
        ('improve_flexibility', 'Improve Flexibility'),
        ('enhance_mobility', 'Enhance Mobility'),
        ('improve_cardio_health', 'Improve Cardiovascular Health'),
        ('increase_core_strength', 'Increase Core Strength'),
        ('improve_stability', 'Improve Stability'),
        ('improve_balance', 'Improve Balance'),
        ('improve_posture', 'Improve Posture'),
        ('increase_functional_fitness', 'Increase Functional Fitness'),
        ('enhance_athletic_performance', 'Enhance Athletic Performance'),
        ('speed_up_injury_recovery', 'Speed Up Injury Recovery'),
        ('improve_body_composition', 'Improve Body Composition'),
        ('increase_sprint_speed', 'Increase Sprint Speed'),
        ('develop_power', 'Develop Power'),
        ('improve_agility', 'Improve Agility'),
        ('boost_coordination', 'Boost Coordination'),
        ('maintain_healthy_weight', 'Maintain Healthy Weight'),
        ('increase_flexibility_and_strength', 'Increase Flexibility and Strength'),
        ('improve_endurance_racing_performance', 'Improve Endurance Racing Performance'),
        ('enhance_sports_performance', 'Enhance Sports Performance'),
        ('improve_postpartum_recovery', 'Improve Postpartum Recovery'),
        ('optimize_functional_movement', 'Optimize Functional Movement'),
        ('increase_stamina', 'Increase Stamina'),
        ('focus_on_longevity', 'Focus on Longevity'),
        ('master_bodyweight_exercises', 'Master Bodyweight Exercises'),
        ('increase_kickboxing_fitness', 'Increase Kickboxing Fitness'),
        ('improve_boxing_fitness', 'Improve Boxing Fitness'),
        ('improve_aerobics_fitness', 'Improve Aerobics Fitness'),
        ('build_strength_in_bodybuilding', 'Build Strength in Bodybuilding'),
        ('improve_calisthenics_skills', 'Improve Calisthenics Skills'),
        ('improve_powerlifting_skills', 'Improve Powerlifting Skills'),
        ('focus_on_strength_training', 'Focus on Strength Training'),
        ('improve_posture_in_yoga', 'Improve Posture in Yoga'),
        ('boost_flexibility_in_stretching', 'Boost Flexibility in Stretching'),
        ('enhance_walking_fitness', 'Enhance Walking Fitness'),
        ('improve_running_fitness', 'Improve Running Fitness'),
        ('improve_resistance_training', 'Improve Resistance Training'),
        ('focus_on_low_impact_fitness', 'Focus on Low Impact Fitness'),
    ])

    # workout preference choices
    WORKOUT_PREFERENCE_CHOICES = [
        ('aerobics', 'Aerobics'),
        ('barre', 'Barre'),
        ('bodybuilding', 'Bodybuilding'),
        ('bootcamp', 'Bootcamp'),
        ('boxing', 'Boxing'),
        ('calisthenics', 'Calisthenics'),
        ('circuit', 'Circuit Training'),
        ('crossfit', 'CrossFit'),
        ('crossfit_partner', 'CrossFit Partner Workouts'),
        ('cycling', 'Indoor Cycling/Spin'),
        ('f45', 'F45 Training'),
        ('functional', 'Functional Training'),
        ('hiit', 'HIIT (High-Intensity Interval Training)'),
        ('kickboxing', 'Kickboxing'),
        ('mobility', 'Mobility/Flexibility'),
        ('pilates', 'Pilates'),
        ('plyometrics', 'Plyometrics'),
        ('powerlifting', 'Powerlifting'),
        ('strength', 'Strength Training'),
        ('tabata', 'Tabata Training'),
        ('yoga', 'Yoga'),
    ]
    # Preferred Workout Intensity Answers
    LOW = 'Low'
    MODERATE = 'Moderate'
    HIGH = 'High'
    WORKOUT_INTENSITY_CHOICES = [
        (LOW, 'Low'),
        (MODERATE, 'Moderate'),
        (HIGH, 'High'),
    ]

    # Fitness Level Answers
    BEGINNER = 'Beginner'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'
    FITNESS_LEVEL_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced')
    ]

    # Specific Muscle Groups to Focus On
    UPPER_BODY = 'Upper Body'
    LOWER_BODY = 'Lower Body'
    CORE = 'Core'
    FULL_BODY = 'Full Body'
    FULL_BODY_TARGETTED = 'Full Body (Individual Workouts should target specific muscel groups)'
    MUSCLE_GROUP_CHOICES = [
        (UPPER_BODY, 'Upper Body'),
        (LOWER_BODY, 'Lower Body'),
        (CORE, 'Core'),
        (FULL_BODY, 'Full Body'),
        (FULL_BODY_TARGETTED, FULL_BODY_TARGETTED)
    ]

    # Cardio Preferences
    HIIT = 'HIIT'
    MODERATE_INTENSITY = 'Moderate Intensity'
    LOW_IMPACT = 'Low Impact'
    FUNCTIONAL_CIRCUITS = 'Functional/Cardio Circuits'
    CARDIO_PREFERENCE_CHOICES = [
        (HIIT, 'High-Intensity Interval Training (HIIT)'),
        (MODERATE_INTENSITY, 'Moderate Intensity'),
        (LOW_IMPACT, 'Low Impact'),
        (FUNCTIONAL_CIRCUITS, 'Functional/Cardio Circuits'),
    ]

    # Recovery and Rest
    ACTIVE_RECOVERY = 'Active Recovery'
    FULL_REST = 'Full Rest'
    RECOVERY_TECHNIQUES = 'Recovery Techniques'
    RECOVERY_AND_REST_CHOICES = [
        (ACTIVE_RECOVERY, 'Active Recovery Days'),
        (FULL_REST, 'Full Rest Days'),
        (RECOVERY_TECHNIQUES, 'Recovery Techniques'),
    ]

    WORKOUT_TIME_CHOICES = [(str(i), f"{i} minutes") for i in range(10, 151, 5)]
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
        default=MODERATE,
        blank=True,
    )
    fitness_level = models.CharField(
        max_length=12,
        choices=FITNESS_LEVEL_CHOICES,
        default=BEGINNER,
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
    recommended_weight = models.TextField(null=True)
    actual_weight = models.TextField(null=True)
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

