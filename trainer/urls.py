# workouts/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('workout-plan/', views.workout_plan, name='workout_plan'),
    # path('signup/', views.signup, name='signup'),
    path('signup/', views.CustomUserWizard.as_view(), name='signup'),
    path('workout-plan/', views.workout_plan_result, name='workout_plan_result'),
    path('locations/new/', views.location_create, name='location_create'),  # Create view
    path('locations/<int:pk>/edit/', views.location_update, name='location_update'),  # Update view
    path('profile/update/', views.update_profile, name='update_profile'),
    path('location/<int:location_id>/', views.location_detail, name='location_detail'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    # path('upcoming-workouts/<str:group_id>/', views.upcoming_workouts_view, name='upcoming_workouts'),
    path('workouts/<int:group_id>/', views.upcoming_workouts_view, name='upcoming_workouts'),
    path('workouts/<int:workout_id>/', views.workout_detail_view, name='workout_detail'),
    # path('workouts/replace/<int:workout_id>/', views.replace_workout, name='replace_workout'),
    path('workouts/replace/<int:group_id>/<int:workout_id>/', views.replace_workout, name='replace_workout'),

    path('workouts/<int:workout_id>/exercise/replace/<int:exercise_id>/', views.replace_exercise, name='replace_exercise'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('workout/<int:pk>/update/', views.update_workout_session, name='update_workout_session'),
    path('update-personal-details/', views.update_personal_details, name='update_personal_details'),
    path('create-workout-form/', views.create_workout_form_view, name='create_workout_form'),
    path('personal_details/', views.personal_details, name='personal_details'),
    path('edit_field/<str:field_name>/', views.edit_field, name='edit_field'),
    path('update_field/<str:field_name>/', views.update_field, name='update_field'),
]
