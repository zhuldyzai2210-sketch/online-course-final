
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Course, Choice, Enrollment, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course}
    )


@login_required
@require_POST
def submit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    submission = Submission.objects.create(enrollment=enrollment)

    selected_ids = request.POST.getlist("choices")

    choices = Choice.objects.filter(
        id__in=selected_ids,
        question__lesson__course=course
    )

    submission.choices.set(choices)

    return redirect(
        "show_exam_result",
        course_id=course.id,
        submission_id=submission.id
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, id=course_id)

    submission = get_object_or_404(
        Submission,
        id=submission_id,
        enrollment__user=request.user,
        enrollment__course=course
    )

    questions = list(
        course.lessons.prefetch_related(
            "questions__choices"
        )
    )

    selected_ids = set(
        submission.choices.values_list("id", flat=True)
    )

    total_score = 0
    earned_score = 0
    results = []

    for lesson in questions:
        for question in lesson.questions.all():
            total_score += question.grade

            correct_ids = {
                choice.id
                for choice in question.choices.all()
                if choice.is_correct
            }

            answer_ids = {
                choice.id
                for choice in question.choices.all()
                if choice.id in selected_ids
            }

            is_correct = (
                answer_ids == correct_ids
                and bool(correct_ids)
            )

            if is_correct:
                earned_score += question.grade

            results.append({
                "question": question,
                "is_correct": is_correct,
                "choices": question.choices.all(),
                "selected_ids": answer_ids,
            })

    percentage = (
        round(earned_score / total_score * 100)
        if total_score > 0
        else 0
    )

    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "course": course,
            "results": results,
            "earned_score": earned_score,
            "total_score": total_score,
            "percentage": percentage,
            "passed": total_score > 0 and percentage >= 70,
        }
    )
