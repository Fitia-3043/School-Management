from .models import AcademicSession, AcademicTerm


class SiteWideConfigs:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_session = AcademicSession.objects.get(current=True)
        current_term = AcademicTerm.objects.filter(current=True).first()

        request.current_session = current_session
        request.current_term = current_term

        response = self.get_response(request)

        return response
