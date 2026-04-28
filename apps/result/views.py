from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, View

from apps.students.models import Student

from .forms import CreateResults, EditResults
from .models import Result


@login_required
def create_result(request):
    # Vérification des permissions : mpampianatra ihany no afaka mi-cree resultat
    if hasattr(request.user, 'role') and request.user.role == 'student':
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Les étudiants ne peuvent pas créer de résultats.")
    
    # personnel : mpianatra ao ihany
    if hasattr(request.user, 'role') and request.user.role == 'staff':
        students = Student.objects.all()  # tous les étudiants
    else:
        # Admin : voir tous les étudiants
        students = Student.objects.all()
    
    if request.method == "POST":

        # avy ni-visiter paage faharoa
        if "finish" in request.POST:
            form = CreateResults(request.POST)
            if form.is_valid():
                subjects = form.cleaned_data["subjects"]
                session = form.cleaned_data["session"]
                term = form.cleaned_data["term"]
                students_ids = request.POST.get("students", "")
                results = []
                
                if not students_ids:
                    messages.error(request, "Aucun étudiant sélectionné")
                    return redirect("create-result")
                
                for student_id in students_ids.split(","):
                    try:
                        stu = Student.objects.get(pk=student_id)
                        print(f"DEBUG: Traitement étudiant {stu.id} - {stu} - Classe: {stu.current_class}")
                        
                        if stu.current_class:
                            print(f"DEBUG: Étudiant {stu} a une classe, traitement des matières...")
                            for subject in subjects:
                                print(f"DEBUG: Matière {subject}")
                                check = Result.objects.filter(
                                    session=session,
                                    term=term,
                                    current_class=stu.current_class,
                                    subject=subject,
                                    student=stu,
                                ).first()
                                if not check:
                                    print(f"DEBUG: Création résultat pour {stu} - {subject}")
                                    results.append(
                                        Result(
                                            session=session,
                                            term=term,
                                            current_class=stu.current_class,
                                            subject=subject,
                                            student=stu,
                                        )
                                    )
                                else:
                                    print(f"DEBUG: Résultat existe déjà pour {stu} - {subject}")
                        else:
                            print(f"DEBUG: Étudiant {stu} n'a pas de classe actuelle, ignoré")
                    except Student.DoesNotExist:
                        print(f"DEBUG: Étudiant ID {student_id} non trouvé")
                        continue

                print(f"DEBUG: Total résultats à créer: {len(results)}")
                ignored_count = 0
                for student_id in students_ids.split(','):
                    if Result.objects.filter(student_id=student_id, session=session, term=term, subject__in=subjects).exists():
                        ignored_count += 1
                print(f"DEBUG: Étudiants ignorés (résultats existants): {ignored_count}")
                
                if results:
                    Result.objects.bulk_create(results)
                    messages.success(request, f"{len(results)} nouveaux résultats créés avec succès")
                    student_ids = [str(stu.id) for stu in Student.objects.filter(
                        id__in=students_ids.split(",")
                    )]
                    subject_ids = [str(subject.id) for subject in subjects]
                    redirect_url = f"/result/edit-results/?students={','.join(student_ids)}&subjects={','.join(subject_ids)}"
                    print(f"DEBUG: Redirection vers: {redirect_url}")
                    return redirect(redirect_url)
                else:
                    messages.warning(request, "Aucun nouveau résultat créé. Les étudiants sélectionnés ont déjà des résultats pour ces matières.")
                    return redirect("create-result")
            else:
                messages.error(request, "Formulaire invalide")
                return redirect("create-result")

        # rehefa avy nisifidy mpianatra
        id_list = request.POST.getlist("students")
        if id_list:
            form = CreateResults(
                initial={
                    "session": request.current_session,
                    "term": request.current_term,
                }
            )
            studentlist = ",".join(id_list)
            return render(
                request,
                "result/create_result_page2.html",
                {"students": studentlist, "form": form, "count": len(id_list)},
            )
        else:
            messages.warning(request, "Vous n'avez sélectionné aucun étudiant.")
    return render(request, "result/create_result.html", {"students": students})


@login_required
def edit_results(request):
    if hasattr(request.user, 'role') and request.user.role == 'student':
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Les étudiants ne peuvent pas modifier de résultats.")
    
    if request.method == "POST":
        form = EditResults(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Results successfully updated")
            return redirect("edit-results")
    else:
        students_param = request.GET.get('students', '')
        subjects_param = request.GET.get('subjects', '')
        
        print(f"DEBUG: students_param = {students_param}")
        print(f"DEBUG: subjects_param = {subjects_param}")
        
        if students_param or subjects_param:
            # filtre
            filters = {
                'session': request.current_session,
                'term': request.current_term
            }
            
            if students_param:
                student_ids = students_param.split(',')
                filters['student_id__in'] = student_ids
                print(f"DEBUG: Filtrage par étudiants: {student_ids}")
                
            if subjects_param:
                subject_ids = subjects_param.split(',')
                filters['subject_id__in'] = subject_ids
                print(f"DEBUG: Filtrage par matières: {subject_ids}")
            
            results = Result.objects.filter(**filters)
            print(f"DEBUG: Nombre de résultats filtrés: {results.count()}")
        else:
            # par défaut : résultat rehetra
            results = Result.objects.filter(
                session=request.current_session, term=request.current_term
            )
            print(f"DEBUG: Comportement par défaut - Nombre total de résultats: {results.count()}")
        
        form = EditResults(queryset=results)
    return render(request, "result/edit_results.html", {"formset": form})


class ResultListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('search', '').strip()
        
        if hasattr(request.user, 'role'):
            if request.user.role == 'student':
                results = Result.objects.filter(
                    student=request.user.student_profile,
                    session=request.current_session, 
                    term=request.current_term
                )
            elif request.user.role in ['admin', 'staff']:
                results = Result.objects.filter(
                    session=request.current_session, term=request.current_term
                )
            else:
                results = Result.objects.none()
        else:
            results = Result.objects.filter(
                session=request.current_session, term=request.current_term
            )
        
        if search_query:
            results = results.filter(
                student__surname__icontains=search_query
            ) | results.filter(
                student__firstname__icontains=search_query
            ) | results.filter(
                student__other_name__icontains=search_query
            ) | results.filter(
                student__current_class__name__icontains=search_query
            ) | results.filter(
                subject__name__icontains=search_query
            )
        
        bulk = {}

        if results.exists():
            for result in results:
                test_total = 0
                exam_total = 0
                subjects = []
                for subject in results:
                    if subject.student == result.student:
                        subjects.append(subject)
                        test_total += subject.test_score
                        exam_total += subject.exam_score

                bulk[result.student.id] = {
                    "student": result.student,
                    "subjects": subjects,
                    "test_total": test_total,
                    "exam_total": exam_total,
                    "total_total": test_total + exam_total,
                }
        else:
            # Message hafakely
            if search_query:
                from django.contrib import messages
                messages.info(request, f"Aucun résultat trouvé pour \"{search_query}\". Essayez avec un autre nom.")
            else:
                from django.contrib import messages
                messages.info(request, "Aucun résultat trouvé pour la session et le trimestre actuels. Veuillez d'abord ajouter des résultats.")

        context = {"results": bulk}
        return render(request, "result/all_results.html", context)
