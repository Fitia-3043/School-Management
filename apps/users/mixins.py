from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour restreindre l'accès aux administrateurs uniquement"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Vous n'avez pas les permissions d'administrateur.")
        return super().handle_no_permission()


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour restreindre l'accès au personnel (enseignants) uniquement"""
    
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff_user or self.request.user.is_admin
        )
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Vous n'avez pas les permissions du personnel.")
        return super().handle_no_permission()


class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour restreindre l'accès aux étudiants uniquement"""
    
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_student_user or self.request.user.is_admin
        )
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Vous n'avez pas les permissions d'étudiant.")
        return super().handle_no_permission()


class AdminOrStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin pour restreindre l'accès aux administrateurs et au personnel"""
    
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or self.request.user.is_staff_user
        )
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Accès réservé au personnel administratif.")
        return super().handle_no_permission()
