from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import timedelta

from .models import Tryout, ParticipantTryout, ParticipantAnswer, Question

@login_required
def tryout_list(request):
    """Display all published tryouts for participant"""
    if not hasattr(request.user, 'participantprofile'):
        return redirect('dashboard:index')
    
    profile = request.user.participantprofile
    tryouts = Tryout.objects.filter(is_published=True).order_by('publish_time')
    
    # Get participant status for each tryout
    tryout_status = {}
    for tryout in tryouts:
        try:
            pt = ParticipantTryout.objects.get(participant=profile, tryout=tryout)
            tryout_status[tryout.id] = {
                'started': pt.started_at is not None,
                'finished': pt.is_finished,
                'can_start': False
            }
        except ParticipantTryout.DoesNotExist:
            # Check if tryout is accessible (published and time has come)
            now = timezone.now()
            can_start = tryout.is_published and now >= tryout.publish_time
            tryout_status[tryout.id] = {
                'started': False,
                'finished': False,
                'can_start': can_start
            }
    
    context = {
        'profile': profile,
        'tryouts': tryouts,
        'tryout_status': tryout_status,
        'now': timezone.now(),
    }
    return render(request, 'exam/tryout_list.html', context)

@login_required
def start_tryout(request, pk):
    """Start a tryout"""
    if not hasattr(request.user, 'participantprofile'):
        return redirect('dashboard:index')
    
    profile = request.user.participantprofile
    tryout = get_object_or_404(Tryout, pk=pk)
    
    # Check if tryout is accessible
    now = timezone.now()
    if not tryout.is_published or now < tryout.publish_time:
        return redirect('exam:tryout_list')
    
    # Get or create participant tryout
    pt, created = ParticipantTryout.objects.get_or_create(
        participant=profile,
        tryout=tryout
    )
    
    # Check if already finished
    if pt.is_finished:
        return redirect('exam:tryout_list')
    
    # Set start time if first time
    if not pt.started_at:
        pt.started_at = now
        pt.save()
    
    # Check if time is up
    end_time = pt.started_at + timedelta(minutes=tryout.work_time_minutes)
    if now > end_time:
        pt.is_finished = True
        pt.finished_at = now
        pt.save()
        return redirect('exam:tryout_list')
    
    return redirect('exam:take_exam', pk=pk)

@login_required
def take_exam(request, pk):
    """Main exam page"""
    if not hasattr(request.user, 'participantprofile'):
        return redirect('dashboard:index')
    
    profile = request.user.participantprofile
    tryout = get_object_or_404(Tryout, pk=pk)
    
    # Get participant tryout
    try:
        pt = ParticipantTryout.objects.get(participant=profile, tryout=tryout)
    except ParticipantTryout.DoesNotExist:
        return redirect('exam:start_tryout', pk=pk)
    
    # Check if finished
    if pt.is_finished:
        return redirect('exam:tryout_list')
    
    # Check time limit
    now = timezone.now()
    end_time = pt.started_at + timedelta(minutes=tryout.work_time_minutes)
    
    if now > end_time:
        pt.is_finished = True
        pt.finished_at = now
        pt.save()
        return redirect('exam:tryout_list')
    
    # Get all questions
    questions = tryout.questions.all().order_by('number')
    
    # Get existing answers
    existing_answers = {}
    for answer in ParticipantAnswer.objects.filter(participant_tryout=pt):
        existing_answers[answer.question.id] = answer.selected_option
    
    # Calculate remaining time in seconds
    remaining_seconds = int((end_time - now).total_seconds())
    
    context = {
        'profile': profile,
        'tryout': tryout,
        'questions': questions,
        'existing_answers': existing_answers,
        'participant_tryout': pt,
        'remaining_seconds': remaining_seconds,
        'end_time': end_time,
    }
    return render(request, 'exam/take_exam.html', context)

@require_POST
@login_required
def save_answer(request, pk):
    """AJAX endpoint to save answer"""
    if not hasattr(request.user, 'participantprofile'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    profile = request.user.participantprofile
    tryout = get_object_or_404(Tryout, pk=pk)
    
    try:
        pt = ParticipantTryout.objects.get(participant=profile, tryout=tryout)
    except ParticipantTryout.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tryout not found'})
    
    if pt.is_finished:
        return JsonResponse({'success': False, 'error': 'Tryout already finished'})
    
    question_id = request.POST.get('question_id')
    selected_option = request.POST.get('selected_option')
    
    question = get_object_or_404(Question, id=question_id, tryout=tryout)
    
    # Save or update answer
    answer, created = ParticipantAnswer.objects.update_or_create(
        participant_tryout=pt,
        question=question,
        defaults={'selected_option': selected_option}
    )
    
    return JsonResponse({'success': True})

@require_POST
@login_required
def submit_exam(request, pk):
    if not hasattr(request.user, 'participantprofile'):
        return redirect('dashboard:index')

    profile = request.user.participantprofile
    tryout = get_object_or_404(Tryout, pk=pk)

    try:
        pt = ParticipantTryout.objects.get(participant=profile, tryout=tryout)
    except ParticipantTryout.DoesNotExist:
        return redirect('exam:tryout_list')

    # hitung skor
    from .models import ParticipantAnswer, Question
    answers = ParticipantAnswer.objects.filter(participant_tryout=pt).select_related('question')
    total_score = 0.0
    max_score = 0.0

    for q in Question.objects.filter(tryout=tryout):
        max_score += q.score
    for ans in answers:
        if ans.selected_option == ans.question.correct_option:
            total_score += ans.question.score

    pt.is_finished = True
    pt.finished_at = timezone.now()
    pt.score = total_score
    pt.max_score = max_score
    pt.save()

    return redirect('exam:thank_you', pk=tryout.id)

@login_required
def thank_you(request, pk):
    if not hasattr(request.user, 'participantprofile'):
        return redirect('dashboard:index')
    tryout = get_object_or_404(Tryout, pk=pk)
    return render(request, 'exam/thank_you.html', {'tryout': tryout})

@require_POST
@login_required
def track_out_of_app(request, pk):
    """AJAX endpoint to track when user leaves app"""
    if not hasattr(request.user, 'participantprofile'):
        return JsonResponse({'success': False})
    
    profile = request.user.participantprofile
    tryout = get_object_or_404(Tryout, pk=pk)
    
    try:
        pt = ParticipantTryout.objects.get(participant=profile, tryout=tryout)
        pt.out_of_app_count += 1
        pt.save()
        
        return JsonResponse({'success': True, 'count': pt.out_of_app_count})
    except ParticipantTryout.DoesNotExist:
        return JsonResponse({'success': False})
