from django.urls import path

from notas.views import NotaDetalleView, NotasEstudianteView, NotasView

urlpatterns = [
    path("notas/", NotasView.as_view()),
    path("estudiantes/<str:id>/notas/", NotasEstudianteView.as_view()),
    path("estudiantes/<str:id>/notas/<str:codigo>/", NotaDetalleView.as_view()),
]
