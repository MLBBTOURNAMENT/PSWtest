from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def participant_login(request):
    if request.user.is_authenticated:
        return redirect('exam:tryout_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'participantprofile'):
                if user.participantprofile.blocked:
                    messages.error(request, 'Akun Anda telah diblokir.')
                else:
                    login(request, user)
                    return redirect('exam:tryout_list')
            elif user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Akun tidak valid.')
        else:
            messages.error(request, 'Username atau password salah.')
    
    blocked = request.GET.get('blocked')
    return render(request, 'accounts/login.html', {'blocked': blocked})

def participant_logout(request):
    logout(request)
    return redirect('accounts:login')
