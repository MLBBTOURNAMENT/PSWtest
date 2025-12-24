from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Avg

from exam.models import ParticipantProfile, Tryout, Question, ParticipantTryout
from exam.forms import TryoutForm, QuestionFormSet
from .forms import ParticipantManualForm

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard_index(request):
    total_participants = ParticipantProfile.objects.count()
    total_tryouts = Tryout.objects.count()
    active_tryouts = Tryout.objects.filter(is_published=True, publish_time__lte=timezone.now()).count()
    
    context = {
        'total_participants': total_participants,
        'total_tryouts': total_tryouts,
        'active_tryouts': active_tryouts,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
@user_passes_test(is_admin)
def participant_list(request):
    participants = ParticipantProfile.objects.select_related('user').all().order_by('day', 'full_name')
    
    # Get active tryouts for monitoring
    active_tryouts = Tryout.objects.filter(
        is_published=True,
        publish_time__lte=timezone.now()
    )
    
    # Check if any tryout is currently active
    has_active_tryout = active_tryouts.exists()
    
    # Get participant tryout status if there's active tryout
    participant_status = {}
    if has_active_tryout:
        for participant in participants:
            tryout_statuses = ParticipantTryout.objects.filter(
                participant=participant,
                tryout__in=active_tryouts
            )
            participant_status[participant.id] = {
                'tryouts': tryout_statuses
            }
    
    context = {
        'participants': participants,
        'has_active_tryout': has_active_tryout,
        'participant_status': participant_status,
    }
    return render(request, 'dashboard/participant_list.html', context)

@login_required
@user_passes_test(is_admin)
def participant_add(request):
    if request.method == 'POST':
        form = ParticipantManualForm(request.POST)
        email = request.POST.get('email')
        
        if form.is_valid():
            try:
                username = email.split('@')[0].lower().replace('.', '_')
                password = get_random_string(8)
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=form.cleaned_data['full_name']
                )
                
                profile = form.save(commit=False)
                profile.user = user
                profile.raw_password = password
                profile.save()
                
                messages.success(request, 'Peserta berhasil ditambahkan.')
                return redirect('dashboard:participant_list')
                
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = ParticipantManualForm()
    
    return render(request, 'dashboard/participant_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def participant_edit(request, pk):
    participant = get_object_or_404(ParticipantProfile, pk=pk)
    
    if request.method == 'POST':
        form = ParticipantManualForm(request.POST, instance=participant)
        email = request.POST.get('email')
        
        if form.is_valid():
            form.save()
            participant.user.email = email
            participant.user.first_name = form.cleaned_data['full_name']
            participant.user.save()
            
            messages.success(request, 'Data peserta berhasil diupdate.')
            return redirect('dashboard:participant_list')
    else:
        form = ParticipantManualForm(instance=participant)
    
    context = {
        'form': form,
        'participant': participant,
        'email': participant.user.email
    }
    return render(request, 'dashboard/participant_form.html', context)

@login_required
@user_passes_test(is_admin)
def participant_delete(request, pk):
    participant = get_object_or_404(ParticipantProfile, pk=pk)
    user = participant.user
    participant.delete()
    user.delete()
    messages.success(request, 'Peserta berhasil dihapus.')
    return redirect('dashboard:participant_list')

@login_required
@user_passes_test(is_admin)
def participant_block(request, pk):
    participant = get_object_or_404(ParticipantProfile, pk=pk)
    participant.blocked = True
    participant.save()
    messages.warning(request, f'Peserta {participant.full_name} telah diblokir.')
    return redirect('dashboard:participant_list')

@login_required
@user_passes_test(is_admin)
def participant_send_email(request, pk):
    participant = get_object_or_404(ParticipantProfile, pk=pk)
    
    try:
        send_participant_card_email(request, participant)
        messages.success(request, f'Email berhasil dikirim ke {participant.full_name}.')
    except Exception as e:
        messages.error(request, f'Gagal mengirim email: {str(e)}')
    
    return redirect('dashboard:participant_list')

@login_required
@user_passes_test(is_admin)
def participant_send_all_emails(request):
    participants = ParticipantProfile.objects.all()
    success_count = 0
    
    for participant in participants:
        try:
            send_participant_card_email(request, participant)
            success_count += 1
        except:
            continue
    
    messages.success(request, f'Berhasil mengirim {success_count} email dari {participants.count()} peserta.')
    return redirect('dashboard:participant_list')

def send_participant_card_email(request, profile):
    user = profile.user
    base_url = request.build_absolute_uri('/')[:-1]
    card_url = base_url + reverse('dashboard:participant_card', args=[profile.pk])
    login_url = base_url + reverse('accounts:login')

    subject = "Kartu Peserta Try Out"

    text_content = f"""
Halo {profile.full_name},

Silakan lihat user dan password kalian di: {card_url}
Gunakan untuk login pada laman: {login_url}
pada saat acara PSW pada jam yang telah ditentukan.

Terima kasih,
Panitia Try Out
"""

    html_content = f"""
<html>
  <body style="font-family: Arial, sans-serif; background:#f5f7fa; padding:16px;">
    <div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:8px;border:1px solid #e5e7eb;">
      <div style="padding:16px 18px;border-bottom:1px solid #e5e7eb;">
        <h2 style="margin:0;font-size:18px;color:#111827;">Kartu Peserta Try Out</h2>
        <p style="margin:4px 0 0;font-size:12px;color:#6b7280;">PSW 2025</p>
      </div>
      <div style="padding:18px;">
        <p style="font-size:14px;color:#111827;margin:0 0 10px;">Halo {{profile.full_name}},</p>
        <p style="font-size:13px;color:#374151;margin:0 0 10px;">
          Silakan lihat user dan password kalian di:
        </p>
        <p style="font-size:13px;margin:0 0 10px;">
          <a href="{card_url}" style="color:#2563eb;text-decoration:none;">{card_url}</a>
        </p>
        <p style="font-size:13px;color:#374151;margin:0 0 10px;">
          Gunakan untuk login pada laman:
        </p>
        <p style="font-size:13px;margin:0 0 10px;">
          <a href="{login_url}" style="color:#2563eb;text-decoration:none;">{login_url}</a>
        </p>
        <p style="font-size:13px;color:#374151;margin:10px 0 0;">
          Pada saat acara PSW pada jam yang telah ditentukan.
        </p>
      </div>
      <div style="padding:12px 18px;border-top:1px solid #e5e7eb;">
        <p style="font-size:12px;color:#6b7280;margin:0;">
          Terima kasih,<br>Panitia Try Out
        </p>
      </div>
    </div>
  </body>
</html>
"""

    msg = EmailMultiAlternatives(subject, text_content, None, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@login_required
def participant_card(request, pk):
    """Public view for participant card - accessible by participant or admin"""
    participant = get_object_or_404(ParticipantProfile, pk=pk)
    
    # Check if user is the participant or admin
    if not (request.user.is_staff or request.user.participantprofile == participant):
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
        return redirect('accounts:login')
    
    base_url = request.build_absolute_uri('/')[:-1]
    login_url = base_url + reverse('accounts:login')
    
    context = {
        'participant': participant,
        'login_url': login_url,
    }
    return render(request, 'dashboard/participant_card.html', context)

# ============ TRYOUT MANAGEMENT ============

@login_required
@user_passes_test(is_admin)
def tryout_list(request):
    tryouts = Tryout.objects.all().order_by('-created_at')

    # tempelkan atribut finished_count dan avg_score ke tiap tryout
    for t in tryouts:
        pts = ParticipantTryout.objects.filter(tryout=t, is_finished=True)
        t.finished_count = pts.count()
        t.avg_score = pts.aggregate(Avg('score'))['score__avg']

    return render(request, 'dashboard/tryout_list.html', {'tryouts': tryouts})

@login_required
@user_passes_test(is_admin)
# create_tryout
def tryout_create(request):
    if request.method == 'POST':
        form = TryoutForm(request.POST)
        formset = QuestionFormSet(request.POST, prefix='questions')
        if form.is_valid() and formset.is_valid():
            tryout = form.save()
            formset.instance = tryout
            formset.save()
            return redirect('dashboard:tryout_settings', pk=tryout.pk)
    else:
        form = TryoutForm()
        formset = QuestionFormSet(prefix='questions')
    return render(request, 'dashboard/tryout_form.html', {'form': form, 'formset': formset})

# tryout_edit
def tryout_edit(request, pk):
    tryout = get_object_or_404(Tryout, pk=pk)
    if request.method == 'POST':
        form = TryoutForm(request.POST, instance=tryout)
        formset = QuestionFormSet(request.POST, instance=tryout, prefix='questions')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('dashboard:tryout_list')
    else:
        form = TryoutForm(instance=tryout)
        formset = QuestionFormSet(instance=tryout, prefix='questions')
    return render(request, 'dashboard/tryout_form.html', {'form': form, 'formset': formset, 'tryout': tryout})


@login_required
@user_passes_test(is_admin)
def tryout_settings(request, pk):
    tryout = get_object_or_404(Tryout, pk=pk)
    
    if request.method == 'POST':
        form = TryoutForm(request.POST, instance=tryout)
        
        if form.is_valid():
            form.save()
            
            # Publish if requested
            if 'publish' in request.POST:
                tryout.is_published = True
                tryout.save()
                messages.success(request, 'Try out berhasil dipublish.')
            else:
                messages.success(request, 'Settings berhasil disimpan.')
            
            return redirect('dashboard:tryout_list')
    else:
        form = TryoutForm(instance=tryout)
    
    context = {
        'form': form,
        'tryout': tryout,
    }
    return render(request, 'dashboard/tryout_settings.html', context)

@login_required
@user_passes_test(is_admin)
def tryout_edit(request, pk):
    tryout = get_object_or_404(Tryout, pk=pk)
    
    if request.method == 'POST':
        form = TryoutForm(request.POST, instance=tryout)
        formset = QuestionFormSet(request.POST, instance=tryout)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            messages.success(request, 'Try out berhasil diupdate.')
            return redirect('dashboard:tryout_list')
    else:
        form = TryoutForm(instance=tryout)
        formset = QuestionFormSet(instance=tryout)
    
    context = {
        'form': form,
        'formset': formset,
        'tryout': tryout,
    }
    return render(request, 'dashboard/tryout_form.html', context)

@login_required
@user_passes_test(is_admin)
def tryout_delete(request, pk):
    tryout = get_object_or_404(Tryout, pk=pk)
    tryout.delete()
    messages.success(request, 'Try out berhasil dihapus.')
    return redirect('dashboard:tryout_list')
