from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('staff', 'Personnel (Enseignant)'),
        ('student', 'Étudiant'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='student',
        verbose_name='Rôle'
    )
    
    # relations @modele efa misy
    student_profile = models.OneToOneField(
        'students.Student', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_profile',
        verbose_name='Profil étudiant'
    )
    
    staff_profile = models.OneToOneField(
        'staffs.Staff', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_profile',
        verbose_name='Profil personnel'
    )
    
    # Champs tsy tena iilaina akory
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name='Téléphone'
    )
    
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        verbose_name='Date de naissance'
    )
    
    address = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Adresse'
    )
    
    is_first_login = models.BooleanField(
        default=True,
        verbose_name='Première connexion'
    )
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_staff_user(self):
        return self.role == 'staff'
    
    @property
    def is_student_user(self):
        return self.role == 'student'
    
    def get_profile(self):
        """Retourne le profil associé selon le rôle"""
        if self.role == 'student' and self.student_profile:
            return self.student_profile
        elif self.role == 'staff' and self.staff_profile:
            return self.staff_profile
        return None
