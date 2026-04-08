from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.views import HealthView

urlpatterns = [
    path("health/", HealthView.as_view()),
    # Swagger UI — documentación interactiva
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Endpoints
    path("", include("estudiantes.urls")),
    path("", include("notas.urls")),
]
