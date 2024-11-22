from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserPreference, Location, WorkoutSession, Exercise, Equipment, WeightHistory
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
    EATING_HABITS_CHOICES,
    PLAN_DURATION_CHOICES
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

from datetime import date

class CustomUserCreationForm(UserCreationForm):
    # User fields
    email = forms.EmailField(required=True)
    firstname = forms.CharField(max_length=50)
    lastname = forms.CharField(max_length=50)
    height = forms.IntegerField()
    weight = forms.DecimalField(max_digits=5, decimal_places=2, help_text="Enter your weight in kilograms.")  # New field
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1940, 2025)))

    # Preference fields
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        help_text="Select your gender."
    )
    workout_type_preference = forms.ChoiceField(
        choices=WORKOUT_TYPE_PREFERENCE_CHOICES,
        required=False,
        help_text='Select your workout type preference.'
    )
    fitness_goals = forms.MultipleChoiceField(
        choices=GOAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="What are your fitness goals?"
    )
    fitness_level = forms.ChoiceField(
        choices=FITNESS_LEVEL_CHOICES,
        initial='Beginner',
        required=False,
        help_text="What is your fitness level?"
    )
    eating_habits = forms.ChoiceField(
        choices=EATING_HABITS_CHOICES,
        initial='average',
        required=False,
        help_text="What are your eating habits?"
    )
    workout_days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        initial=['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    )
    # Add a field for existing locations
    existing_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select an existing location."
    )

    # Preferred location as a choice between 'existing' and 'new'
    preferred_location = forms.ChoiceField(
        choices=[('existing', 'Choose Existing Location'), ('new', 'Create New Location')],
        widget=forms.RadioSelect,
        help_text="Select your preferred workout location or choose to create a new location."
    )

    new_location_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Location Name'}),
        help_text="If 'Create New Location' is selected, enter the name here."
    )
    new_location_address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Location Address'}),
        help_text="Enter the physical address of the new location."
    )
    new_location_type = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Location Type'}),
        help_text="Enter the type of location (e.g., Gym, Park)."
    )
    new_location_equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select available equipment for the new location."
    )
    preferred_workout_duration = forms.ChoiceField(
        choices=WORKOUT_TIME_CHOICES,
        required=False,
        help_text="Select your preferred workout duration."
    )

    class Meta:
        model = CustomUser
        fields = [
            'email', 'password1', 'password2', 'firstname', 'lastname', 'dob',
            'gender', 'height', 'weight', 'workout_type_preference', 'fitness_goals', 'fitness_level',
            'eating_habits', 'workout_days', 'preferred_location', 'existing_location',
            'new_location_name', 'new_location_address', 'new_location_type',
            'new_location_equipment', 'preferred_workout_duration'
        ]

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
                gender=self.cleaned_data['gender'],
                height=self.cleaned_data['height'],
                workout_type_preference=self.cleaned_data['workout_type_preference'],
                fitness_goals=self.cleaned_data['fitness_goals'],
                fitness_level=self.cleaned_data['fitness_level'],
                eating_habits=self.cleaned_data['eating_habits'],
                workout_days=self.cleaned_data['workout_days'],
                preferred_workout_duration=self.cleaned_data['preferred_workout_duration'],
            )

            preferred_location = self.cleaned_data.get('preferred_location')

            if preferred_location == 'new':
                # Create a new location
                new_location = Location.objects.create(
                    name=self.cleaned_data['new_location_name'],
                    location_type=self.cleaned_data['new_location_type'],
                    address=self.cleaned_data['new_location_address']
                )
                new_location.equipment.set(self.cleaned_data.get('new_location_equipment', []))
                preferences.preferred_location = new_location
            elif preferred_location == 'existing':
                # Use an existing location
                preferences.preferred_location = self.cleaned_data['existing_location']

            preferences.save()

            # Create the WeightHistory instance
            WeightHistory.objects.create(
                user=preferences,
                date=date.today(),
                weight=self.cleaned_data['weight']
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
        choices=WORKOUT_TYPE_PREFERENCE_CHOICES, 
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
    # Fields for CustomUser
    firstname = forms.CharField(max_length=50, required=True)
    lastname = forms.CharField(max_length=50, required=True)
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2025)), required=True)

    # Fields for UserPreference
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        help_text="Select your gender.",
        required=True
    )
    workout_type_preference = forms.ChoiceField(
        choices=WORKOUT_TYPE_PREFERENCE_CHOICES,
        required=False,
        help_text="Select your workout type preference."
    )
    fitness_goals = forms.MultipleChoiceField(
        choices=GOAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="What are your fitness goals?"
    )
    fitness_level = forms.ChoiceField(
        choices=FITNESS_LEVEL_CHOICES,
        initial='Beginner',
        required=False,
        help_text="What is your fitness level?"
    )
    eating_habits = forms.ChoiceField(
        choices=EATING_HABITS_CHOICES,
        initial='average',
        required=False,
        help_text="What are your eating habits?"
    )
    workout_days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        initial=['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    )
    preferred_location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        help_text="Select your preferred workout location."
    )
    preferred_workout_duration = forms.ChoiceField(
        choices=WORKOUT_TIME_CHOICES,
        required=False,
        help_text="Select your preferred workout duration."
    )

    class Meta:
        model = UserPreference
        fields = [
            'firstname', 'lastname', 'dob', 'gender', 'workout_type_preference', 
            'fitness_goals', 'fitness_level', 'eating_habits', 'workout_days',
            'preferred_location', 'preferred_workout_duration',
        ]

    def save(self, commit=True):
        # Save changes to the associated CustomUser instance
        user = self.instance.user
        user.first_name = self.cleaned_data['firstname']
        user.last_name = self.cleaned_data['lastname']
        if commit:
            user.save()

        # Save UserPreference instance
        user_preference = super().save(commit=False)
        if commit:
            user_preference.save()
        return user_preference

    
class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ['difficulty_rating', 'enjoyment_rating', 'complete']

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['actual_weight']

