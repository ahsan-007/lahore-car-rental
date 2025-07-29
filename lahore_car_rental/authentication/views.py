from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer,
                         responses={
                             201: openapi.Response(
                                 description="User registered successfully",
                                 schema=openapi.Schema(
                                     type=openapi.TYPE_OBJECT,
                                     properties={
                                         "message": openapi.Schema(type=openapi.TYPE_STRING),
                                         "access": openapi.Schema(type=openapi.TYPE_STRING),
                                         "user": openapi.Schema(
                                             type=openapi.TYPE_OBJECT,
                                             properties={
                                                 "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                                 "username": openapi.Schema(type=openapi.TYPE_STRING),
                                                 "email": openapi.Schema(type=openapi.TYPE_STRING),
                                             }
                                         ),
                                     },
                                     example={
                                         "message": "User registered successfully",
                                         "access": "access_token_here",
                                         "user": {
                                             "id": 1,
                                             "username": "example_user",
                                             "email": "user@example.com"
                                         },
                                     }
                                 )
                             ),
                             500: "Internal Server Error",
                         })
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()

                # Generate JWT token
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "User registered successfully",
                    "access": str(refresh.access_token),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "error": "Internal Server Error",
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Login Successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                    },
                    example={
                        "access": "access_token_here",
                        "user": {
                            "id": 1,
                            "username": "example_user",
                            "email": "user@example.com"
                        }
                    }
                )
            ),
            400: "Invalid credentials"
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Get the user from the validated data
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.user

                # Remove refresh token and add user details to the response
                response.data.pop('refresh', None)
                response.data.update({
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    }
                })

        return response
