from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # --- Authentication ---
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- Main Pages ---
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-skill/', views.add_skill, name='add_skill'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # --- Actions (No pages, just processing) ---
    path('request/<int:user_id>/', views.send_request, name='send_request'),
    path('handle/<int:request_id>/<str:action>/', views.handle_request, name='handle_request'),
    path('delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('delete-conversation/<int:user_id>/', views.delete_conversation, name='delete_conversation'),

    # --- Chat & API ---
    path('chat/<int:user_id>/', views.chat, name='chat'),
    path('api/messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('autocomplete/', views.skill_autocomplete, name='skill_autocomplete'),

    path('check_updates/', views.check_updates, name='check_updates'),
    path('profile/delete/', views.delete_account, name='delete_account'),
]