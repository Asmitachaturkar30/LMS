# views.py
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import *
from django.utils import timezone

SUREPASS_CUSTOMER_ID = "your_customer_id_here" 
SUREPASS_CIBIL_PDF_URL = "https://sandbox.surepass.io/api/v1/credit-report-cibil/fetch-report-pdf"
SUREPASS_ELECTRICITY_URL = "https://sandbox.surepass.io/api/v1/utility/electricity/"
SUREPASS_BANK_URL = "https://sandbox.surepass.io/api/v1/bank-verification/"
SUREPASS_DL_URL = "https://sandbox.surepass.io/api/v1/driving-license/driving-license"
SUREPASS_PAN_URL = "https://sandbox.surepass.io/api/v1/pan/pan"
SANDBOX_aadhaar_number_URL = "https://sandbox.surepass.io/api/v1/aadhaar-v2/generate-otp"
SUREPASS_VOTER_URL = "https://sandbox.surepass.io/api/v1/voter-id/voter-id"

SUREPASS_SANDBOX_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MTUyMzI4NSwianRpIjoiZTE1NGIxYTgtYTQ4ZS00NmI0LWIxNGYtYTZkM2Y5ZGZlOGJmIiwidHlwZSI6ImFjY2VzcyIsImlkZW50aXR5IjoiZGV2LmlteXVnMDMwOEBzdXJlcGFzcy5pbyIsIm5iZiI6MTc1MTUyMzI4NSwiZXhwIjoxNzU0MTE1Mjg1LCJlbWFpbCI6ImlteXVnMDMwOEBzdXJlcGFzcy5pbyIsInRlbmFudF9pZCI6Im1haW4iLCJ1c2VyX2NsYWltcyI6eyJzY29wZXMiOlsidXNlciJdfX0.OgJKUnWn0KGsDOkJi0-HaYsdMSGOnMh1rXSfOJKBeyE"

SUREPASS_BANK_URL = "https://sandbox.surepass.io/api/v1/bank-verification/"
SUREPASS_CIBIL_URL = "https://sandbox.surepass.io/api/v1/credit-report-cibil/fetch-report"


@api_view(['POST'])
def verify_aadhaar(request):
    aadhaar_number = request.data.get('aadhaar_number')
    if not aadhaar_number or len(aadhaar_number) != 12:
        return JsonResponse({"error": "Invalid Aadhaar number"}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "id_number": aadhaar_number
    }

    try:
        response = requests.post(SANDBOX_aadhaar_number_URL, json=payload, headers=headers)
        print(response)
        resp_json = response.json()

        # Get or create the log entry
        log_entry, created = AadhaarVerificationLog.objects.get_or_create(
            aadhaar_number=aadhaar_number,
            defaults={
                "request_count": 1,
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )
        if not created:
            log_entry.request_count += 1
            log_entry.request_time = timezone.now()
            log_entry.response_status = response.status_code
            log_entry.response_message = resp_json.get("message", "")
            log_entry.success = resp_json.get("success", False)
            log_entry.save()

        return JsonResponse(resp_json, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



#----------------------------------------- 

@api_view(['POST'])
def verify_pan(request):
    pan_number = request.data.get("id_number")
    if not pan_number or len(pan_number) != 10:
        return JsonResponse({"error": "Invalid PAN number"}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "id_number": pan_number
    }

    try:
        response = requests.post(SUREPASS_PAN_URL, json=payload, headers=headers)
        
        try:
            resp_json = response.json()
        except ValueError:
            return JsonResponse({
                "error": "Surepass response not in JSON format",
                "status_code": response.status_code,
                "raw": response.text
            }, status=500)

        log_entry, created = PANVerificationLog.objects.get_or_create(
            pan_number=pan_number,
            defaults={
                "request_count": 1,
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )
        if not created:
            log_entry.request_count += 1
            log_entry.last_request_time = timezone.now()
            log_entry.response_status = response.status_code
            log_entry.response_message = resp_json.get("message", "")
            log_entry.success = resp_json.get("success", False)
            log_entry.save()

        return JsonResponse(resp_json, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#-----------------------------------------------


@api_view(['POST'])
def verifyDrivingLicense(request):
    license_number = request.data.get("id_number")
    dob = request.data.get("dob")  # Expected in 'YYYY-MM-DD' format

    if not license_number or not dob:
        return JsonResponse({"error": "Both license number and DOB are required."}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "id_number": license_number,
        "dob": dob
    }

    try:
        response = requests.post(SUREPASS_DL_URL, json=payload, headers=headers)

        try:
            resp_json = response.json()
        except ValueError:
            return JsonResponse({
                "error": "Surepass response not in JSON format",
                "status_code": response.status_code,
                "raw": response.text
            }, status=500)

        # Log to DB
        log_entry, created = DrivingLicenseVerificationLog.objects.get_or_create(
            license_number=license_number,
            dob=dob,
            defaults={
                "request_count": 1,
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )
        if not created:
            log_entry.request_count += 1
            log_entry.last_request_time = timezone.now()
            log_entry.response_status = response.status_code
            log_entry.response_message = resp_json.get("message", "")
            log_entry.success = resp_json.get("success", False)
            log_entry.save()

        return JsonResponse(resp_json, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#----------------------------------------- 

@api_view(['POST'])
def verify_voter_id(request):
    voter_id_number = request.data.get("id_number")

    if not voter_id_number:
        return JsonResponse({"error": "Voter ID number is required."}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "X-Customer-Id": SUREPASS_CUSTOMER_ID,
        "Content-Type": "application/json",
    }
    payload = {
        "id_number": voter_id_number
    }

    try:
        response = requests.post(SUREPASS_VOTER_URL, json=payload, headers=headers)

        try:
            resp_json = response.json()
        except ValueError:
            return JsonResponse({
                "error": "Surepass response not in JSON format",
                "status_code": response.status_code,
                "raw": response.text
            }, status=500)

        # Log to DB
        log_entry, created = VoterIDVerificationLog.objects.get_or_create(
            voter_id_number=voter_id_number,
            defaults={
                "request_count": 1,
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )
        if not created:
            log_entry.request_count += 1
            log_entry.last_request_time = timezone.now()
            log_entry.response_status = response.status_code
            log_entry.response_message = resp_json.get("message", "")
            log_entry.success = resp_json.get("success", False)
            log_entry.save()

        return JsonResponse(resp_json, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

#----------------------------------------- 
@api_view(['POST'])
def verify_bank(request):
    id_number = request.data.get("id_number")
    ifsc = request.data.get("ifsc")
    ifsc_details = request.data.get("ifsc_details", True)

    if not id_number or not ifsc:
        return JsonResponse({"error": "Both 'id_number' and 'ifsc' are required."}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "id_number": id_number,
        "ifsc": ifsc,
        "ifsc_details": ifsc_details,
    }

    try:
        response = requests.post(SUREPASS_BANK_URL, json=payload, headers=headers)

        try:
            resp_json = response.json()
        except ValueError:
            return JsonResponse({
                "error": "Surepass response not in JSON format",
                "status_code": response.status_code,
                "raw": response.text
            }, status=500)

        # Log the response in the DB
        log_entry, created = BankVerificationLog.objects.get_or_create(
            id_number=id_number,
            ifsc=ifsc,
            defaults={
                "ifsc_details": ifsc_details,
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )
        if not created:
            log_entry.request_count += 1
            log_entry.last_request_time = timezone.now()
            log_entry.ifsc_details = ifsc_details
            log_entry.response_status = response.status_code
            log_entry.response_message = resp_json.get("message", "")
            log_entry.success = resp_json.get("success", False)
            log_entry.save()

        return JsonResponse(resp_json, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# {
#   "id_number": "12121245457878",
#   "ifsc": "CNRB0000000",
#   "ifsc_details": true
# }

#----------------------------------------- 

@api_view(['POST'])
def verify_electricity_bill(request):
    id_number = request.data.get("id_number")
    operator_code = request.data.get("operator_code")

    if not id_number or not operator_code:
        return JsonResponse({"error": "Both 'id_number' and 'operator_code' are required."}, status=400)

    operator_code = operator_code.upper()  # Normalize to uppercase

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "id_number": id_number,
        "operator_code": operator_code,
    }

    try:
        response = requests.post(SUREPASS_ELECTRICITY_URL, json=payload, headers=headers)

        try:
            resp_json = response.json()
        except ValueError:
            return JsonResponse({
                "error": "Surepass response not in JSON format",
                "status_code": response.status_code,
                "raw": response.text
            }, status=500)

        # Log the response in the database
        log_entry, created = ElectricityBillVerificationLog.objects.get_or_create(
            id_number=id_number,
            operator_code=operator_code,
            defaults={
                "request_count": 1,
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )
        if not created:
            log_entry.request_count += 1
            log_entry.last_request_time = timezone.now()
            log_entry.response_status = response.status_code
            log_entry.response_message = resp_json.get("message", "")
            log_entry.success = resp_json.get("success", False)
            log_entry.save()

        return JsonResponse(resp_json, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




@api_view(['POST'])
def verify_itr_v(request):
    client_id = request.data.get('client_id')
    if not client_id:
        return JsonResponse({"error": "Client ID is required"}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",  # put token in settings
        "Content-Type": "application/json",
    }
    payload = {
        "client_id": client_id
    }

    try:
        response = requests.post("https://sandbox.surepass.io/api/v1/itr/download-itr-v", json=payload, headers=headers)
        resp_json = response.json()

        prev_log = ITRVerificationLog.objects.filter(client_id=client_id).first()
        request_count = prev_log.request_count + 1 if prev_log else 1

        ITRVerificationLog.objects.update_or_create(
            client_id=client_id,
            defaults={
                "request_count": request_count,
                "request_time": timezone.now(),
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )

        return JsonResponse({
            "status": "success" if resp_json.get("success") else "failed",
            "message": resp_json.get("message"),
            "data": resp_json.get("data", {}),
        }, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": "Internal server error", "details": str(e)}, status=500)



@api_view(['POST'])
def verify_itr_compliance(request):
    pan_number = request.data.get('pan_number')
    if not pan_number or len(pan_number) != 10:
        return JsonResponse({"error": "Invalid PAN number"}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "pan_number": pan_number
    }

    try:
        response = requests.post("https://sandbox.surepass.io/api/v1/itr/itr-compliance-check", json=payload, headers=headers)
        resp_json = response.json()

        prev_log = ITRComplianceLog.objects.filter(pan_number=pan_number).first()
        request_count = prev_log.request_count + 1 if prev_log else 1

        ITRComplianceLog.objects.update_or_create(
            pan_number=pan_number,
            defaults={
                "request_count": request_count,
                "request_time": timezone.now(),
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )

        return JsonResponse({
            "status": "success" if resp_json.get("success") else "failed",
            "message": resp_json.get("message"),
            "data": resp_json.get("data", {}),
        }, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": "Internal server error", "details": str(e)}, status=500)


@api_view(['POST'])
def credit_report_cibil(request):
    mobile = request.data.get("mobile")
    pan = request.data.get("pan")
    name = request.data.get("name")
    gender = request.data.get("gender")
    consent = request.data.get("consent", "Y")

    if not all([mobile, pan, name, gender]):
        return JsonResponse({"error": "Missing required fields: mobile, pan, name, gender."}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "mobile": mobile,
        "pan": pan,
        "name": name,
        "gender": gender,
        "consent": consent,
    }

    try:
        response = requests.post(SUREPASS_CIBIL_URL, json=payload, headers=headers)

        try:
            resp_json = response.json()
        except ValueError:
            return JsonResponse({
                "error": "Surepass response not in JSON format",
                "status_code": response.status_code,
                "raw": response.text
            }, status=500)

        log_entry, created = CreditReportCIBILLog.objects.get_or_create(
            mobile=mobile,
            defaults={
                "request_count": 1,
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )
        if not created:
            log_entry.request_count += 1
            log_entry.last_request_time = timezone.now()
            log_entry.response_status = response.status_code
            log_entry.response_message = resp_json.get("message", "")
            log_entry.success = resp_json.get("success", False)
            log_entry.save()

        return JsonResponse(resp_json, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




@api_view(['POST'])
def fetch_credit_report_cibil_pdf(request):
    mobile = request.data.get("mobile")
    pan = request.data.get("pan")
    name = request.data.get("name")
    gender = request.data.get("gender")
    consent = request.data.get("consent", "Y")

    if not all([mobile, pan, name, gender]):
        return JsonResponse({"error": "Missing required fields: mobile, pan, name, gender."}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "mobile": mobile,
        "pan": pan,
        "name": name,
        "gender": gender,
        "consent": consent,
    }

    try:
        response = requests.post(SUREPASS_CIBIL_PDF_URL, json=payload, headers=headers)

        try:
            resp_json = response.json()
        except ValueError:
            return JsonResponse({
                "error": "Surepass response not in JSON format",
                "status_code": response.status_code,
                "raw": response.text
            }, status=500)

        # Logging the request
        log_entry, created = CreditReportCIBILPDFLog.objects.get_or_create(
            mobile=mobile,
            defaults={
                "request_count": 1,
                "response_status": response.status_code,
                "response_message": resp_json.get("message", ""),
                "success": resp_json.get("success", False),
            }
        )
        if not created:
            log_entry.request_count += 1
            log_entry.last_request_time = timezone.now()
            log_entry.response_status = response.status_code
            log_entry.response_message = resp_json.get("message", "")
            log_entry.success = resp_json.get("success", False)
            log_entry.save()

        return JsonResponse(resp_json, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.utils import timezone
from .models import DigiLockerLog  # Optional if you're logging

SUREPASS_DIGILOCKER_URL = "https://sandbox.surepass.io/api/v1/digilocker/initialize"


@api_view(['POST'])
def initialize_digilocker(request):
    data = request.data.get("data")

    if not data:
        return JsonResponse({"error": "Missing 'data' field in request body"}, status=400)

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(SUREPASS_DIGILOCKER_URL, json={"data": data}, headers=headers)
        resp_json = response.json()

        # Optional Logging
        DigiLockerLog.objects.create(
            full_name=data.get("prefill_options", {}).get("full_name", ""),
            mobile_number=data.get("prefill_options", {}).get("mobile_number", ""),
            user_email=data.get("prefill_options", {}).get("user_email", ""),
            request_time=timezone.now(),
            response_status=response.status_code,
            response_message=resp_json.get("message", str(resp_json)),
            success=resp_json.get("success", False)
        )

        return JsonResponse(resp_json, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



# kyc_services/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import KYCLog, Customer, LoanApplication, NewInquiry
import requests


def get_customer_obj(customer_id=None, loan_id=None, inquiry_id=None):
    customer = loan = inquiry = None
    if customer_id:
        customer = Customer.objects.filter(pk=customer_id).first()
    elif loan_id:
        loan = LoanApplication.objects.filter(pk=loan_id).first()
        if loan:
            customer = Customer.objects.filter(LoanId=loan).first()
    elif inquiry_id:
        inquiry = NewInquiry.objects.filter(pk=inquiry_id).first()
        if inquiry:
            customer = Customer.objects.filter(InquiryId=inquiry).first()
    return customer, loan, inquiry


@api_view(["POST"])
def digilocker_initialize(request):
    data = request.data
    customer_id = data.get("customer_id")
    loan_id = data.get("loan_id")
    inquiry_id = data.get("inquiry_id")

    payload = {
        "data": data.get("data")
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}"
    }

    url = "https://sandbox.surepass.io/api/v1/digilocker/initialize"

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        customer, loan, inquiry = get_customer_obj(customer_id, loan_id, inquiry_id)

        KYCLog.objects.create(
            log_type="digilocker_initialize",
            customer=customer,
            loan=loan,
            inquiry=inquiry,
            kyc_service="digilocker_initialize",
            endpoint=url,
            token=SUREPASS_SANDBOX_TOKEN,
            payload=payload,
            response=response.json()
        )

        return Response(response.json())

    except requests.exceptions.RequestException as e:
        return Response({
            "success": False,
            "message": "Surepass API connection failed",
            "error": str(e)
        }, status=500)

from rest_framework import status
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def digilocker_list_documents(request, client_id):

    headers = {
        "Authorization": f"Bearer {SUREPASS_SANDBOX_TOKEN}"
    }

    url = f"https://sandbox.surepass.io/api/v1/digilocker/list-documents/{client_id}"

    try:
        response = requests.get(url, headers=headers)
        return Response({
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "surepass_response": response.json()
        }, status=response.status_code)

    except requests.exceptions.RequestException as e:
        return Response({
            "success": False,
            "message": "Failed to fetch document list",
            "error": str(e)
        }, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def digilocker_download_document(request, client_id, file_id):
    token = SUREPASS_SANDBOX_TOKEN

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"https://sandbox.surepass.io/api/v1/digilocker/download-document/{client_id}/{file_id}"

    try:
        response = requests.get(url, headers=headers)
        return Response({
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "surepass_response": response.json()
        }, status=response.status_code)

    except requests.exceptions.RequestException as e:
        return Response({
            "success": False,
            "message": "Failed to fetch document",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
