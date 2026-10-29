
from django.contrib import admin
from django.contrib.auth.models import User

from .models import (
    Course,
    Lesson,
    Enrollment,
    Question,
    Choice,
    Submission,
)

# Task 2: Admin configuration

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "lesson", "grade")
    search_fields = ("question_text",)
    inlines = [ChoiceInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    inlines = [QuestionInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "enrolled_at")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "submitted_at")
