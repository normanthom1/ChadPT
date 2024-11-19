# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserPreference, Location, WorkoutSession, Exercise
from .lists_and_dictionaries import (
    FITNESS_GOAL_CHOICES, 
    WORKOUT_PREFERENCE_CHOICES, 
    MUSCLE_GROUP_CHOICES, 
    CARDIO_PREFERENCE_CHOICES, 
    RECOVERY_AND_REST_CHOICES, 
    PLAN_DURATION_CHOICES,
    WORKOUT_TYPE_CHOICES
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'location_type', 'address', 'equipment']
        widgets = {
            'equipment': forms.CheckboxSelectMultiple()  # Allows selection of multiple equipment
        }


class CustomUserCreationForm(UserCreationForm):
    # User fields
    email = forms.EmailField(required=True)
    firstname = forms.CharField(max_length=50)
    lastname = forms.CharField(max_length=50)
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1940, 2025)))

    # Preference fields
    workout_preferences = forms.MultipleChoiceField(
        choices=WORKOUT_PREFERENCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    preferred_workout_time = forms.ChoiceField(
        choices=[('', 'Select Preferred Workout Time')] + [(str(i), f"{i} minutes") for i in range(10, 151, 5)],
        label="Preferred Workout Time",
        required=False
    )
    fitness_goals = forms.MultipleChoiceField(
        choices=FITNESS_GOAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    specific_muscle_groups = forms.MultipleChoiceField(
        choices=MUSCLE_GROUP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    cardio_preferences = forms.MultipleChoiceField(
        choices=CARDIO_PREFERENCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    recovery_and_rest = forms.MultipleChoiceField(
        choices=RECOVERY_AND_REST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    # Update preferred_location to a ModelChoiceField for single location selection
    preferred_location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False)
    
    workouts_per_week = forms.IntegerField(min_value=1, max_value=7)
    current_injuries = forms.CharField(max_length=50)

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2', 'firstname', 'lastname', 'dob', 'current_injuries',
                  'workout_preferences', 'preferred_workout_time', 'fitness_goals',
                  'specific_muscle_groups', 'cardio_preferences', 'recovery_and_rest',
                  'preferred_location', 'workouts_per_week']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            # Create the UserPreference instance
            preferences = UserPreference.objects.create(
                user=user,
                firstname=self.cleaned_data['firstname'],
                lastname=self.cleaned_data['lastname'],
                dob=self.cleaned_data['dob'],
                workout_preferences=self.cleaned_data['workout_preferences'],
                preferred_workout_time=self.cleaned_data['preferred_workout_time'],
                fitness_goals=self.cleaned_data['fitness_goals'],
                workouts_per_week=self.cleaned_data['workouts_per_week'],
                current_injuries=self.cleaned_data['current_injuries'],
                specific_muscle_groups=self.cleaned_data['specific_muscle_groups'],
                cardio_preferences=self.cleaned_data['cardio_preferences'],
                recovery_and_rest=self.cleaned_data['recovery_and_rest'],
                
                # Direct assignment for ForeignKey field preferred_location
                preferred_location=self.cleaned_data['preferred_location'],
            )

        return user



class WorkoutPlanForm(forms.Form):
    
    plan_duration = forms.ChoiceField(
        choices=PLAN_DURATION_CHOICES, 
        label="Select Workout Plan Duration"
    )

    start_date = forms.DateField(
        widget=forms.SelectDateWidget(),
        initial=timezone.now().date()
    )
    
    preferred_location = forms.ModelChoiceField(
        queryset=Location.objects.all(), 
        label="Select Workout Location (Optional)",
        required=False,
        empty_label="Select Workout Location"  # Blank option added here
    )
    
    preferred_workout_type = forms.ChoiceField(
        choices=WORKOUT_TYPE_CHOICES, 
        label="Preferred Workout Type (Optional)",
        required=False
    )
    
    WORKOUT_LENGTH_CHOICES = [('', 'Select Workout Length')] + [(str(i), f"{i} minutes") for i in range(10, 151, 5)]
    
    workout_length = forms.ChoiceField(
        choices=WORKOUT_LENGTH_CHOICES,
        label="Workout Length (Optional)",
        required=False
    )



class UserUpdateForm(forms.ModelForm):
    # CustomUser fields
    # email = forms.EmailField(required=True)
    firstname = forms.CharField(max_length=50)
    lastname = forms.CharField(max_length=50)
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2025)))

    # UserPreference fields
    workout_preferences = forms.MultipleChoiceField(
        choices=WORKOUT_PREFERENCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    preferred_workout_time = forms.ChoiceField(
        choices=[('', 'Select Preferred Workout Time')] + [(str(i), f"{i} minutes") for i in range(10, 151, 5)],
        label="Preferred Workout Time (in minutes)",
        required=False
    )
    fitness_goals = forms.MultipleChoiceField(
        choices=FITNESS_GOAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    specific_muscle_groups = forms.MultipleChoiceField(
        choices=MUSCLE_GROUP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    cardio_preferences = forms.MultipleChoiceField(
        choices=CARDIO_PREFERENCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    recovery_and_rest = forms.MultipleChoiceField(
        choices=RECOVERY_AND_REST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    preferred_location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False)
    workouts_per_week = forms.IntegerField(min_value=1, max_value=7)
    current_injuries = forms.CharField(max_length=50, required=False)

    class Meta:
        model = UserPreference
        fields = [
            'firstname', 'lastname', 'dob', 'current_injuries',
            'workout_preferences', 'preferred_location', 'workouts_per_week', 
            'preferred_workout_time', 'fitness_goals', 'specific_muscle_groups',
            'cardio_preferences', 'recovery_and_rest'
        ]

    def save(self, commit=True):
        # Save CustomUser fields
        user = self.instance.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['firstname']
        user.last_name = self.cleaned_data['lastname']
        if commit:
            user.save()

        # Save UserPreference fields
        return super().save(commit)
    
class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ['difficulty_rating', 'enjoyment_rating', 'complete']

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['actual_weight']

