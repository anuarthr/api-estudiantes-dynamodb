from django.urls import path

from estudiantes.views import EstudianteDetailView, EstudiantesListView

urlpatterns = [
    path("estudiantes/", EstudiantesListView.as_view()),
    path("estudiantes/<str:id>/", EstudianteDetailView.as_view()),
]
