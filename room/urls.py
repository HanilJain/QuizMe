from django.contrib import admin
from django.urls import path
from . import views
from room.views import QuizCreateView , QuizDeleteView

urlpatterns = [
    path('' , views.home, name='home'),
    path('quiz/' , views.QuizListView.as_view() , name='quiz_list'),
    path('quiz/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('createquiz/', QuizCreateView.as_view() , name='add_quiz'),
    path('taken/', views.TakenQuizListView.as_view(), name='taken_quiz_list'),
    path('deletequiz/<int:pk>/', QuizDeleteView.as_view() , name='deleteQuiz'),
    path('add_question/<int:pk>/', views.question_add , name='add_question'),
    path('quiz/<int:pk>/results/', views.QuizResultsView.as_view(), name='quiz_results'),
    path('quiz/update/<int:pk>/', views.QuizUpdateView.as_view(), name='quiz_change'),
    path('quiz/<int:quiz_pk>/question/<int:question_pk>/', views.question_change, name='question_change'),
    path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    path('questionType/<int:pk>/' , views.question_type , name='ques_type'),
    path('quiz/<int:pk>/results/excel/',views.export_users_xls , name='excel'),
    path('quiz/<int:pk>/leaderboard/', views.highscores , name='highscore'),
    path('quizmaster/quiz/', views.QuizMasterListView.as_view(), name='quiz_change_list'),
]

