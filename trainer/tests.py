from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from .models import CustomUser, Equipment, Location, UserPreference, WeightHistory, WorkoutSession, WarmUp, CoolDown, Exercise

User = get_user_model()

class ModelsTestCase(TestCase):
    def setUp(self):
        # Set up test data for CustomUser, Equipment, Location, and other models
        self.user = User.objects.create_user(email='testuser@example.com', first_name='Test', last_name='User', password='password')
        self.equipment = Equipment.objects.create(equipment='Dumbbells', equipment_type='Strength')
        self.location = Location.objects.create(name="Gym A", location_type="Gym", address="123 Fitness St.")
        self.user_pref = UserPreference.objects.create(
            user=self.user,
            firstname="Test",
            lastname="User",
            dob=date(1990, 1, 1),
            preferred_location=self.location,
            preferred_workout_time="30"
        )

    def test_create_equipment(self):
        # Verify equipment creation
        self.assertEqual(self.equipment.equipment, 'Dumbbells')
        self.assertEqual(self.equipment.equipment_type, 'Strength')

    def test_update_equipment(self):
        # Update and verify equipment
        self.equipment.equipment_type = 'Cardio'
        self.equipment.save()
        updated_equipment = Equipment.objects.get(id=self.equipment.id)
        self.assertEqual(updated_equipment.equipment_type, 'Cardio')

    def test_delete_equipment(self):
        # Delete and verify equipment
        equipment_id = self.equipment.id
        self.equipment.delete()
        self.assertFalse(Equipment.objects.filter(id=equipment_id).exists())

    def test_create_location(self):
        # Verify location creation
        self.assertEqual(self.location.name, "Gym A")
        self.assertEqual(self.location.location_type, "Gym")

    def test_update_location(self):
        # Update and verify location
        self.location.name = "New Gym"
        self.location.save()
        updated_location = Location.objects.get(id=self.location.id)
        self.assertEqual(updated_location.name, "New Gym")

    def test_delete_location(self):
        # Delete and verify location
        location_id = self.location.id
        self.location.delete()
        self.assertFalse(Location.objects.filter(id=location_id).exists())

    def test_user_preference_creation(self):
        # Verify user preference creation and relationship with user and location
        self.assertEqual(self.user_pref.user, self.user)
        self.assertEqual(self.user_pref.firstname, "Test")
        self.assertEqual(self.user_pref.preferred_location, self.location)

    def test_update_user_preference(self):
        # Update and verify user preference
        self.user_pref.fitness_level = UserPreference.ADVANCED
        self.user_pref.save()
        updated_user_pref = UserPreference.objects.get(id=self.user_pref.id)
        self.assertEqual(updated_user_pref.fitness_level, UserPreference.ADVANCED)

    def test_delete_user_preference(self):
        # Delete and verify user preference
        user_pref_id = self.user_pref.id
        self.user_pref.delete()
        self.assertFalse(UserPreference.objects.filter(id=user_pref_id).exists())

    def test_weight_history(self):
        # Create, update, and delete WeightHistory for user preference
        weight_history = WeightHistory.objects.create(user=self.user_pref, date=date.today(), weight=70.0, bmi=22.0)
        self.assertEqual(weight_history.weight, 70.0)
        
        # Update WeightHistory
        weight_history.weight = 68.0
        weight_history.save()
        updated_weight_history = WeightHistory.objects.get(id=weight_history.id)
        self.assertEqual(updated_weight_history.weight, 68.0)
        
        # Delete WeightHistory
        weight_history_id = weight_history.id
        weight_history.delete()
        self.assertFalse(WeightHistory.objects.filter(id=weight_history_id).exists())

    def test_workout_session(self):
        # Create, update, and delete WorkoutSession
        workout = WorkoutSession.objects.create(
            group_id="001",
            user=self.user_pref,
            name="Morning Routine",
            goal="Increase Strength",
            date=date.today(),
            location=self.location,
            description="Circuit training focusing on core and lower body",
            time_taken=timedelta(minutes=45),
            difficulty_rating=4,
            enjoyment_rating=5
        )
        self.assertEqual(workout.name, "Morning Routine")

        # Update WorkoutSession
        workout.goal = "Improve Endurance"
        workout.save()
        updated_workout = WorkoutSession.objects.get(id=workout.id)
        self.assertEqual(updated_workout.goal, "Improve Endurance")

        # Delete WorkoutSession
        workout_id = workout.id
        workout.delete()
        self.assertFalse(WorkoutSession.objects.filter(id=workout_id).exists())

    def test_exercise(self):
        # Create, update, and delete Exercise for WorkoutSession
        workout = WorkoutSession.objects.create(group_id="002", user=self.user_pref, name="Evening Cardio", date=date.today(), location=self.location)
        exercise = Exercise.objects.create(workout=workout, name="Jumping Jacks", recommended_weight="Bodyweight", actual_weight="Bodyweight", reps="3x15")
        
        self.assertEqual(exercise.name, "Jumping Jacks")
        
        # Update Exercise
        exercise.reps = "4x20"
        exercise.save()
        updated_exercise = Exercise.objects.get(id=exercise.id)
        self.assertEqual(updated_exercise.reps, "4x20")
        
        # Delete Exercise
        exercise_id = exercise.id
        exercise.delete()
        self.assertFalse(Exercise.objects.filter(id=exercise_id).exists())
        
    def test_warm_up_and_cool_down(self):
        # Test creating WarmUp and CoolDown for a WorkoutSession
        workout = WorkoutSession.objects.create(group_id="003", user=self.user_pref, name="Warm-Up Session", date=date.today(), location=self.location)
        warm_up = WarmUp.objects.create(workout=workout, description="5 minutes of light cardio")
        cool_down = CoolDown.objects.create(workout=workout, description="5 minutes of stretching")

        # Verify WarmUp and CoolDown creation
        self.assertEqual(warm_up.description, "5 minutes of light cardio")
        self.assertEqual(cool_down.description, "5 minutes of stretching")

        # Update WarmUp and CoolDown
        warm_up.description = "10 minutes of light cardio"
        cool_down.description = "10 minutes of stretching"
        warm_up.save()
        cool_down.save()

        updated_warm_up = WarmUp.objects.get(id=warm_up.id)
        updated_cool_down = CoolDown.objects.get(id=cool_down.id)
        self.assertEqual(updated_warm_up.description, "10 minutes of light cardio")
        self.assertEqual(updated_cool_down.description, "10 minutes of stretching")

        # Delete WarmUp and CoolDown
        warm_up_id = warm_up.id
        cool_down_id = cool_down.id
        warm_up.delete()
        cool_down.delete()
        self.assertFalse(WarmUp.objects.filter(id=warm_up_id).exists())
        self.assertFalse(CoolDown.objects.filter(id=cool_down_id).exists())
