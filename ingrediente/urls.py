from rest_framework import routers
from .views import IngredienteViewSet

router = routers.DefaultRouter()
router.register(r'ingredientes', IngredienteViewSet)

urlpatterns = router.urls