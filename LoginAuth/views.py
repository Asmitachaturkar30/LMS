from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .utils import *
from rest_framework.views import APIView
from .models import *
from .serializers import *
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist

class RegisterView(APIView):
    def post(self, request):
        try:
            required_fields = ['email', 'username', 'password']
            missing_fields = [field for field in required_fields if field not in request.data]

            # Field existence check
            if missing_fields:
                return Response({
                    "result": "failure",
                    "error_message": f"Missing fields: {', '.join(missing_fields)}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Field validation and duplication check
            if User.objects.filter(email=request.data['email']).exists():
                return Response({
                    "result": "failure",
                    "error_message": "Email already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=request.data['username']).exists():
                return Response({
                    "result": "failure",
                    "error_message": "Username already exists."
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "result": "success",
                    "message": "User registered successfully."
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "result": "failure",
                    "error_message": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "result": "failure",
                "error_message": f"Server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#---------------------------------------------------------------------------

def jsonResponse(result, message, data=None, status_code=status.HTTP_200_OK):
    res = {'result': result, 'message': message}
    if data:
        res['data'] = data
    return Response(res, status=status_code)

#---------------------------------------------------------------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import LoginSerializer
User = get_user_model()

# class LoginView(APIView):
#     def post(self, request):
#         try:
#             serializer = LoginSerializer(data=request.data)

#             if not serializer.is_valid():
#                 if 'email' in serializer.errors and not request.data.get('email'):
#                     return jsonResponse(result=False, message="Email is required.", status_code=status.HTTP_400_BAD_REQUEST)
#                 if 'password' in serializer.errors and not request.data.get('password'):
#                     return jsonResponse(result=False, message="Password is required.", status_code=status.HTTP_400_BAD_REQUEST)
#                 if 'email' in serializer.errors:
#                     return jsonResponse(result=False, message="Invalid email or email not registered.", status_code=status.HTTP_401_UNAUTHORIZED)
#                 if 'password' in serializer.errors:
#                     return jsonResponse(result=False, message="Incorrect password.", status_code=status.HTTP_401_UNAUTHORIZED)

#                 return jsonResponse(result=False, message="Invalid credentials. Please try again.", status_code=status.HTTP_401_UNAUTHORIZED)

#             validated_data = serializer.validated_data
#             email = validated_data.get('email')
#             user = User.objects.get(email=email)

#             # Log the login event
#             send_login_success_email(email)
#             ip, _ = get_user_log_details(request)
#             loginLogs.objects.create(ipAddress=ip, email=email)

#             # Fetch roles assigned to the user
#             roles = Role.objects.filter(userrole__user=user)
#             role_data = roles.values('role_id', 'role_name', 'description', 'status')

#             # Fetch modules assigned to roles
#             modules = Modules.objects.filter(modulerole__role__in=roles).distinct()
#             module_data = modules.values('module_id', 'module_name', 'description')

#             # Fetch permissions assigned to roles
#             permissions = Permission.objects.filter(rolepermission__role__in=roles).select_related('module').distinct()
#             permission_data = [
#                 {
#                     "permission_id": p.permission_id,
#                     "permission_name": p.permission_name,
#                     "module": p.module.module_name,
#                     "action": p.action,
#                     "status": p.status
#                 } for p in permissions
#             ]

#             return jsonResponse(
#                 result=True,
#                 message=f"{email} login successful.",
#                 data={
#                     "user": {
#                         "id": validated_data.get("id"),
#                         "email": validated_data.get("email"),
#                         "username": validated_data.get("username"),
#                         "access": validated_data.get("access"),
#                         "refresh": validated_data.get("refresh")
#                     },
#                     "roles": list(role_data),
#                     "modules": list(module_data),
#                     "permissions": permission_data
#                 }
#             )

#         except Exception as e:
#             return Response({
#                 'result': 'failure',
#                 'error_message': f'Server error: {str(e)}'
#             }, status=500)


# --- Forgot Password Request (Step 1) ---

@api_view(['POST'])
def forgot_password_request(request):
    email = request.data.get('email')
    
    if not email:
        return jsonResponse(False, "Email is required.", status_code=400)

    # Check if the email exists in the database
    try:
        user = User.objects.get(email=email)  # Check if the email is registered
    except ObjectDoesNotExist:
        return jsonResponse(False, "Email not registered. Please check your email address.", status_code=400)

    otp = generate_otp()
    # Save OTP to the database or cache (this part depends on your approach)
    OTPRequest.objects.create(email=email, otp=otp)

    # Send the OTP email
    if not send_otp_email(email, otp):
        return jsonResponse(False, "Failed to send OTP email. Try again later.", status_code=500)

    return jsonResponse(True, "OTP sent to your email successfully.", data={'email': email})


@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return jsonResponse(result=False, message="Email and OTP are required.", status_code=400)

    # Validate Email Format
    try:
        validate_email(email)  # This will raise a ValidationError if the email is not valid
    except ValidationError:
        return jsonResponse(result=False, message="Invalid email format.", status_code=400)

    try:
        otp_requests = OTPRequest.objects.filter(email=email, is_verified=False)
        if otp_requests.count() == 0:
            return jsonResponse(result=False, message="No active OTP found. Please request a new OTP.", status_code=400)

        otp_request = otp_requests.order_by('-created_at').first()  # Get the most recent OTP

        # Check if OTP is expired
        if otp_request.is_expired():
            otp_request.delete()  # Optionally delete expired OTPs
            return jsonResponse(result=False, message="OTP has expired. Please request a new OTP.", status_code=400)

        # Check if OTP matches
        if otp_request.otp != otp:
            return jsonResponse(result=False, message="Invalid OTP.", status_code=400)

        # OTP is valid
        otp_request.is_verified = True  # Mark OTP as verified
        otp_request.save()

        return jsonResponse(result=True, message="OTP verified successfully.")
    
    except MultipleObjectsReturned:
        return jsonResponse(result=False, message="Multiple OTP records found. Please contact support.", status_code=500)
# --- Reset Password (Step 2) ---  

@api_view(['POST'])
def reset_password(request):
    try:
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not email or not new_password:
            return Response({'result': 'failure','error_message': 'Email and new password are required.'}, status=400)

        # Check OTP verification using model
        try:
            otp_entry = OTPRequest.objects.filter(email=email, is_verified=True).latest('created_at')
        except OTPRequest.DoesNotExist:
            return Response({'result': 'failure','error_message': 'Email not verified.'}, status=401)

        if otp_entry.is_expired():
            return Response({'result': 'failure','error_message': 'OTP has expired.'}, status=401)

        # Check password strength
        if not is_strong_password(new_password):
            return Response({
                'result': 'failure',
                'error_message': 'Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.'
            }, status=400)

        # Find user and update password
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'result': 'failure','error_message': 'User not found.'}, status=404)

        user.set_password(new_password)
        user.save()

        # Mark all verified OTPs as not verified (invalidate)
        OTPRequest.objects.filter(email=email, is_verified=True).update(is_verified=False)

        return Response({'result': 'success','message': 'Password reset successfully.'}, status=200)

    except Exception as e:
        return Response({'result': 'failure','error_message': f'Server error: {str(e)}'}, status=500)

# -----------------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def testing(request):
    user = request.user
    return Response(user.email,status=200)


#------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def createModule(request):
    try:
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            module = serializer.save(user=request.user)
            module.save()

            ip = get_client_ip(request)
            ModuleLogs.objects.create(user=request.user, ip_address=ip)

            return Response({
                'result': True,
                'message': 'Module created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        # Field-level validation error formatting
        fields = " and ".join(serializer.errors.keys())
        return Response({
            'result': False,
            'message': 'Validation failed.',
            'errors': f"{fields} field{' is' if len(serializer.errors) == 1 else 's are'} required or invalid."
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'result': False,
            'message': 'Internal server error.',
            'errors': {
                'message': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateModule(request, pk):
    try:
        # Step 1: Check if the module exists
        try:
            module = ModuleTable.objects.get(pk=pk)
        except ModuleTable.DoesNotExist:
            return Response({
                'result': False,
                'message': 'Module not found.',
                'errors': f'No module found with ID {pk}.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Step 2: Validate unexpected fields
        allowed_fields = set(ModuleSerializer().get_fields().keys())
        invalid_fields = set(request.data.keys()) - allowed_fields
        if invalid_fields:
            return Response({
                'result': False,
                'message': 'Validation failed.',
                'errors': f"Unexpected field(s): {', '.join(invalid_fields)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Validate and update module
        serializer = ModuleSerializer(instance=module, data=request.data, partial=True)
        if serializer.is_valid():
            updated_module = serializer.save()

            ip = get_client_ip(request)
            ModuleLogs.objects.create(user=request.user, ip_address=ip)

            return Response({
                'result': True,
                'message': 'Module updated successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        # Step 4: Field-level validation errors
        fields = " and ".join(serializer.errors.keys())
        return Response({
            'result': False,
            'message': 'Validation failed.',
            'errors': f"{fields} field{' is' if len(serializer.errors) == 1 else 's are'} required or invalid."
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Step 5: Catch-all for unexpected errors
        return Response({
            'result': False,
            'message': 'Internal server error.',
            'errors': {
                'message': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from threading import Thread
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class Login(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            
            if not serializer.is_valid():
                if 'email' in serializer.errors and not request.data.get('email'):
                    return jsonResponse(result=False, message="Email is required.", status_code=status.HTTP_400_BAD_REQUEST)
                if 'password' in serializer.errors and not request.data.get('password'):
                    return jsonResponse(result=False, message="Password is required.", status_code=status.HTTP_400_BAD_REQUEST)
                if 'email' in serializer.errors:
                    return jsonResponse(result=False, message="Invalid email or email not registered.", status_code=status.HTTP_401_UNAUTHORIZED)
                if 'password' in serializer.errors:
                    return jsonResponse(result=False, message="Incorrect password.", status_code=status.HTTP_401_UNAUTHORIZED)

                return jsonResponse(result=False, message="Invalid credentials. Please try again.", status_code=status.HTTP_401_UNAUTHORIZED)

            validated_data = serializer.validated_data
            email = validated_data.get('email')
            user = User.objects.get(email=email)

            # Start background tasks
            self._start_background_tasks(email, request)
            
            # Get user data including tokens from validated_data
            user_data = self._get_user_data(user, validated_data)
            
            return jsonResponse(
                result=True,
                message=f"{email} login successful.",
                data=user_data
            )

        except Exception as e:
            return Response({
                'result': 'failure',
                'error_message': f'Server error: {str(e)}'
            }, status=500)

    def _start_background_tasks(self, email, request):
        """Start all non-critical path operations in threads"""
        # Email thread
        Thread(target=send_login_success_email, args=(email,)).start()
        
        # IP logging thread (if this is slow)
        Thread(
            target=self._log_login_activity,
            args=(email, request)
        ).start()

    def _log_login_activity(self, email, request):
        """Thread-safe login logging"""
        try:
            ip, _ = get_user_log_details(request)
            loginLogs.objects.create(ipAddress=ip, email=email)
        except:
            pass  # Log but don't fail login

    def _get_user_data(self, user, validated_data):
        """Optimized single query for all role/module/permission data"""
        with transaction.atomic():
            # Removed invalid select_related('department')
            roles = Role.objects.filter(
                userrole__user=user
            ).only(
                'role_id', 'role_name', 'description', 'status'
            )
            
            # Get all related data in one query
            permissions = Permission.objects.filter(
                rolepermission__role__in=roles
            ).select_related('module').only(
                'permission_id', 'permission_name', 'action', 'status',
                'module__module_id', 'module__module_name', 'module__description'
            )
            
            # Build response data structure
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "access": validated_data.get("access"),
                    "refresh": validated_data.get("refresh")
                },
                "roles": [
                    {
                        "role_id": r.role_id,
                        "role_name": r.role_name,
                        "description": r.description,
                        "status": r.status
                    } for r in roles
                ],
                "modules": list({
                    'module_id': p.module.module_id,
                    'module_name': p.module.module_name,
                    'description': p.module.description
                } for p in permissions),
                "permissions": [
                    {
                        "permission_id": p.permission_id,
                        "permission_name": p.permission_name,
                        "module": p.module.module_name,
                        "action": p.action,
                        "status": p.status
                    } for p in permissions
                ]
            }