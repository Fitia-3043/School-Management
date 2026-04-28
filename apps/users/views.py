from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, PasswordChangeForm
from .models import CustomUser


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "Vous avez été déconnecté avec succès.")
        return super().dispatch(request, *args, **kwargs)


class SignUpView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.")
        return response


@login_required
def profile_view(request):
    """Vue pour afficher et modifier le profil utilisateur"""
    if request.method == 'POST':
        if 'change_password' in request.POST:
            # fanovana mot de passe
            form = PasswordChangeForm(request.POST, instance=request.user)
            if form.is_valid():
                if request.user.check_password(form.cleaned_data.get('current_password')):
                    request.user.set_password(form.cleaned_data.get('new_password'))
                    request.user.save()
                    messages.success(request, "Votre mot de passe a été changé avec succès.")
                    return redirect('profile')
                else:
                    messages.error(request, "Le mot de passe actuel est incorrect.")
        else:
            # fanovana profil
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Votre profil a été mis à jour avec succès.")
                return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {
        'form': form,
        'password_form': PasswordChangeForm(),
        'user': request.user
    })


@login_required
def dashboard_view(request):
    """Tableau de bord selon le rôle de l'utilisateur"""
    user = request.user
    
    if user.is_admin:
        # Dashboard an'admin
        from apps.students.models import Student
        from apps.staffs.models import Staff
        from apps.finance.models import Invoice
        from apps.corecode.models import AcademicSession, AcademicTerm
        
        context = {
            'total_students': Student.objects.count(),
            'total_staff': Staff.objects.count(),
            'total_invoices': Invoice.objects.count(),
            'current_session': AcademicSession.objects.filter(current=True).first(),
            'current_term': AcademicTerm.objects.filter(current=True).first(),
            'recent_students': Student.objects.all().order_by('-id')[:5],
        }
        return render(request, 'users/admin_dashboard.html', context)
    
    elif user.is_staff_user:
        # Dashboard perso (mpampianatra)
        if user.staff_profile:
            # Maka matiere sy class an-mpampianatra
            context = {
                'staff': user.staff_profile,
                'user': user,
            }
            return render(request, 'users/staff_dashboard.html', context)
        else:
            messages.warning(request, "Votre profil personnel n'est pas configuré.")
            return redirect('profile')
    
    elif user.is_student_user:
        # Dashboard mpianatra
        if user.student_profile:
            from apps.finance.models import Invoice
            from apps.result.models import Result
            
            context = {
                'student': user.student_profile,
                'user': user,
                'invoices': Invoice.objects.filter(student=user.student_profile),
                'results': Result.objects.filter(student=user.student_profile),
            }
            return render(request, 'users/student_dashboard.html', context)
        else:
            messages.warning(request, "Votre profil étudiant n'est pas configuré.")
            return redirect('profile')
    
    # par défaut
    return render(request, 'users/dashboard.html', {'user': user})
