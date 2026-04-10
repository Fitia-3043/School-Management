from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.students.models import Student
from apps.staffs.models import Staff

User = get_user_model()

class Command(BaseCommand):
    help = 'Créer des utilisateurs de test pour chaque rôle'

    def handle(self, *args, **options):
        # Créer un administrateur
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@school.com',
                password='admin123',
                first_name='Admin',
                last_name='System',
                role='admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Administrateur créé: admin/admin123'))
        else:
            self.stdout.write(self.style.WARNING('Administrateur existe déjà'))

        # Créer un utilisateur personnel
        if not User.objects.filter(username='enseignant').exists():
            # D'abord créer un staff si nécessaire
            staff, created = Staff.objects.get_or_create(
                surname='Dupont',
                firstname='Jean',
                defaults={
                    'other_name': 'Marie',
                    'gender': 'male',
                    'mobile_number': '1234567890',
                    'address': 'Adresse de l\'enseignant'
                }
            )
            
            staff_user = User.objects.create_user(
                username='enseignant',
                email='enseignant@school.com',
                password='enseignant123',
                first_name='Jean',
                last_name='Dupont',
                role='staff',
                staff_profile=staff
            )
            self.stdout.write(self.style.SUCCESS('Personnel créé: enseignant/enseignant123'))
        else:
            self.stdout.write(self.style.WARNING('Personnel existe déjà'))

        # Créer un utilisateur étudiant
        if not User.objects.filter(username='etudiant').exists():
            # D'abord créer un étudiant si nécessaire
            from apps.corecode.models import StudentClass
            student_class = StudentClass.objects.first()
            
            student, created = Student.objects.get_or_create(
                registration_number='ETU001',
                defaults={
                    'surname': 'Martin',
                    'firstname': 'Lucas',
                    'other_name': 'Pierre',
                    'gender': 'male',
                    'current_class': student_class,
                    'parent_mobile_number': '0987654321',
                    'address': 'Adresse de l\'étudiant'
                }
            )
            
            student_user = User.objects.create_user(
                username='etudiant',
                email='etudiant@school.com',
                password='etudiant123',
                first_name='Lucas',
                last_name='Martin',
                role='student',
                student_profile=student
            )
            self.stdout.write(self.style.SUCCESS('Étudiant créé: etudiant/etudiant123'))
        else:
            self.stdout.write(self.style.WARNING('Étudiant existe déjà'))

        self.stdout.write(self.style.SUCCESS('\nUtilisateurs de test créés avec succès!'))
        self.stdout.write('\nIdentifiants de connexion:')
        self.stdout.write('Administrateur: admin / admin123')
        self.stdout.write('Personnel: enseignant / enseignant123')
        self.stdout.write('Étudiant: etudiant / etudiant123')
