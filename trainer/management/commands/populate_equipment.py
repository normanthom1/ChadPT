import django
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from trainer.models import Equipment  # Replace with your actual app name

# Equipment choices with group assignment
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

    # Gym Cardio Machines
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

    # Gym Strength Machines
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

    # Gym Free Weights
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

    # Gym Benches and Racks
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

class Command(BaseCommand):
    help = 'Populate the Equipment model with predefined equipment choices'

    def handle(self, *args, **kwargs):
        for equipment_name, equipment_type in EQUIPMENT_CHOICES:
            try:
                Equipment.objects.create(
                    equipment=equipment_name,
                    equipment_type=equipment_type
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully added: {equipment_name} under {equipment_type}'
                ))
            except IntegrityError:
                self.stdout.write(self.style.WARNING(
                    f'Error adding: {equipment_name} (may already exist)'
                ))
