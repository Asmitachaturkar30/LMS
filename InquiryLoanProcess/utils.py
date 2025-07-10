# # # utils/base64_file.py
# import base64
# from uuid import uuid4
# from django.core.files.base import ContentFile
# from rest_framework import serializers


# def base64_to_file(base64_string, field_name):
#     if not base64_string:
#         return None
    
#     # Check if it's a data URL (starts with 'data:')
#     if isinstance(base64_string, str) and base64_string.startswith('data:'):
#         # Extract the base64 part from the data URL
#         base64_string = base64_string.split(',')[1]
    
#     try:
#         # Decode the base64 string
#         decoded_file = base64.b64decode(base64_string)
        
#         # Generate a unique filename
#         file_extension = 'png'  # default to png, adjust as needed
#         if field_name.endswith('_card'):
#             file_extension = 'png'
#         elif field_name == 'bank_statement':
#             file_extension = 'pdf'
#         elif field_name == 'salary_slips':
#             file_extension = 'pdf'
            
#         filename = f"{field_name}_{uuid4().hex[:8]}.{file_extension}"
        
#         # Return a ContentFile that Django can save
#         return ContentFile(decoded_file, name=filename)
#     except Exception as e:
#         raise ValueError(f"Invalid base64 string for {field_name}: {str(e)}")




# # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"




# from .validation import *


# def validate_Inquiry_structure(Inquiry_data):
#     errors = []

#     # Top-level keys must match
#     for section in Inquiry_FIELD_DEFINITIONS:
#         if section not in Inquiry_data:
#             errors.append(f"Missing section: {section}")
#         else:
#             extra_keys = set(Inquiry_data[section].keys()) - set(Inquiry_FIELD_DEFINITIONS[section].keys())
#             if extra_keys:
#                 errors.append(f"Invalid keys in '{section}': {', '.join(extra_keys)}")
    
#     # Detect extra sections not expected
#     unexpected_sections = set(Inquiry_data.keys()) - set(Inquiry_FIELD_DEFINITIONS.keys())
#     if unexpected_sections:
#         errors.append(f"Unexpected section(s): {', '.join(unexpected_sections)}")

#     return errors
