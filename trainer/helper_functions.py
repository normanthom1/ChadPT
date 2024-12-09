from dotenv import load_dotenv
from pathlib import Path
import os
import random
import json
import google.generativeai as genai
import requests
import re
import datetime
from . models import Location
import json
from datetime import date

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

def get_value_from_choices(key, choices):
    """
    Retrieve the value corresponding to a given key from a list of tuples.

    Args:
        key (str): The key to search for in the list of tuples.
        choices (list): A list of tuples where each tuple contains a key-value pair.

    Returns:
        str: The value corresponding to the key if found, otherwise None.
    """
    for choice_key, choice_value in choices:
        if choice_key == key:
            return choice_value
    return None



def replace_text(text, new_date):
    # Replace the date in the format YYYY-MM-DD
    text = re.sub(r'The workout should start on \d{4}-\d{2}-\d{2}', f'The workout should start on {new_date}', text)
    
    # Replace 'one day tailored' with 'one week tailored' if it exists in the text
    text = re.sub(r'one week tailored', 'one day tailored', text)
    
    return text

def generate_random_id():
    """Generates a random 20-digit ID."""
    return ''.join([str(random.randint(0, 9)) for _ in range(20)])


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


import json
import re

def convert_text_to_json(text):
    """
    Converts a JSON-like text input to a Python object.

    Args:
        text (str): A string containing JSON-formatted data, possibly wrapped in delimiters.

    Returns:
        dict or list: A Python object (e.g., list or dictionary) parsed from the JSON text.

    Raises:
        ValueError: If the input text is not valid JSON or is empty.
    """
    # Check if the text is empty or None
    if not text or not text.strip():
        raise ValueError("Input text is empty or invalid.")
    
    try:
        # Normalize and remove common wrappers such as backticks or markers
        sanitized_text = text.strip()
        
        # Remove ```json or ``` if present
        if sanitized_text.startswith("```json") or sanitized_text.startswith("```"):
            sanitized_text = sanitized_text.lstrip("```json").lstrip("```").strip()
        
        # Remove ending backticks if present
        if sanitized_text.endswith("```"):
            sanitized_text = sanitized_text.rstrip("```").strip()
        
        # Fix invalid JSON (e.g., unquoted strings in values)
        sanitized_text = re.sub(r'(?<="reps": )([^",\]}]+)', r'"\1"', sanitized_text)
        
        # Parse the sanitized JSON
        return json.loads(sanitized_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}\nInput text: {sanitized_text[:2000]}...")

    
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)




def personal_details_dict(preferences):
        GOAL_CHOICES_DICT = dict(GOAL_CHOICES)
        # Ensure `fitness_goals` is converted into a list of strings
        fitness_goals_list = preferences.fitness_goals or []

        # Map fitness goals to their descriptions
        mapped_fitness_goals = [
            GOAL_CHOICES_DICT.get(goal.strip(), goal.strip())
            for goal in fitness_goals_list
        ]

        DAYS_OF_WEEK_CHOICES_DICT = dict(DAYS_OF_WEEK_CHOICES)
        # Ensure `fitness_goals` is converted into a list of strings
        days_of_week_list = preferences.workout_days or []

        # Map fitness goals to their descriptions
        mapped_days_of_week = [
            DAYS_OF_WEEK_CHOICES_DICT.get(day.strip(), day.strip())
            for day in days_of_week_list
        ]

        WORKOUT_TYPE_PREFERENCE_DICT = dict(WORKOUT_TYPE_PREFERENCE_CHOICES)
        workout_type_description = WORKOUT_TYPE_PREFERENCE_DICT.get(preferences.workout_type_preference, preferences.workout_type_preference)

        EATING_HABITS_CHOICES_DICT = dict(EATING_HABITS_CHOICES)
        eating_habit_description = EATING_HABITS_CHOICES_DICT.get(preferences.eating_habits, preferences.eating_habits)

        FITNESS_LEVEL_CHOICES_DICT = dict(FITNESS_LEVEL_CHOICES)
        fitness_level_description = FITNESS_LEVEL_CHOICES_DICT.get(preferences.fitness_level, preferences.fitness_level)


        user_details = {
            "firstname": preferences.firstname,
            "lastname": preferences.lastname,
            "dob": preferences.dob,
            "age": preferences.age,  # Calculated field
            "height": preferences.height,
            "bmi": preferences.bmi,  # Calculated field
            "gender": preferences.gender,
            "fitness_level": fitness_level_description,
            "eating_habits": eating_habit_description,
            "workout_type_preference": workout_type_description,  # Correctly join list items
            "preferred_location": preferences.preferred_location.name if preferences.preferred_location else "Not specified",
            "preferred_workout_duration": preferences.preferred_workout_duration,
            "fitness_goals": mapped_fitness_goals,  # Correctly join list items
            "workout_days": mapped_days_of_week,
        }
        return user_details


def workout_payload_text(
    plan_duration_value,
    start_date,
    preferences,
    preferred_workout_type,
    workout_length,
    location,
    weight_history,
    workout_sessions,
    ):
    """
    Generates a personalized workout plan payload as a formatted text.

    Args:
        plan_duration_value (str): Duration of the workout plan.
        start_date (str): Starting date for the workout plan.
        preferences (object): User preferences including fitness goals, intensity, etc.
        preferred_workout_type (str): Preferred type of workout.
        workout_length (int): Maximum workout duration in minutes.
        preferred_location (object): Location and available equipment details.
        weight_history (list): List of weight history entries.
        workout_sessions (list): List of past workout sessions.
        safe_join (callable): A utility function to safely join list items.

    Returns:
        str: A formatted workout plan payload text.
    """
    location = Location.objects.get(name=location)


    days = ', '.join([i.title() for i in preferences.workout_days])
    # print([get_value_from_choices(i, FITNESS_LEVEL_CHOICES) for i in preferences.fitness_goals])
    fitness_goals_desc = '\n - '.join([get_value_from_choices(i, GOAL_CHOICES) for i in preferences.fitness_goals])
    preferred_workout_type_desc = get_value_from_choices(preferred_workout_type, WORKOUT_TYPE_PREFERENCE_CHOICES)
    fitness_level_desc = get_value_from_choices(preferences.fitness_level, FITNESS_LEVEL_CHOICES)

    payload_text = (
        f"Imagine you are a personal trainer. Create a unique and challenging workout plan for one {plan_duration_value} "
        f"tailored to the individual's current fitness goals and workout frequency. The workout should "
        f"start on {start_date}. Take into account the users Personal Info, Workout Location & Available Equipment," 
        f"Fitness, Level Age and BMI and Past Workouts below.\n\n"
        f"--- Personal Info ---\n"
        + f"Fitness Goals:\n{fitness_goals_desc}\n"
        + f"Preferred Workout Type: {preferred_workout_type_desc}\n"
        + f"Workout should not take longer than: {workout_length} minutes\n"
        + f"Workouts should take place on these days: {days}, and there should be no more than {len(preferences.workout_days)} workouts per week"    
        + f"\n\n--- Workout Location & Available Equipment ---\n"
        + f"Location: {location.name}\n"
        + "Available Equipment for the Workout:\n"
        + "\n".join([f"  - {equipment.equipment}" for equipment in location.equipment.all()])
        + f"\n\n--- Fitness Level Age and BMI ---\n"
        + f"{fitness_level_desc}\n"
        + f"Age: {preferences.age}\n"
        + f"--- Weight History ---\n"
        + "\n".join([f"  - Date: {entry.date}, Weight: {entry.weight} kg, BMI: {entry.bmi}" for entry in weight_history])
        + "\n\n--- Past Workouts ---\n"
        + f"Make sure that the new workout plan takes into account past workouts below "
        + f"so that muscel groups are not overused and workouts are challenging and varied.\n"
        + "\n".join(
            [
                f"  - Date: {session.date}\n    Type: {session.workout_type}\n"
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
    )
    return payload_text

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
