from django.http import JsonResponse
from rest_framework import status
from django.core.exceptions import ValidationError
from datetime import datetime
#============================= Response helper functions ===============================
# validators.py
from django.core.validators import RegexValidator, ValidationError
def validation_error_response(errors):
    error_messages = []
    for field, field_errors in errors.items():
        error_messages.append(f"{field}: {', '.join(field_errors)}")
    
    return JsonResponse({
        "result": False,
        "message": "Validation failed",
        "errors": ". ".join(error_messages)
    }, status=status.HTTP_400_BAD_REQUEST)

def not_found_response(message):
    return JsonResponse({
        "result": False,
        "message": message
    }, status=status.HTTP_404_NOT_FOUND)

def server_error_response(error):
    return JsonResponse({
        "result": False,
        "message": "Internal server error",
        "error": str(error)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def success_response(data=None, message="Success"):
    response = {
        "result": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return JsonResponse(response, status=status.HTTP_200_OK)

def created_response(data, message="Resource created successfully"):
    return JsonResponse({
        "result": True,
        "message": message,
        "data": data
    }, status=status.HTTP_201_CREATED)

def no_content_response(message="Resource deleted successfully"):
    return JsonResponse({
        "result": True,
        "message": message
    }, status=status.HTTP_204_NO_CONTENT)


def multi_status_response(data, errors, message):
    return JsonResponse({
        "result": bool(data) and not bool(errors),
        "message": message,
        "data": data,
        "errors": errors
    }, status=status.HTTP_207_MULTI_STATUS)




def validate_real_estate_fields(data):
    required_fields = ['Latitude', 'Longitude', 'BuildingType', 'AreaSqft']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for real estate collateral."] for field in missing_fields})
    
    # try:
    #     latitude = float(data['Latitude'])
    #     if not (-90 <= latitude <= 90):
    #         raise ValueError
    # except ValueError:
    #     return validation_error_response({
    #         'Latitude': ["Must be a valid latitude between -90 and 90."]
    #     })
    
    # try:
    #     longitude = float(data['Longitude'])
    #     if not (-180 <= longitude <= 180):
    #         raise ValueError
    # except ValueError:
    #     return validation_error_response({
    #         'Longitude': ["Must be a valid longitude between -180 and 180."]
    #     })
    
    # try:
    #     area_sqft = float(data['AreaSqft'])
    #     if area_sqft <= 0:
    #         raise ValueError
    # except ValueError:
    #     return validation_error_response({
    #         'AreaSqft': ["Must be a positive number."]
    #     })
    
    return None

def validate_vehicle_fields(data):
    required_fields = ['VehicleRC_Number', 'EngineNumber', 'ChassisNumber']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for vehicle collateral."] for field in missing_fields})
    
    # try:
    #     RegexValidator(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$')(data['VehicleRC_Number'])
    # except ValidationError:
    #     return validation_error_response({
    #         'VehicleRC_Number': ["Invalid RC number format."]
    #     })
    
    return None

def validate_financial_fields(data):
    required_fields = ['InstrumentType', 'Instrument_ISIN', 'InstitutionName', 'MaturityDate']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for financial collateral."] for field in missing_fields})
    
    # try:
    #     maturity_date = datetime.strptime(data['MaturityDate'], '%Y-%m-%d').date()
    #     if maturity_date < datetime.now().date():
    #         return validation_error_response({
    #             'MaturityDate': ["Maturity date cannot be in the past."]
    #         })
    # except ValueError:
    #     return validation_error_response({
    #         'MaturityDate': ["Invalid date format. Use YYYY-MM-DD."]
    #     })
    
    # try:
    #     haircut = float(data.get('HaircutPercentage', 0))
    #     if not (0 <= haircut <= 100):
    #         raise ValueError
    # except ValueError:
    #     return validation_error_response({
    #         'HaircutPercentage': ["Must be a decimal number between 0 and 100."]
    #     })
    
    return None

def validate_inventory_fields(data):
    required_fields = ['Description', 'Quantity', 'StorageLocation']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for inventory collateral."] for field in missing_fields})
    
    # try:
    #     quantity = int(data['Quantity'])
    #     if quantity <= 0:
    #         raise ValueError
    # except ValueError:
    #     return validation_error_response({
    #         'Quantity': ["Must be a positive integer."]
    #     })
    
    return None

def validate_machinery_fields(data):
    required_fields = ['MachineType', 'Manufacturer', 'PurchaseYear']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return validation_error_response({field: ["This field is required for machinery collateral."] for field in missing_fields})
    
    # try:
    #     purchase_year = int(data['PurchaseYear'])
    #     current_year = datetime.now().year
    #     if not (1900 <= purchase_year <= current_year):
    #         raise ValueError
    # except ValueError:
    #     return validation_error_response({
    #         'PurchaseYear': [f"Must be a valid year between 1900 and {current_year}."]
    #     })
    
    return None

def validate_others_fields(data):
    if 'Description' not in data:
        return validation_error_response({
            'Description': ["This field is required for other collateral types."]
        })
    return None
