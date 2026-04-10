from django.core.management.base import BaseCommand
from apps.result.models import Result
from apps.students.models import Student
from apps.corecode.models import AcademicSession, AcademicTerm, Subject
import random

class Command(BaseCommand):
    help = 'Create sample results for testing'

    def handle(self, *args, **kwargs):
        # Get current session and term
        current_session = AcademicSession.objects.get(current=True)
        current_term = AcademicTerm.objects.get(current=True)
        
        # Get some students and subjects
        students = list(Student.objects.all()[:10])  # First 10 students
        subjects = list(Subject.objects.all()[:5])  # First 5 subjects
        
        # Clear existing results for current session/term
        Result.objects.filter(session=current_session, term=current_term).delete()
        
        # Create results
        results_to_create = []
        for student in students:
            if student.current_class:
                for subject in subjects:
                    results_to_create.append(
                        Result(
                            student=student,
                            session=current_session,
                            term=current_term,
                            current_class=student.current_class,
                            subject=subject,
                            test_score=random.randint(10, 20),
                            exam_score=random.randint(20, 40)
                        )
                    )
        
        # Bulk create
        Result.objects.bulk_create(results_to_create)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(results_to_create)} results for {len(students)} students'))
        self.stdout.write(f'Session: {current_session}')
        self.stdout.write(f'Term: {current_term}')
