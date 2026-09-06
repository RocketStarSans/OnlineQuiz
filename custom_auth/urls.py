from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('quizzes/<int:quiz_id>/', views.detail_quiz, name='detail_quiz'),
    path('quizzes/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('my-quizzes/', views.my_quizzes, name='my_quizzes'),
    path('quizzes/<int:quiz_id>/take/', views.start_quiz, name='start_quiz'),
    path('quizzes/<int:quiz_id>/question/', views.take_quiz, name='take_quiz'),
    path('quizzes/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
    path('quizzes/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]