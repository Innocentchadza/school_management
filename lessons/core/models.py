from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Program(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Students(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    program = models.ForeignKey(Program, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class SchoolFees(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"SchoolFees for {self.student} - {self.amount} on {self.date}"

class Examination(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=60)
    total_marks = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title

class Question(models.Model):
    Examinations = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    marks = models.IntegerField(default=1)
    order = models.IntegerField(default=1)

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class StudentResponse(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'question')

class ExamResult(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_possible = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'examination')

class search(models.Model):
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query
