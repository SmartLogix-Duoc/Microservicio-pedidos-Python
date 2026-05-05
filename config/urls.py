from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from pedidos.controllers.api_v1 import OrderController

# 1. Creamos el Router mágico de Django
router = DefaultRouter()

# 2. Registramos tu controlador en la ruta base que querías.
# El router creará automáticamente:
# - GET /api/v1/orders/
# - POST /api/v1/orders/
# - GET /api/v1/orders/{id}/
# - PUT /api/v1/orders/{id}/
# - DELETE /api/v1/orders/{id}/
router.register(r'api/v1/orders', OrderController, basename='orders')

urlpatterns = [
    path('admin/', admin.site.urls),

    # 3. Inyectamos todas las rutas que el router generó por nosotros
    path('', include(router.urls)),

    # 4. Rutas para generar la documentación Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]   