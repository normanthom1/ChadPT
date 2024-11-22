from dotenv import load_dotenv
from pathlib import Path
import os
import random
import json
import google.generativeai as genai
import requests
import re
import datetime

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

    
# def convert_text_to_json(text):
#     """
#     Converts a given text to a JSON object after removing backticks and unnecessary prefixes.
#     """
#     clean_text = text.strip('`').rstrip()
    
#     # Check for "json" prefix and remove it
#     if clean_text.lower().startswith("json"):
#         clean_text = clean_text[4:].strip()
    
#     # Clean up any remaining unnecessary parts (like extra backticks or unwanted characters)
#     cleaned_text = clean_text.replace('{{', '{').replace('}}', '}')
#     cleaned_text = cleaned_text.strip('`')  # Strip any remaining backticks at the ends
    
#     # Attempt to load the cleaned text as JSON
#     try:
#         parsed_json = json.loads(cleaned_text)
#         print(parsed_json)  # Log the successfully parsed JSON
#         return parsed_json
#     except json.JSONDecodeError as e:
#         print("Error decoding JSON:", e)
#         print("Failed text:", cleaned_text)  # Log the problematic text
#         return None
    
import json



def convert_text_to_json(text):
    try:
        # Replace potential problematic characters (e.g., unquoted values like 5-8 repetitions)
        sanitized_text = text.replace("5-8 repetitions", "\"5-8 repetitions\"")
        return json.loads(sanitized_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    
from datetime import date
    
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def workout_payload_text(
    plan_duration_value,
    start_date,
    preferences,
    preferred_workout_type,
    workout_length,
    preferred_location,
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

    Returns:
        str: A formatted workout plan payload text.
    """
    import json

    payload_text = {
        "plan_duration": plan_duration_value,
        "start_date": start_date.isoformat() if isinstance(start_date, (str, object)) else start_date,
        "preferences": {
            "fitness_goals": preferences.fitness_goals if preferences.fitness_goals else [],
            "workout_type": preferred_workout_type,
            "workout_length": workout_length,
            "workout_intensity": preferences.preferred_workout_intensity if preferences.preferred_workout_intensity else None,
            "fitness_level": preferences.fitness_level if preferences.fitness_level else None,
            "workouts_per_week": preferences.workouts_per_week,
            "current_injuries": preferences.current_injuries if preferences.current_injuries else None,
            "muscle_focus": preferences.specific_muscle_groups if preferences.specific_muscle_groups else [],
            "cardio_preferences": preferences.cardio_preferences if preferences.cardio_preferences else [],
        },
        "location": {
            "name": preferred_location,
            "equipment": [equipment.equipment for equipment in preferred_location.equipment.all()],
        },
        "weight_history": [
            {"date": entry.date, "weight": entry.weight, "bmi": entry.bmi} for entry in weight_history
        ],
        "past_workouts": [
            {
                "date": session.date,
                "type": session.workout_type,
                "duration": session.time_taken,
                "difficulty": session.difficulty_rating,
                "exercises": [
                    {
                        "name": exercise.name,
                        "sets": exercise.sets,
                        "reps": exercise.reps,
                        "actual_weight": exercise.actual_weight or "Bodyweight",
                    }
                    for exercise in session.exercises.all()
                ],
            }
            for session in workout_sessions
        ],
        "structured_workout_plan": [
            {
                "name": "Workout Name",
                "goal": "Goal of the workout",
                "muscle_group": "Muscle group worked",
                "location": "Location of workout",
                "date": start_date,
                "exercises": [
                    {
                        "name": "Exercise Name",
                        "sets": 3,
                        "reps": "10 per leg",
                        "recommended_weight": "10 kg",
                        "description": "Exercise description",
                    }
                ],
                "warm_up": "Warm-up details",
                "cool_down": "Cool-down details",
                "important_considerations": "Important considerations",
                "explanation": "Detailed explanation of the workout",
            }
        ],
    }

    # Convert to formatted JSON string
    return json.dumps(payload_text, indent=2, cls=CustomJSONEncoder)


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


# def workout_payload_text(
#     plan_duration_value,
#     start_date,
#     preferences,
#     preferred_workout_type,
#     workout_length,
#     preferred_location,
#     weight_history,
#     workout_sessions,
#     ):
#     """
#     Generates a personalized workout plan payload as a formatted text.

#     Args:
#         plan_duration_value (str): Duration of the workout plan.
#         start_date (str): Starting date for the workout plan.
#         preferences (object): User preferences including fitness goals, intensity, etc.
#         preferred_workout_type (str): Preferred type of workout.
#         workout_length (int): Maximum workout duration in minutes.
#         preferred_location (object): Location and available equipment details.
#         weight_history (list): List of weight history entries.
#         workout_sessions (list): List of past workout sessions.
#         safe_join (callable): A utility function to safely join list items.

#     Returns:
#         str: A formatted workout plan payload text.
#     """
#     payload_text = (
#         f"Imagine you are a personal trainer. Create a unique and challenging workout plan for one {plan_duration_value} "
#         f"tailored to the individual's current fitness goals and workout frequency. Avoid repetition of past exercises while "
#         f"ensuring a focus on under-targeted muscle groups based on workout history and user preference. The workout should "
#         f"start on {start_date}\n\n"
#         f"--- Personal Info ---\n"
#         + (f"Fitness Goals: {', '.join(preferences.fitness_goals)}\n" if preferences.fitness_goals else "")
#         + f"Preferred Workout Type: {preferred_workout_type}\n"
#         + f"Workout should not take longer than: {workout_length} minutes\n"
#         + (f"Preferred Workout Intensity: {preferences.preferred_workout_intensity}\n" if preferences.preferred_workout_intensity else "")
#         + (f"Fitness Level: {preferences.fitness_level}\n" if preferences.fitness_level else "")
#         + f"Workouts Per Week: {preferences.workouts_per_week}\n"
#         + (f"Current injuries to consider: {preferences.current_injuries}\n" if preferences.current_injuries else "")
#         + (f"Specific Muscle Groups to Focus on: {safe_join(preferences.specific_muscle_groups)}\n" if preferences.specific_muscle_groups else "")
#         + (f"Cardio Preferences: {safe_join(preferences.cardio_preferences)}\n" if preferences.cardio_preferences else "")
#         + (f"Recovery and Rest: {safe_join(preferences.recovery_and_rest)}\n" if preferences.recovery_and_rest and plan_duration_value == 'One Week' else "")
#         + f"\n--- Workout Location & Available Equipment ---\n"
#         + f"Location: {preferred_location.name}\n"
#         + "Available Equipment for the Workout:\n"
#         + "\n".join([f"  - {equipment.equipment}" for equipment in preferred_location.equipment.all()])
#         + f"\n\n--- Weight History ---\n"
#         + "\n".join([f"  - Date: {entry.date}, Weight: {entry.weight} kg, BMI: {entry.bmi}" for entry in weight_history])
#         + "\n\n--- Past Workouts ---\n"
#         + "\n".join(
#             [
#                 f"  - Date: {session.date}\n    Type: {session.workout_type}\n    Duration: {session.time_taken} mins\n    Difficulty: {session.difficulty_rating}\n"
#                 "    Exercises:\n"
#                 + "\n".join(
#                     [
#                         f"      - {exercise.name}: Sets {exercise.sets}, Reps {exercise.reps}, Weight: {exercise.actual_weight or 'Bodyweight'}"
#                         for exercise in session.exercises.all()
#                     ]
#                 )
#                 for session in workout_sessions
#             ]
#         )
#         + f"\n\n--- Structured Workout Plan ---\n"
#         f"Format the entire response as valid JSON as follows:\n"
#         "[{{\n"
#         "  \"name\": \"Workout Name\",\n"
#         "  \"goal\": \"Goal of the workout\",\n"
#         "  \"muscle group\": \"Muscle group worked\",\n"
#         "  \"location\": \"Location of workout\",\n"
#         "  \"date\": \"28-10-2024\",\n"
#         "  \"exercises\": [\n"
#         "    {{\n"
#         "      \"name\": \"Exercise Name\",\n"
#         "      \"sets\": \"3\",\n"
#         "      \"reps\": \"10 per leg\",\n"
#         "      \"recommended_weight\": \"10 kg\",\n"
#         "      \"description\": \"Exercise description\"\n"
#         "    }}\n"
#         "  ],\n"
#         "  \"warm_up\": \"Warm-up details\",\n"
#         "  \"cool_down\": \"Cool-down details\",\n"
#         "  \"important_considerations\": \"Important considerations\",\n"
#         "  \"explanation\": \"Detailed explanation of the workout\"\n"
#         "}}]\n"
#     )
#     return payload_text

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
