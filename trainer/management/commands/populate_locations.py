from trainer.models import Location, Equipment  # Replace 'your_app_name' with your actual app name
from django.db import IntegrityError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Populate locations and equipment in the database'

    def handle(self, *args, **options):
        # Define comprehensive equipment choices
        EQUIPMENT_CHOICES = [
            # Public Park Equipment
            ('Pull-Up Bar', 'Public Park Equipment'),
            ('Dip Station', 'Public Park Equipment'),
            ('Monkey Bars', 'Public Park Equipment'),
            ('Benches', 'Public Park Equipment'),
            ('Resistance Bands', 'Public Park Equipment'),
            ('Climbing Wall', 'Public Park Equipment'),
            ('Parallel Bars', 'Public Park Equipment'),
            ('Push-Up Bars', 'Public Park Equipment'),
            ('Sit-Up Bench', 'Public Park Equipment'),
            ('Balance Beam', 'Public Park Equipment'),
            ('Bodyweight Workout Station', 'Public Park Equipment'),
            ('Battle Rope Anchors', 'Public Park Equipment'),
            ('Outdoor Elliptical Machines', 'Public Park Equipment'),
            ('Steppers', 'Public Park Equipment'),
            ('Leg Press Stations', 'Public Park Equipment'),
            ('Body Twist Machines', 'Public Park Equipment'),

            # Gym Equipment - Cardio Machines
            ('Treadmill', 'Gym Cardio Machines'),
            ('Elliptical', 'Gym Cardio Machines'),
            ('Stationary Bike', 'Gym Cardio Machines'),
            ('Rowing Machine', 'Gym Cardio Machines'),
            ('Assault Bike', 'Gym Cardio Machines'),
            ('Stair Climber', 'Gym Cardio Machines'),
            ('Fan Bike', 'Gym Cardio Machines'),
            ('Spin Bike', 'Gym Cardio Machines'),
            ('Air Runner', 'Gym Cardio Machines'),
            ('SkiErg', 'Gym Cardio Machines'),
            ('Recumbent Bike', 'Gym Cardio Machines'),
            ('Arc Trainer', 'Gym Cardio Machines'),
            ('Climbing Machine', 'Gym Cardio Machines'),
            ('Jacobs Ladder', 'Gym Cardio Machines'),
            ('Vertical Climber', 'Gym Cardio Machines'),
            ('Upper Body Ergometer (UBE)', 'Gym Cardio Machines'),

            # Gym Equipment - Strength Machines
            ('Smith Machine', 'Gym Strength Machines'),
            ('Leg Press Machine', 'Gym Strength Machines'),
            ('Lat Pulldown Machine', 'Gym Strength Machines'),
            ('Chest Press Machine', 'Gym Strength Machines'),
            ('Leg Extension Machine', 'Gym Strength Machines'),
            ('Cable Machine', 'Gym Strength Machines'),
            ('Hack Squat Machine', 'Gym Strength Machines'),
            ('Shoulder Press Machine', 'Gym Strength Machines'),
            ('Seated Row Machine', 'Gym Strength Machines'),
            ('Pec Deck Machine', 'Gym Strength Machines'),
            ('Ab Crunch Machine', 'Gym Strength Machines'),
            ('Leg Curl Machine', 'Gym Strength Machines'),
            ('Glute Bridge Machine', 'Gym Strength Machines'),
            ('Calf Raise Machine', 'Gym Strength Machines'),
            ('Inner/Outer Thigh Machine', 'Gym Strength Machines'),
            ('Biceps Curl Machine', 'Gym Strength Machines'),
            ('Triceps Extension Machine', 'Gym Strength Machines'),
            ('Multi-Station Gym Machine', 'Gym Strength Machines'),
            ('Chest Fly Machine', 'Gym Strength Machines'),

            # Gym Equipment - Free Weights
            ('Dumbbells', 'Gym Free Weights'),
            ('Barbells', 'Gym Free Weights'),
            ('Kettlebells', 'Gym Free Weights'),
            ('Medicine Balls', 'Gym Free Weights'),
            ('EZ Curl Bar', 'Gym Free Weights'),
            ('Trap Bar', 'Gym Free Weights'),
            ('Weight Plates', 'Gym Free Weights'),
            ('Powerlifting Chains', 'Gym Free Weights'),
            ('Weighted Vest', 'Gym Free Weights'),
            ('Adjustable Dumbbells', 'Gym Free Weights'),
            ('Ankle Weights', 'Gym Free Weights'),
            ('Weighted Sandbags', 'Gym Free Weights'),
            ('Power Bags', 'Gym Free Weights'),
            ('Club Bells', 'Gym Free Weights'),
            ('Mace Bells', 'Gym Free Weights'),

            # Gym Equipment - Benches and Racks
            ('Flat Bench', 'Gym Benches and Racks'),
            ('Adjustable Bench', 'Gym Benches and Racks'),
            ('Squat Rack', 'Gym Benches and Racks'),
            ('Power Rack', 'Gym Benches and Racks'),
            ('Half Rack', 'Gym Benches and Racks'),
            ('Preacher Curl Bench', 'Gym Benches and Racks'),
            ('Decline Bench', 'Gym Benches and Racks'),
            ('Incline Bench', 'Gym Benches and Racks'),
            ('Roman Chair', 'Gym Benches and Racks'),
            ('Hip Thrust Machine', 'Gym Benches and Racks'),

            # CrossFit Equipment
            ('Plyo Boxes', 'CrossFit Equipment'),
            ('Wall Balls', 'CrossFit Equipment'),
            ('Olympic Barbells', 'CrossFit Equipment'),
            ('Battle Ropes', 'CrossFit Equipment'),
            ('Sled Push', 'CrossFit Equipment'),
            ('Sandbags', 'CrossFit Equipment'),
            ('Wooden Rings', 'CrossFit Equipment'),
            ('GHD (Glute Ham Developer)', 'CrossFit Equipment'),
            ('Heavy Ropes', 'CrossFit Equipment'),
            ('Climbing Ropes', 'CrossFit Equipment'),
            ('Tire Flip Station', 'CrossFit Equipment'),
            ('Kegs for Lifting', 'CrossFit Equipment'),
            ('Steel Logs', 'CrossFit Equipment'),

            # F45 Training Equipment
            ('Slam Balls', 'F45 Training Equipment'),
            ('Agility Ladder', 'F45 Training Equipment'),
            ('TRX', 'F45 Training Equipment'),
            ('Boxing Bags', 'F45 Training Equipment'),
            ('Battle Ropes', 'F45 Training Equipment'),
            ('Core Sliders', 'F45 Training Equipment'),
            ('Bulgarian Bags', 'F45 Training Equipment'),
            ('Resistance Tubes', 'F45 Training Equipment'),
            ('Balance Boards', 'F45 Training Equipment'),

            # Yoga & Mobility Equipment
            ('Yoga Mat', 'Yoga & Mobility Equipment'),
            ('Foam Roller', 'Yoga & Mobility Equipment'),
            ('Stretch Bands', 'Yoga & Mobility Equipment'),
            ('Massage Balls', 'Yoga & Mobility Equipment'),
            ('Yoga Blocks', 'Yoga & Mobility Equipment'),
            ('Resistance Bands', 'Yoga & Mobility Equipment'),
            ('Yoga Bolsters', 'Yoga & Mobility Equipment'),
            ('Stretch Straps', 'Yoga & Mobility Equipment'),
            ('Yoga Wheel', 'Yoga & Mobility Equipment'),
            ('Cushions or Zafus for Meditation', 'Yoga & Mobility Equipment'),
            ('Eye Pillows', 'Yoga & Mobility Equipment'),

            # Functional Training Equipment
            ('Agility Cones', 'Functional Training Equipment'),
            ('Speed Ladder', 'Functional Training Equipment'),
            ('Parallette Bars', 'Functional Training Equipment'),
            ('Weighted Sled', 'Functional Training Equipment'),
            ('Jump Rope', 'Functional Training Equipment'),
            ('Resistance Parachute', 'Functional Training Equipment'),
            ('Balance Trainer (BOSU Ball)', 'Functional Training Equipment'),
            ('Core Bags', 'Functional Training Equipment'),
            ('Balance Disc', 'Functional Training Equipment'),
            ('Landmine Attachment for Barbells', 'Functional Training Equipment'),
            ('Sand Discs', 'Functional Training Equipment'),
            ('Weighted Bags', 'Functional Training Equipment'),

            # Miscellaneous
            ('Boxing Gloves', 'Miscellaneous'),
            ('Heart Rate Monitor', 'Miscellaneous'),
            ('Weighted Jump Rope', 'Miscellaneous'),
            ('Gymnastic Rings', 'Miscellaneous'),
            ('Aerobic Stepper', 'Miscellaneous'),
            ('Chalk or Chalk Balls', 'Miscellaneous'),
            ('Exercise Ball (Stability Ball)', 'Miscellaneous'),
        ]

        # Equipment categories relevant to each location type
        LOCATION_EQUIPMENT_MAP = {
            'Standard Gym': ['Gym Cardio Machines', 'Gym Strength Machines', 'Gym Free Weights', 'Gym Benches and Racks'],
            'Standard Park/Playground': ['Public Park Equipment'],
            'Standard Crossfit Gym': ['CrossFit Equipment', 'Gym Free Weights']
        }

        # List of locations to create
        locations = [
            ('Standard Gym', 'Gym'),
            ('Standard Park/Playground', 'Park'),
            ('Standard Crossfit Gym', 'Crossfit'),
        ]

        # Create locations and populate them with equipment
        for location_name, location_type in locations:
            try:
                # Create location
                location, created = Location.objects.get_or_create(
                    name=location_name,
                    location_type=location_type
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Successfully created location: {location_name}"))

                # Filter and add equipment based on location type
                allowed_equipment_types = LOCATION_EQUIPMENT_MAP[location_name]
                for equipment_name, equipment_group in EQUIPMENT_CHOICES:
                    if equipment_group in allowed_equipment_types:
                        try:
                            equipment, _ = Equipment.objects.get_or_create(
                                equipment=equipment_name,
                                equipment_type=equipment_group
                            )
                            location.equipment.add(equipment)  # Associate equipment with the location
                            self.stdout.write(f"  Added equipment: {equipment_name} under {equipment_group}")
                        except IntegrityError:
                            self.stdout.write(self.style.WARNING(f"  Warning: {equipment_name} may already exist."))

            except IntegrityError:
                self.stdout.write(self.style.ERROR(f"Error: {location_name} may already exist."))
