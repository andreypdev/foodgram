from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, NewUserViewSet, RecipeViewSet, TagViewSet

app_name = 'api'

router = DefaultRouter()


router.register('users', NewUserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
