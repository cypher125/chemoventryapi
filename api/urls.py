from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabViewSet, CabinetViewSet, ShelfViewSet, ChemicalViewSet, UserViewSet, RegisterView, LoginView, LogoutView
from .views import GenerateReportView, ListReportView, DownloadReportView

router = DefaultRouter()
router.register(r'labs', LabViewSet)
router.register(r'cabinets', CabinetViewSet)
router.register(r'shelves', ShelfViewSet)
router.register(r'chemicals', ChemicalViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reports/generate/', GenerateReportView.as_view(), name='generate-report'),
    path('reports/', ListReportView.as_view(), name='list-reports'),
    path('reports/download/<int:pk>/', DownloadReportView.as_view(), name='download-report'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]                                                                                                                             