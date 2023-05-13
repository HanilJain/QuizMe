from django.contrib import admin
from .models import User,quizzes,Questions,Answer,Marks,Quiztaker,TakenQuiz,QTAnswer

# Register your models here.
admin.site.register(User)
admin.site.register(quizzes)
admin.site.register(Questions)
admin.site.register(Answer)
admin.site.register(Marks)
admin.site.register(QTAnswer)
admin.site.register(Quiztaker)
admin.site.register(TakenQuiz)