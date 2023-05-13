from django.db import models
from django.contrib.auth.models import AbstractUser

role_choice = (
    ("QuizTaker","QuizTaker"),
    ("QuizMaster", "QuizMaster"), 
)

question_type = (
    ("numerical" ,"numerical"),
    ("Boolean","Boolean"),
    ("mcq", "mcq"),
)

class User(AbstractUser):
    username = models.TextField(max_length=15, unique=True)
    role_choice = models.CharField(max_length=20,choices=role_choice,default='QuizTaker')

    def __str__(self) -> str:
        return self.username
    
    def __str__(self) -> str:
        self.role_choice
        return super().__str__()


class quizzes(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes' )    
    quiz_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.quiz_name

class Questions(models.Model):
    quiz = models.ForeignKey(quizzes , on_delete=models.CASCADE , related_name='questions')
    question_content = models.CharField(max_length=100)
    question_type = models.CharField(max_length=10 , choices=question_type ,default='mcq')

    def __str__(self) -> str:
        return self.question_content
    
    
class Answer(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE , related_name="answer")
    Answer_content = models.CharField(max_length=50)
    is_correct = models.BooleanField(default=False)
    numerical_option = models.IntegerField(blank=True,null=True)
    boolean_question = models.BooleanField(blank=True , null =True , default=False)

    def __str__(self) -> str:
        return self.Answer_content
    

class Marks(models.Model):
    question_marking = models.OneToOneField(Questions , on_delete=models.CASCADE ,  related_name="marking")
    positive_marking = models.IntegerField(null= True , blank=True ,default=4)
    negative_marking = models.IntegerField(null=True, blank=True , default=1)



""" class Quiztaker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    Quizzes = models.ManyToManyField(quizzes ) #through='TakenQuiz'

    

    def __str__(self):
        return self.user.username """


class TakenQuiz(models.Model):
    quiztaker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(quizzes, on_delete=models.CASCADE, related_name='taken_quizzes')
    score = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)



class Quiztaker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,related_name='quiztaker')
    quizzes = models.ManyToManyField(quizzes)

    def get_unanswered_questions(self,quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('question_content')
        return questions

    def __str__(self):
        return self.user.username

class QTAnswer(models.Model):
    quiztaker = models.ForeignKey(Quiztaker, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+' , null=True)