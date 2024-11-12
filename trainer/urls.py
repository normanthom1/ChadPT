# workouts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    # path('locations/', views.location_list, name='location_list'),
    # path('locations/add/', views.location_create, name='location_create'),
    # path('locations/update/<int:pk>/', views.location_update, name='location_update'),
    path('workout-plan/', views.workout_plan, name='workout_plan'),
    path('signup/', views.signup, name='signup'),
    path('generate_workout/', views.send_user_data_to_gemini, name='generate_workout'),
    # path('generate_workout/', views.send_user_data_to_gemini, name='generate_workout'),
    path('workout_plan/', views.workout_plan_result, name='workout_plan_result'),
    path('locations/new/', views.location_create, name='location_create'),  # Create view
    path('locations/<int:pk>/edit/', views.location_update, name='location_update'),  # Update view
    path('profile/update/', views.update_profile, name='update_profile'),
    path('location/<int:location_id>/', views.location_detail, name='location_detail'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    # path('', views.home, name='home'),
]
