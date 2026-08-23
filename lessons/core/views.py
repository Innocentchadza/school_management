from http.client import responses
from django.shortcuts import redirect, render
from requests import request
from streamlit import button
from .models import Students, SchoolFees, Program
from .forms import StudentsForm, SchoolFeesForm, ProgramForm
from .models import *
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import StudentregistrationForm, StudentLoginForm

def student_register(request):
    form = StudentregistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['Username'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],

        )
            
        Students.objects.create(
            user=user,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
            date_of_birth=form.cleaned_data['date_of_birth'],
            program=form.cleaned_data['program']
        )
        login(request, user)
        messages.success(request, "Registration successful.")
        return redirect('exam_list')
    return render(request, 'student_register.html', {'form': form})

def student_login(request):
    form = StudentLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "Login successful.")
        return redirect('exam_list')
    return render(request, 'student_login.html', {'form': form})

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, "Admin login successful.")
            return redirect('admin_dashboard')  # Redirect to admin dashboard or desired page
        else:
            messages.error(request, "Invalid credentials or not an admin.")
    return render(request, 'admin_login.html')

def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('admin_login')  # Redirect to admin login or another page
    exams = Examination.objects.all()
    total_students = Students.objects.count()
    total_exams = Examination.objects.count()
    total_programs = Program.objects.count()
    total_fees = SchoolFees.objects.count()


    context = {
        "total_students": total_students,
        "total_exams": total_exams,
        "total_programs": total_programs,
        "total_fees": total_fees,
        "exams": exams,
    }
    return render(request, 'admin_dashboard/admin_dashboard.html', context)

def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('admin_login')

def student_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('student_login')

def index(request):
    students = Students.objects.all()
    total_students = Students.objects.count()
    context = {
        "total_students": total_students
    }
    return render(request, 'index.html', context)

def students(request):
    students = Students.objects.all()
    total_students = Students.objects.count()
    student_list = list(Students.objects.all())
    context = {
        "students": students,
        "total_students": total_students,
        "student_list": student_list
    }
    return render(request, 'students.html', context)

def fees(request):
    fees = SchoolFees.objects.all()
    context = {
        "fees": fees
    }
    return render(request, 'fees.html', context)


def program(request):
    programs = Program.objects.all()
    context = {
        "programs": programs
    }
    return render(request, 'program.html', context)


def add_student(request):
    if request.method == "POST":
        form = StudentsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students')
    else:
        form = StudentsForm()
    return render(request, 'add_students.html', {'form': form})


def add_fees(request):
    if request.method == "POST":
        form = SchoolFeesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fees')
    else:
        form = SchoolFeesForm()
    return render(request, 'add_fees.html', {'form': form})


def add_program(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programs')
    else:
        form = ProgramForm()
    return render(request, 'add_program.html', {'form': form})

def exam_list(request):
    exams = Examination.objects.all()
    students = Students.objects.all()
    context = {
        "exams": exams,
        "students": students
    }
    return render(request, 'examlist.html', context)

def take_exam(request, exam_id):
    exam = get_object_or_404(Examination, id=exam_id, is_active=True)
    student = get_object_or_404(Students, user=request.user)
    if ExamResult.objects.filter(student=student, examination=exam).exists():
        messages.error(request, "You have already taken this exam.")    
        return redirect('exam_list')
    questions = exam.questions.prefetch_related('choices').order_by('order')

    if request.method == "POST":
        score = 0
        total = sum(q.marks for q in questions)
    
        for question in questions:

            form = StudentResponseForm(request.POST or None, prefix=f"q_{question.id}", question=question)
            if form.is_valid():
                response = form.save(commit=False)
                response.student = student
                response.question = question
                response.save()
                if response.selected_choice and response.selected_choice.is_correct:
                    score += question.marks
        
        ExamResult.objects.create(
            student=student,
            examination=exam,
            score=score,
            total_possible=total
        )

        messages.success(request, f"Your responses have been submitted successfully {score}/{total}.")
        return redirect('exam_results', exam_id=exam.id)

    forms = []
    for question in questions:
        form = StudentResponseForm(prefix=f"q_{question.id}", question=question)
        forms.append(form)
    context = {
        "exam": exam,
        "questions": questions,
        "forms": forms          
    }
    return render(request, 'take_exam.html', context)

def student_results(request, exam_id):
    exam = get_object_or_404(Examination, id=exam_id)
    student = get_object_or_404(Students, user=request.user)
    result = get_object_or_404(ExamResult, student=student, examination=exam)
    percentage = round((result.score / result.total_possible) * 100, 2) if result.total_possible > 0 else 0
    context = {
        "exam": exam,
        "result": result,
        "percentage": percentage
    }
    return render(request, 'exam_results.html', context)    
def student_results_list(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, 'student_results_list.html', context)

def exam_results(request, exam_id):
    student = get_object_or_404(Students, user=request.user)
    exam=get_object_or_404(Examination, id=exam_id)
    result=get_object_or_404(ExamResult, student=student, examination=exam)
    percentage = round((result.score / result.total_possible) * 100, 2) if result.total_possible > 0 else 0
    responses = StudentResponse.objects.filter(student=student, question__Examinations=exam).select_related('question', 'selected_choice')
    breakdown = []
    for response in responses:
        correct_choice = response.question.choices.filter(is_correct=True).first()
        breakdown.append({
            "question": response.question,
            "selected_choice": response.selected_choice,
            "correct_choice": correct_choice,
            "is_correct": response.selected_choice.is_correct if response.selected_choice else False
        })
    context = {
        "exam": exam,
        "result": result,
        "percentage": percentage,
        "responses": responses,
        "breakdown": breakdown
    }
    return render(request, 'student_results.html', context)

def admin_create_exam(request):
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam created successfully.")
            return redirect('admin_dashboard')
    else:
        form = ExamForm()
    return render(request, 'admin_dashboard/exam_create.html', {'form': form})

def admin_list_exams(request):
    exams = Examination.objects.all()
    context = {
        "exams": exams
    }
    return render(request, 'admin_dashboard/exam_list.html', context)

def admin_exam_edit(request, exam_id):
    exam = get_object_or_404(Examination, id=exam_id)
    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'admin_dashboard/exam_edit.html', {'form': form, 'exam': exam})

def admin_exam_delete(request, exam_id):
    exam = get_object_or_404(Examination, id=exam_id)
    if request.method == "POST":
        exam.delete()
        messages.success(request, "Exam deleted successfully.")
        return redirect('admin_dashboard')
    return render(request, 'admin_dashboard/exam_delete_confirm.html', {'exam': exam})

#question management views
def admin_create_question(request, exam_id):
    exam = get_object_or_404(Examination, id=exam_id)
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.Examinations = exam
            question.save()
            messages.success(request, "Question created successfully.")
            return redirect('admin_exam_edit', exam_id=exam.id)
    else:
        form = QuestionForm()
    return render(request, 'admin_dashboard/question_create.html', {'form': form, 'exam': exam})

def admin_list_question(request, exam_id):
    exam = get_object_or_404(Examination, id=exam_id)
    questions = exam.questions.prefetch_related('choices').order_by('order')
    context = {
        "exam": exam,
        "questions": questions
    }
    return render(request, 'admin_dashboard/question_list.html', context)

def admin_edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Question updated successfully.")
            return redirect('admin_list_question', exam_id=question.Examinations.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'admin_dashboard/question_edit.html', {'form': form, 'question': question})

def admin_delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    exam_id = question.Examinations.id
    if request.method == "POST":
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect('admin_exam_edit', exam_id=exam_id)
    return render(request, 'admin_dashboard/question_delete_confirm.html', {'question': question})

#choice management
def admin_create_choice(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == "POST":
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            messages.success(request, "Choice created successfully.")
            return redirect('admin_list_question', exam_id=question.Examinations.id)
    else:
        form = ChoiceForm()
    return render(request, 'admin_dashboard/choice_create.html', {'form': form, 'question': question})

def admin_edit_choice(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)
    if request.method == "POST":
        form = ChoiceForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            messages.success(request, "Choice updated successfully.")
            return redirect('admin_list_question', exam_id=choice.question.Examinations.id)
    else:
        form = ChoiceForm(instance=choice)
    return render(request, 'admin_dashboard/choice_edit.html', {'form': form, 'choice': choice})

def admin_delete_choice(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)
    question_id = choice.question.id
    if request.method == "POST":
        choice.delete()
        messages.success(request, "Choice deleted successfully.")
        return redirect('admin_list_question', exam_id=choice.question.Examinations.id)
    return render(request, 'admin_dashboard/choice_delete_confirm.html', {'choice': choice})

def search_button(request):
    query = request.GET.get('q')
    if query:
        students = Students.objects.filter(first_name__icontains=query) | Students.objects.filter(last_name__icontains=query)
        exams = Examination.objects.filter(title__icontains=query)
        context = {
            "students": students,
            "exams": exams,
            "query": query
        }
        return render(request, 'admin_dashboard/search.html', context)
    else:
        messages.error(request, "Please enter a search term.")
        return redirect('admin_dashboard')  # Redirect to a relevant page if no query is provided
    

import base64
import json
import cv2
import numpy as np
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .recognizer import identify_face

User = get_user_model()


def face_login_page(request):
    return render(request, "opencv_login.html")


DEFAULT_THRESHOLD = getattr(settings, "FACE_MATCH_THRESHOLD", 70)


def _decode_image(data_url_or_b64):
    if "," in data_url_or_b64:
        data_url_or_b64 = data_url_or_b64.split(",", 1)[1]
    img_bytes = base64.b64decode(data_url_or_b64)
    np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


@require_POST
@csrf_protect
def face_login(request):
    try:
        body = json.loads(request.body)
        image_data = body["image"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"success": False, "reason": "bad_request"}, status=400)

    frame = _decode_image(image_data)
    if frame is None:
        return JsonResponse({"success": False, "reason": "bad_image"}, status=400)

    name, confidence = identify_face(frame)
    if name is None:
        return JsonResponse({"success": False, "reason": "no_face"})

    if confidence > DEFAULT_THRESHOLD:
        return JsonResponse({
            "success": False,
            "reason": "no_match",
            "closest_name": name,
            "confidence": round(confidence, 1),
        })

    try:
        user = User.objects.get(username__iexact=name)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "reason": "no_matching_account"})

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return JsonResponse({
        "success": True,
        "username": user.username,
        "confidence": round(confidence, 1),
    })


import base64
import json

import cv2
import numpy as np
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .recognizer import identify_face

User = get_user_model()


def face_login_page(request):
    """Renders the page with the webcam + 'Log in with my face' button.
    This is the URL you actually open in the browser (GET)."""
    return render(request, "opencv_login.html")

# Fall back to 100 if not set in settings.py
DEFAULT_THRESHOLD = getattr(settings, "FACE_MATCH_THRESHOLD", 100)


def _decode_image(data_url_or_b64):
    """Accepts either a raw base64 string or a data URL like
    'data:image/jpeg;base64,/9j/4AAQ...' and returns an OpenCV BGR image,
    or None if the data was empty/unusable."""
    if "," in data_url_or_b64:
        data_url_or_b64 = data_url_or_b64.split(",", 1)[1]
    if not data_url_or_b64:
        return None
    try:
        img_bytes = base64.b64decode(data_url_or_b64)
    except (base64.binascii.Error, ValueError):
        return None
    if not img_bytes:
        return None
    np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

@login_required
def open_cv_dashboard(request):
    return render(request, "face_dashboard.html")

def face_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('face_login_page')

@require_POST
@csrf_protect
def face_login(request):
    """
    Expects JSON body: {"image": "data:image/jpeg;base64,...."}
    Returns JSON: {"success": true, "username": "alice"}
               or {"success": false, "reason": "no_face" | "no_match"}
    """
    try:
        body = json.loads(request.body)
        image_data = body["image"]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"success": False, "reason": "bad_request"}, status=400)

    frame = _decode_image(image_data)
    if frame is None or frame.size == 0:
        return JsonResponse({"success": False, "reason": "bad_image"}, status=400)

    name, confidence = identify_face(frame)

    if name is None:
        return JsonResponse({"success": False, "reason": "no_face"})

    # LBPH confidence is a DISTANCE — lower means a closer match.
    if confidence > DEFAULT_THRESHOLD:
        return JsonResponse({
            "success": False,
            "reason": "no_match",
            "closest_name": name,          # useful for debugging/tuning threshold
            "confidence": round(confidence, 1),
        })

    try:
        user = User.objects.get(username__iexact=name)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "reason": "no_matching_account"})

    # Explicit backend needed if you have more than one AUTHENTICATION_BACKENDS entry
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    return JsonResponse({
        "success": True,
        "username": user.username,
        "confidence": round(confidence, 1),
        "redirect_url": "/face-dashboard/",  # optional: where to redirect after login
    })
