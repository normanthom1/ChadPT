from django.contrib import admin
from .models import (
    CustomUser,
    Equipment,
    Location,
    UserPreference,
    WeightHistory,
    WorkoutSession,
    WarmUp,
    WarmUpExercise,
    CoolDown,
    CoolDownExercise,
    Exercise,
    CardioExercise,
)

# Register your models here
admin.site.register(CustomUser)
admin.site.register(Equipment)
admin.site.register(Location)
admin.site.register(UserPreference)
admin.site.register(WeightHistory)
admin.site.register(WorkoutSession)
admin.site.register(WarmUp)
admin.site.register(WarmUpExercise)
admin.site.register(CoolDown)
admin.site.register(CoolDownExercise)
admin.site.register(Exercise)
admin.site.register(CardioExercise)
