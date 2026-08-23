from django.urls import include, path
from .views import students, fees, program, add_student, add_fees, add_program, index, exam_list, take_exam, exam_results
from .views import student_results_list, student_results, student_login, student_logout, student_register, admin_dashboard, admin_login, admin_logout
from .views import admin_create_question, admin_create_choice, admin_edit_question, admin_edit_choice, admin_delete_question, admin_delete_choice
from .views import admin_create_exam, admin_exam_edit, admin_exam_delete, admin_list_exams, admin_list_question, search_button
from . import views

urlpatterns = [
    path("", student_login, name="student_login"),
    path("home/", index, name="home"),
    path("students/", students, name="students"),
    path("fees/", fees, name="fees"),
    path("programs/", program, name="programs"),
    path("exams/", exam_list, name="exam_list"),
    path("take-exam/<int:exam_id>/", take_exam, name="take_exam"),
    path("exam-results/<int:exam_id>/", exam_results, name="exam_results"),
    path("add-student/", add_student, name="add_student"),
    path("add-fees/", add_fees, name="add_fees"),
    path("add-program/", add_program, name="add_program"),
    path("results/", student_results_list, name="student_results_list"),
    path("results/<int:student_id>/", student_results, name="student_results"),    
    path("logout/", student_logout, name="student_logout"),
    path("register/", student_register, name="student_register"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin-login/", admin_login, name="admin_login"),
    path("admin-logout/", admin_logout, name="admin_logout"),
    path("admin-create-exam/", admin_create_exam, name="admin_create_exam"),
    path("admin-exam-edit/<int:exam_id>/", admin_exam_edit, name="admin_exam_edit"),
    path("admin-exam-delete/<int:exam_id>/", admin_exam_delete, name="admin_exam_delete"),
    path("admin-create-question/<int:exam_id>/", admin_create_question, name="admin_create_question"),
    path("admin-create-choice/<int:question_id>/", admin_create_choice, name="admin_create_choice"),
    path("admin-edit-question/<int:question_id>/", admin_edit_question, name="admin_edit_question"),
    path("admin-edit-choice/<int:choice_id>/", admin_edit_choice, name="admin_edit_choice"),
    path("admin-delete-question/<int:question_id>/", admin_delete_question, name="admin_delete_question"),
    path("admin-delete-choice/<int:choice_id>/", admin_delete_choice, name="admin_delete_choice"),
    path("admin-list-exams/", admin_list_exams, name="admin_list_exams"),
    path("admin-list-question/<int:exam_id>/", admin_list_question, name="admin_list_question"),
    path("search/", views.search_button, name="search"),
    path("face-login/", views.face_login_page, name="face_login_page"), 
    path("face-login/submit/", views.face_login, name="face_login"),
    path("face-dashboard/", views.open_cv_dashboard, name="face_dashboard"),
    path("face-logout/", views.face_logout, name="face_logout"),
]
