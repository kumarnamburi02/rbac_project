from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from .models import Profile
from .permissions import IsAdmin, IsModerator, IsUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer

# Home view
def home(request):
    context = {
        'message': 'Welcome to the Homepage! This is a Role-Based Access Control (RBAC) system.',
    }
    return render(request, 'home.html', context)

# Registration View
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Logout View
class LogoutView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Admin-only View - Full CRUD access
class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        profiles = Profile.objects.all()
        return Response({'profiles': [profile.bio for profile in profiles]})

    def post(self, request):
        # Admin can create new profiles
        pass

    def put(self, request):
        # Admin can update profiles
        pass

    def delete(self, request):
        # Admin can delete profiles
        pass

# Moderator-only View - Can approve/reject profiles
class ModeratorProfileView(APIView):
    permission_classes = [IsAuthenticated, IsModerator]

    def get(self, request):
        profiles = Profile.objects.all()
        return Response({'profiles': [profile.bio for profile in profiles]})

    def patch(self, request, profile_id):
        # Moderator can approve/reject a profile
        profile = get_object_or_404(Profile, id=profile_id)
        profile.is_approved = True  # Or False, depending on the action
        profile.save()
        return Response({'message': 'Profile updated successfully'})

# User-only View - Can only view their own profile
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsUser]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        return Response({'profile': profile.bio})

