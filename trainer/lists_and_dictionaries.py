EQUIPMENT_GROUP_CHOICES = [
    ('Public Park Equipment', 'Public Park Equipment'),
    ('Gym Cardio Machines', 'Gym Cardio Machines'),
    ('Gym Strength Machines', 'Gym Strength Machines'),
    ('Gym Free Weights', 'Gym Free Weights'),
    ('Gym Benches and Racks', 'Gym Benches and Racks'),
    ('CrossFit Equipment', 'CrossFit Equipment'),
    ('F45 Training Equipment', 'F45 Training Equipment'),
    ('Yoga & Mobility Equipment', 'Yoga & Mobility Equipment'),
    ('Functional Training Equipment', 'Functional Training Equipment'),
    ('Miscellaneous', 'Miscellaneous')
]

QUOTES = [
    {"quote": "The only bad workout is the one that didn’t happen.", "author": None},
    {"quote": "Take care of your body. It’s the only place you have to live.", "author": "Jim Rohn"},
    {"quote": "Exercise is a celebration of what your body can do, not a punishment for what you ate.", "author": None},
    {"quote": "The pain you feel today will be the strength you feel tomorrow.", "author": None},
    {"quote": "Push yourself, because no one else is going to do it for you.", "author": None},
    {"quote": "Sweat is fat crying.", "author": None},
    {"quote": "Success usually comes to those who are too busy to be looking for it.", "author": "Henry David Thoreau"},
    {"quote": "Fitness is not about being better than someone else. It’s about being better than you used to be.", "author": None},
    {"quote": "Motivation is what gets you started. Habit is what keeps you going.", "author": "Jim Ryun"},
    {"quote": "The body achieves what the mind believes.", "author": None},
    {"quote": "What hurts today makes you stronger tomorrow.", "author": "Jay Cutler"},
    {"quote": "Your body can stand almost anything. It’s your mind that you have to convince.", "author": None},
    {"quote": "Train insane or remain the same.", "author": None},
    {"quote": "The only way to define your limits is by going beyond them.", "author": "Arthur C. Clarke"},
    {"quote": "The only bad workout is the one you didn’t do.", "author": None},
    {"quote": "Strength does not come from physical capacity. It comes from an indomitable will.", "author": "Mahatma Gandhi"},
    {"quote": "Success is usually the culmination of controlling failure.", "author": "Sylvester Stallone"},
    {"quote": "You don’t have to be extreme, just consistent.", "author": None},
    {"quote": "Don’t limit your challenges, challenge your limits.", "author": None},
    {"quote": "Nothing will work unless you do.", "author": "Maya Angelou"}
    # Add more quotes as desired
]

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



EATING_HABITS_CHOICES = [
    ('poor', 'Poor – Frequent junk food and limited fruits/vegetables.'),
    ('fair', 'Fair – Balanced meals but occasional unhealthy snacks.'),
    ('average', 'Average – Mix of healthy and unhealthy meals.'),
    ('good', 'Good – Mostly balanced meals with occasional indulgences.'),
    ('excellent', 'Excellent – Consistently balanced, nutrient-rich diet.'),
]

WORKOUT_TIME_CHOICES = [(str(i), f"{i} minutes") for i in range(10, 151, 5)]

FITNESS_LEVEL_CHOICES = [
    ('beginner', 'Beginner - Just starting out or returning after a long break, with limited experience.'),
    ('intermediate', 'Intermediate - Some experience with regular exercise and a moderate level of fitness.'),
    ('advanced', 'Advanced - Extensive experience, high level of fitness, and familiarity with intense workouts.'),
    ('elite', 'Elite - Exceptional fitness and performance at a professional or near-professional level.'),
]

WORKOUT_TYPE_PREFERENCE_CHOICES = [
    ('functional', 'Improve everyday movement (Functional training)'),
    ('targeted', 'Build specific muscles (Targeted training)'),
    ('both', 'Combination of both (Functional and targeted training)'),
]

# Choices for preferred workout intensity
WORKOUT_INTENSITY_CHOICES = [
    ('low', 'Low - Relaxed activities focusing on recovery, flexibility, or light effort.'),
    ('moderate', 'Moderate - A balanced intensity that improves endurance and strength without overexertion.'),
    ('high', 'High - Challenging intensity, pushing limits to achieve greater fitness and performance gains.'),
    ('extreme', 'Extreme - Very intense workouts for peak performance and competitive goals.'),
]

GENDER_CHOICES=[
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
    ('prefer_not_to_say', 'Prefer not to say'),
]

PLAN_DURATION_CHOICES = [
    ('day', 'One Day'),
    ('week', 'One Week'),
]


GOAL_CHOICES = [
    ('heart_health', 'Cardiovascular Health and Endurance - Improve your ability to exercise for longer periods without tiring.'),
    ('energy', 'General Energy and Stamina - Increase your daily energy levels and feel less fatigue.'),
    ('muscle_strength', 'Muscle Strength - Become stronger and lift or carry things more easily.'),
    ('flexibility', 'Flexibility - Improve your ability to stretch and move your body.'),
    ('explosive_power', 'Explosive Power - Perform quick and powerful movements like jumps or sprints.'),
    ('speed', 'Speed - Run or move faster over short distances.'),
    ('coordination', 'Coordination - Improve how your body moves smoothly and in sync.'),
    ('agility', 'Agility - Move quickly and easily, especially when changing direction.'),
    ('balance', 'Balance - Stay steady and stable during exercises or daily activities.'),
    ('precision_control', 'Precision and Control - Perform exercises or movements with accuracy and focus.'),
]


DAYS_OF_WEEK_CHOICES = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
]
