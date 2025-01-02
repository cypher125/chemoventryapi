from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from inventory.models import Lab, Cabinet, Shelf, Chemical
from account.models import User
from .serializers import LabSerializer, CabinetSerializer, ShelfSerializer, ChemicalSerializer, UserSerializer

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer, ReportSerializer
from report.utils import generate_report
from report.models import Report


# Custom permissions

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and request.user.is_superuser
        return request.user and request.user.is_authenticated



class IsSuperUserOrLabAttendant(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'DELETE']:  # Restrict POST and DELETE to superusers
            return request.user.is_superuser
        return request.user.role in ["superuser", "lab_attendant"]
# Inventory 

class LabViewSet(viewsets.ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrLabAttendant]

class CabinetViewSet(viewsets.ModelViewSet):
    queryset = Cabinet.objects.all()
    serializer_class = CabinetSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrLabAttendant]

class ShelfViewSet(viewsets.ModelViewSet):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserOrLabAttendant]

class ChemicalViewSet(viewsets.ModelViewSet):
    queryset = Chemical.objects.all()
    serializer_class = ChemicalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]  # Admin permission for create/update
        else:
            self.permission_classes = [permissions.IsAuthenticated]  # Default permission for other actions
        return super().get_permissions()
    
    def perform_create(self, serializer):
        # Automatically set the authenticated user as the creator
        serializer.save(created_by=self.request.user)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list','destroy']:
            self.permission_classes = [permissions.IsAdminUser]  # Admin permission for create/update
        return super().get_permissions()  # Apply the permission classes properly
    



# Account 

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Logout successful"}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Report

class GenerateReportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    
    def post(self, request):
        report_type = request.data.get('report_type')
        filters = request.data.get('filters', {})

        # Generate the report
        file_path = generate_report(report_type, filters)
        if file_path:
            report = Report.objects.create(title=f'{report_type.capitalize()} Report', report_type=report_type, created_by=request.User)
            serialzer = ReportSerializer(Report)
            return Response(serialzer.data, status=status.HTTP_201_CREATED)
        
        return Response({'error': 'Failed to generate report or no data available'}, status=status.HTTP_400_BAD_REQUEST)
    
class ListReportView(APIView):
    def get(self, request):
        reports = Report.objects.filter(created_by=request.user)
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)


class DownloadReportView(APIView):
    def get(self, request, pk):
        report = Report.objects.filter(id=pk, created_by=request.user).first()
        if not report:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # serve the file
        try:
            with open(report.file_path, 'rb') as report_file:
                response = Response(report_file.read(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = f'attachment; filename="{report.title}.xlsx"'
                return response
        except FileNotFoundError:
            return Response({'error': 'Report file not found'}, status=status.HTTP_404_NOT_FOUND)