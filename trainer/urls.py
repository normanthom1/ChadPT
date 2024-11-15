# workouts/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('workout-plan/', views.workout_plan, name='workout_plan'),
    path('signup/', views.signup, name='signup'),
    path('generate-workout/', views.send_user_data_to_gemini, name='generate_workout'),
    path('workout-plan/', views.workout_plan_result, name='workout_plan_result'),
    path('locations/new/', views.location_create, name='location_create'),  # Create view
    path('locations/<int:pk>/edit/', views.location_update, name='location_update'),  # Update view
    path('profile/update/', views.update_profile, name='update_profile'),
    path('location/<int:location_id>/', views.location_detail, name='location_detail'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    # path('upcoming-workouts/<str:group_id>/', views.upcoming_workouts_view, name='upcoming_workouts'),
    path('workouts/<int:group_id>/', views.upcoming_workouts_view, name='upcoming_workouts'),
    path('workouts/<int:workout_id>/', views.workout_detail_view, name='workout_detail'),
    path('workouts/replace/<int:workout_id>/', views.replace_workout, name='replace_workout'),
    path('workouts/<int:workout_id>/exercise/replace/<int:exercise_id>/', views.replace_exercise, name='replace_exercise'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('workout/<int:pk>/update/', views.update_workout_session, name='update_workout_session'),
]
