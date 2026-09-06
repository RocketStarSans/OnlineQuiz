from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, QuizForm, EditProfileForm
from .models import Quiz, Question, Choice, Comment


# 1. Реєстрація
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'OnlineQuiz/register.html', {'form': form})


# 2. Вхід
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'OnlineQuiz/login.html', {'form': form})


# 3. Вихід
def logout_view(request):
    logout(request)
    return redirect('index')


def index_view(request):
    return render(request, 'OnlineQuiz/index.html')


# 4. Список квізів
def quiz_list(request):
    quizzes = Quiz.objects.all().order_by('-created_at')
    return render(request, 'OnlineQuiz/quiz_list.html', {'quizzes': quizzes})


# 5. Деталі квізу
def detail_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            Comment.objects.create(quiz=quiz, author=request.user, text=comment_text)
        return redirect('detail_quiz', quiz_id=quiz.id)

    comments = quiz.comments.select_related('author').all()
    return render(request, 'OnlineQuiz/detail_quiz.html', {'quiz': quiz, 'comments': comments})


# 6. Створення квізу
@login_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuizForm()

    return render(request, 'OnlineQuiz/create_quiz.html', {'form': form})


# 7. Мої квізи
@login_required
def my_quizzes(request):
    quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'OnlineQuiz/quiz_list.html', {'quizzes': quizzes})


# 8. Додавання питання до квізу
@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)

    if request.method == 'POST':
        num_choices = int(request.POST.get('num_choices', 4))
        question_text = request.POST.get('text', '').strip()
        correct_indexes = request.POST.getlist('correct')
        choice_texts = [request.POST.get(f'choice_{i}', '').strip() for i in range(num_choices)]

        if not question_text or not all(choice_texts) or not correct_indexes:
            return render(request, 'OnlineQuiz/add_question.html', {
                'quiz': quiz,
                'num_choices': num_choices,
                'choice_range': range(num_choices),
                'error': 'Заповни питання, всі варіанти відповіді та познач хоча б одну правильну.',
            })

        question = Question.objects.create(quiz=quiz, text=question_text)
        for i, choice_text in enumerate(choice_texts):
            Choice.objects.create(question=question, text=choice_text, is_correct=(str(i) in correct_indexes))

        return redirect('add_question', quiz_id=quiz.id)

    num_choices = int(request.GET.get('num', 4))
    return render(request, 'OnlineQuiz/add_question.html', {
        'quiz': quiz,
        'num_choices': num_choices,
        'choice_range': range(num_choices),
    })


# 9. Почати проходження — скидає прогрес і стартує з першого питання
@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    session_key = f'quiz_{quiz_id}_progress'
    request.session[session_key] = {'index': 0, 'score': 0}
    return redirect('take_quiz', quiz_id=quiz.id)


# 10. Проходження питання за питанням
@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.prefetch_related('choices').all())
    session_key = f'quiz_{quiz_id}_progress'
    progress = request.session.get(session_key, {'index': 0, 'score': 0})

    if progress['index'] >= len(questions):
        return redirect('quiz_result', quiz_id=quiz.id)

    current_question = questions[progress['index']]

    if request.method == 'POST':
        selected_ids = set(int(cid) for cid in request.POST.getlist('choice'))
        correct_ids = set(current_question.choices.filter(is_correct=True).values_list('id', flat=True))

        is_correct = selected_ids == correct_ids
        if is_correct:
            progress['score'] += 1

        progress['index'] += 1
        finished = progress['index'] >= len(questions)
        request.session[session_key] = progress

        return render(request, 'OnlineQuiz/take_quiz.html', {
            'quiz': quiz,
            'question': current_question,
            'question_number': progress['index'],
            'total': len(questions),
            'progress_percent': int(progress['index'] / len(questions) * 100),
            'answered': True,
            'is_correct': is_correct,
            'selected_choice_ids': selected_ids,
            'correct_choice_ids': correct_ids,
            'finished': finished,
        })

    return render(request, 'OnlineQuiz/take_quiz.html', {
        'quiz': quiz,
        'question': current_question,
        'question_number': progress['index'] + 1,
        'total': len(questions),
        'progress_percent': int((progress['index'] + 1) / len(questions) * 100),
        'answered': False,
    })


# 11. Підсумковий результат
@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    session_key = f'quiz_{quiz_id}_progress'
    progress = request.session.pop(session_key, {'index': 0, 'score': 0})
    total = quiz.questions.count()

    earned_xp = progress.get('score', 0)
    request.user.xp += earned_xp
    request.user.save(update_fields=['xp'])

    return render(request, 'OnlineQuiz/quiz_result.html', {
        'quiz': quiz,
        'score': progress.get('score', 0),
        'total': total,
        'earned_xp': earned_xp,
    })

# 12. Редагування квізу
@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('detail_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'OnlineQuiz/edit_quiz.html', {'form': form, 'quiz': quiz})


# 13. Видалення квізу
@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    if request.method == 'POST':
        quiz.delete()
    return redirect('quiz_list')


# 14. Профіль користувача
@login_required
def profile_view(request):
    user_quizzes = Quiz.objects.filter(created_by=request.user).order_by('-created_at')
    total_questions = Question.objects.filter(quiz__created_by=request.user).count()

    level = request.user.xp // 50 + 1
    xp_into_level = request.user.xp % 50
    xp_progress_percent = int(xp_into_level / 50 * 100)

    return render(request, 'OnlineQuiz/profile.html', {
        'quizzes': user_quizzes,
        'total_questions': total_questions,
        'level': level,
        'xp_into_level': xp_into_level,
        'xp_progress_percent': xp_progress_percent,
    })


# 15. Редагування профілю
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'OnlineQuiz/edit_profile.html', {'form': form})