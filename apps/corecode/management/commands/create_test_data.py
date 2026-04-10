from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.finance.models import Invoice
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Create test data for the school management system'

    def handle(self, *args, **kwargs):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@school.com', 'admin123')
            self.stdout.write('Admin user created')

        # Create academic sessions
        sessions = ['2023-2024', '2024-2025', '2025-2026']
        for i, session_name in enumerate(sessions):
            AcademicSession.objects.get_or_create(
                name=session_name,
                defaults={'current': i == 1}  # 2024-2025 is current
            )

        # Create academic terms
        terms = ['Premier Trimestre', 'Deuxième Trimestre', 'Troisième Trimestre']
        for i, term_name in enumerate(terms):
            AcademicTerm.objects.get_or_create(
                name=term_name,
                defaults={'current': i == 0}  # Premier Trimestre is current
            )

        # Create classes
        classes = [
            '6ème A', '6ème B', '5ème A', '5ème B', 
            '4ème A', '4ème B', '3ème A', '3ème B',
            '2nde A', '2nde B', '1ère A', '1ère B', 'Tle A', 'Tle B'
        ]
        for class_name in classes:
            StudentClass.objects.get_or_create(name=class_name)

        # Create subjects
        subjects = [
            'Mathématiques', 'Français', 'Anglais', 'Histoire-Géographie',
            'Physique-Chimie', 'SVT', 'Technologie', 'EPS',
            'Musique', 'Arts Plastiques', 'Espagnol', 'Allemand'
        ]
        for subject_name in subjects:
            Subject.objects.get_or_create(name=subject_name)

        # Create staff members
        staff_data = [
            {'surname': 'Dupont', 'firstname': 'Jean', 'gender': 'Male', 'status': 'Active'},
            {'surname': 'Martin', 'firstname': 'Marie', 'gender': 'Female', 'status': 'Active'},
            {'surname': 'Bernard', 'firstname': 'Pierre', 'gender': 'Male', 'status': 'Active'},
            {'surname': 'Petit', 'firstname': 'Sophie', 'gender': 'Female', 'status': 'Active'},
            {'surname': 'Durand', 'firstname': 'Michel', 'gender': 'Male', 'status': 'Active'},
        ]

        for staff_info in staff_data:
            staff, created = Staff.objects.get_or_create(
                surname=staff_info['surname'],
                firstname=staff_info['firstname'],
                defaults={
                    'gender': staff_info['gender'],
                    'current_status': staff_info['status'],
                    'mobile_number': f'06{random.randint(10000000, 99999999)}',
                    'address': f'{random.randint(1, 100)} Rue de l\'École, Paris',
                    'others': 'Enseignant expérimenté'
                }
            )
            if created:
                # Create user account for staff
                username = f"{staff_info['surname'].lower()}{staff_info['firstname'].lower()}"
                User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@school.com',
                        'first_name': staff_info['firstname'],
                        'last_name': staff_info['surname']
                    }
                )

        # Create students
        first_names = ['Lucas', 'Emma', 'Louis', 'Chloé', 'Hugo', 'Léa', 'Nathan', 'Manon']
        surnames = ['Martin', 'Bernard', 'Dubois', 'Petit', 'Durand', 'Leroy', 'Moreau', 'Simon']
        
        all_classes = list(StudentClass.objects.all())
        
        for i in range(40):  # Create 40 students
            surname = random.choice(surnames)
            firstname = random.choice(first_names)
            current_class = random.choice(all_classes)
            
            student, created = Student.objects.get_or_create(
                registration_number=f'STU{2024}{i+1:03d}',
                defaults={
                    'surname': surname,
                    'firstname': firstname,
                    'current_class': current_class,
                    'gender': random.choice(['Male', 'Female']),
                    'parent_mobile_number': f'06{random.randint(10000000, 99999999)}',
                    'address': f'{random.randint(1, 100)} Rue des Écoles, Paris',
                    'others': 'Élève régulier',
                    'current_status': 'Active'
                }
            )

        # Create some invoices
        students = list(Student.objects.all())
        current_session = AcademicSession.objects.get(current=True)
        current_term = AcademicTerm.objects.get(current=True)
        all_classes = list(StudentClass.objects.all())
        
        for i, student in enumerate(students[:20]):  # Create invoices for first 20 students
            invoice, created = Invoice.objects.get_or_create(
                student=student,
                session=current_session,
                term=current_term,
                class_for=random.choice(all_classes),
                defaults={
                    'status': random.choice(['active', 'closed']),
                    'balance_from_previous_term': random.randint(0, 100)
                }
            )
            
            # Create invoice items
            if created:
                from apps.finance.models import InvoiceItem, Receipt
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description='Frais de scolarité',
                    amount=500
                )
                
                # Create some receipts
                if random.random() > 0.3:  # 70% chance of payment
                    Receipt.objects.create(
                        invoice=invoice,
                        amount_paid=500,
                        comment='Paiement complet'
                    )
                elif random.random() > 0.5:  # Partial payment
                    Receipt.objects.create(
                        invoice=invoice,
                        amount_paid=250,
                        comment='Acompte'
                    )

        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))
        self.stdout.write(f'Created: {StudentClass.objects.count()} classes')
        self.stdout.write(f'Created: {Subject.objects.count()} subjects')
        self.stdout.write(f'Created: {Staff.objects.count()} staff members')
        self.stdout.write(f'Created: {Student.objects.count()} students')
        self.stdout.write(f'Created: {Invoice.objects.count()} invoices')
