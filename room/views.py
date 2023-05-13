from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django .contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForms,TakeQuizForm , QuestionForm , MarksForm , AnswerForm , BaseAnswerInlineFormSet , QuestionTypeForm , BooleanAnswerForm , NumericalAnswerForm
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth import login, authenticate , logout
from django.views.generic import CreateView, ListView, UpdateView , DeleteView , DetailView
from .models import quizzes,Questions,Answer,Marks,User,TakenQuiz,Quiztaker
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.db.models import Avg,Count
from django.forms import inlineformset_factory
import xlwt
from django.template import RequestContext
from QuizMe.decorators import quizmaster_required , quiztaker_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request , 'room/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForms(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account is Created for {username}')
            return redirect('home')
    else:
        form = UserRegisterForms()
        messages.error(request, "Unsuccessful registration. Invalid information.")
    return render(request , 'room/register.html',context={'form' : form})


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request , data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username , password = password)
            if user is not None :
                login(request,user)
                if user.role_choice == 'QuizTaker' : 
                    messages.info(request,f"You are now logged in as {username}.")
                    return redirect('quiz_list')
                else :
                    messages.info(request,f"You are now logged in as {username}.")
                    return redirect('quiz_change_list')
            else :
                messages.error(request,"Invalid username or password.")
        else :
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="room/login.html", context={"login_form":form})


	

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("home")

@method_decorator([login_required, quiztaker_required], name='dispatch')
class QuizListView(ListView):
    model = quizzes
    ordering = ('quiz_name', )
    context_object_name = 'quizzes'
    template_name = 'room/quiz_list.html'

@login_required
@quiztaker_required
def take_quiz(request, pk):

    qt = request.user.quiztaker
    quiz = quizzes.objects.get(pk=pk)
#    answer = a.get_answer(question)
#    unanswered_questions = qt.get_unanswered_question(quiz)
#    print(unanswered_questions)
#    total_unanswered_questions = unanswered_questions.count()
#    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
#    question = unanswered_questions.first()

    qt.quizzes.add(quiz)
    unanswered_questions = qt.get_unanswered_questions(quiz=quiz)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question,data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                QT_Answer = form.save(commit=False)
                QT_Answer.qt = qt
                QT_Answer.save()
                if qt.get_unanswered_questions(quiz).exists():
                    return redirect('/')
                else:
                    positive_marks = int(Marks.objects.filter('positive_marking'))
                    negative_marks = int(Marks.objects.filter('negative_marking'))
                    correct_answers = qt.quizzes_Answer.filter(Answer__Questions__quizzes=quiz, Answer__is_correct=True).count()
                    wrong_answers = qt.quizzes_Answer.filter(Answer__Questions__quizzes=quiz, Answer__is_correct=False).count()
                    score = (correct_answers * positive_marks) - (wrong_answers * negative_marks)
                    messages.warning(request, 'Your score for the quiz %s was %s.' % (quiz.quiz_name, score))
                    return redirect('home')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'room/take_quiz.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
    })

@method_decorator([login_required, quizmaster_required], name='dispatch')
class QuizCreateView(CreateView):
    model = quizzes
    fields = ('quiz_name', )
    template_name = 'room/quiz_add_form.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(self.request, 'The quiz was created with success! Go ahead and add some questions now.')
        return redirect('home')


@method_decorator([login_required, quizmaster_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = quizzes
    fields = ('quiz_name', )
    context_object_name = 'quiz'
    template_name = 'room/quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answer'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('room:quiz_change', kwargs={'pk': self.object.pk})


@method_decorator([login_required, quizmaster_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = quizzes
    context_object_name = 'quiz'
    template_name = 'room/quiz_delete.html'
    success_url = reverse_lazy('quiz_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.quiz_name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()
  
def question_type(request, pk):
    quiz = get_object_or_404(quizzes, pk=pk, owner=request.user)
    if request.method =='POST':        
        type_form = QuestionTypeForm(request.POST)
        if type_form.is_valid():
            ques_type = type_form.save(commit=False)
            ques_type.save()
    else:
        type_form = QuestionTypeForm(request.POST)
    
    return render(request , 'room/question_type_form.html' , {'type_form' : type_form  , 'quiz' : quiz}) 
        
    
@login_required
@quizmaster_required
def question_add(request, pk):

    quiz = get_object_or_404(quizzes, pk=pk, owner=request.user)
    question_type = Questions.question_type
    question_type = 'mcq'

    if request.method == 'POST':
        ques_form = QuestionForm(request.POST)
        marks_form = MarksForm(request.POST)
        ans_form = AnswerForm(request.POST)
        num_form = NumericalAnswerForm(request.POST)
        bool_form = BooleanAnswerForm(request.POST)
        if ques_form.is_valid() and ans_form.is_valid() and marks_form.is_valid() and bool_form.is_valid() and num_form.is_valid(): 
            question = ques_form.save(commit=False)
            marks = marks_form.save(commit=False)
            num = num_form.save(commit=False)
#            bool_type = bool_form(commit=False)
            ans = ans_form.save(commit=False)
            question.quiz = quiz
            question.save()
#            num.save()
#            bool_type.save()
#            marks.save()
#            ans.save() 
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('quiz_change_list')
    else:
        ques_form = QuestionForm(request.POST)
        marks_form = MarksForm(request.POST)
        ans_form = AnswerForm(request.POST)
        num_form = NumericalAnswerForm(request.POST)
        bool_form = BooleanAnswerForm(request.POST)

    return render(request, 'room/question_add_form.html', {'quiz': quiz, 'ques_form': ques_form , 'ans_form' : ans_form ,'marks_form' : marks_form  , 'num_form' : num_form , 'bool_form' : bool_form , 'ques_type' : question_type})

@method_decorator([login_required, quiztaker_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'room/taken_quiz.html'



    def get_queryset(self):
        queryset = self.request.user.taken_quizzes \
                .select_related('quiz') \
                .order_by('quiz__quiz_name')
        return queryset
    

@method_decorator([login_required, quizmaster_required], name='dispatch')
class QuizResultsView(DetailView):
    model = quizzes
    context_object_name = 'quiz'
    template_name = 'room/quiz_result.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related('quiztaker').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score
        }
        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()
    
@login_required
@quizmaster_required
def question_change(request, quiz_pk, question_pk):
    # Simlar to the `question_add` view, this view is also managing
    # the permissions at object-level. By querying both `quiz` and
    # `question` we are making sure only the owner of the quiz can
    # change its details and also only questions that belongs to this
    # specific quiz can be changed via this url (in cases where the
    # user might have forged/player with the url params.
    quiz = get_object_or_404(quizzes, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Questions, pk=question_pk, quiz=quiz)

    AnswerFormSet = inlineformset_factory(
        Questions,  # parent model
        Answer,  # base model
        formset=BaseAnswerInlineFormSet,
        fields=('Answer_content', 'is_correct'),
        min_num=2,
        validate_min=True,
        max_num=10,
        validate_max=True
    )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Question and answers saved with success!')
            return redirect('quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'room/question_change_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'formset': formset
    })

@method_decorator([login_required, quizmaster_required], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Questions
    context_object_name = 'question'
    template_name = 'room/question_delete_form.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The question %s was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Questions.objects.filter(quiz__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('quiz_change', kwargs={'pk': question.quiz_id})
    

@login_required
@quizmaster_required
def export_users_xls(request , pk):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="results.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Quiz Result') # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Username', 'Score', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = TakenQuiz.objects.all().values_list('quiztaker', 'score')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)

    return response


def highscores(request, pk , page=1):
    """
    displays the leaderboard table
    """
    # You can set the default page size 
    #Leaderboard.DEFAULT_PAGE_SIZE = 2
    game = get_object_or_404(quizzes , pk=pk , owner=request.user)
    scores = TakenQuiz.objects.all().values_list('quiztaker', 'score')
    score_list = {}
    user_ids = []

    for score in scores:
        user_ids.append(score["username"])
        score_list[int(score["member"])] = score

    users = User.objects.filter(pk__in=user_ids)

    return render(request , 'room/leaderboard.html' , {'user_ids' : user_ids , 'score_list' : score_list})


@method_decorator([login_required, quizmaster_required], name='dispatch')
class QuizMasterListView(ListView):
    model = quizzes
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'room/quiz_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_quizzes', distinct=True))
        return queryset

""" def highscores(request, pk , page=1):

    # You can set the default page size 
    #Leaderboard.DEFAULT_PAGE_SIZE = 2
    game = get_object_or_404(quizzes , pk=pk , owner=request.user)
    page = int(page)
    leaderboard = leaderboard(game)
    scores = leaderboard.leaders(int(page))
    if not scores:
        scores = []
    total_pages = int(leaderboard.total_pages())

    # Pagination values
    has_next = True if (page < total_pages) else False
    has_prev = True if (page != 1) else False
    next_page = page + 1 if has_next else page
    prev_page = page - 1 if has_prev else page

    # hashmap to get the score instance quickly
    score_list = {}

    # Collect the user ids
    user_ids = []
    for score in scores:
        user_ids.append(score["member"])
        score_list[int(score["member"])] = score

    # Fetch users in question
    users = User.objects.filter(pk__in=user_ids)

    for user in users:
        score_list[user.pk]["user"] = user

    return render("room/leaderboard.html", 
            {
                "scores": scores, 
                "total_pages":total_pages, 
                "game":game, 
                "page":page, 
                'has_next': has_next, 
                'has_prev': has_prev, 
                'next_page': next_page,
                'prev_page': prev_page,
            }, 
             context_instance=RequestContext(request))

 """
