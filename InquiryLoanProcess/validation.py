# #-------------------------------------------------------------------------------
# Inquiry_FIELD_DEFINITIONS = {
#     "Personal Information": {
#         "Date": {"type": "date", "required": False},
#         "First Name": {"type": "string", "required": False, "regex": r"^[A-Za-z\s]+$"},
#         "Middle Name": {"type": "string", "required": False},
#         "Last Name": {"type": "string", "required": False},
#         "Gender": {"type": "enum", "required": False, "choices": ["Male", "Female", "Other"]},
#         "Marital Status": {"type": "string", "required": False},
#         "Date of Birth": {"type": "date", "required": False, "min_age": 18},
#         "Phone Number": {"type": "string", "required": False, "regex": r"^\d{10}$"},
#         "Alternate Phone Number": {"type": "string", "required": False, "regex": r"^\d{10}$"},
#         "Email Address": {"type": "email", "required": False},
#         "Father's/Mother's Name": {"type": "string", "required": False}
#     },
#     "KYC Basics": {
#         "PAN Number": {"type": "string", "required": False, "regex": r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"},
#         "Aadhaar Number": {"type": "string", "required": False, "regex": r"^\d{12}$", "mask": False}
#     },
#     "Address Details": {
#         "Address Line 1": {"type": "string", "required": False},
#         "Address Line 2": {"type": "string", "required": False},
#         "City": {"type": "string", "required": False},
#         "State": {"type": "string", "required": False},
#         "Pincode": {"type": "string", "required": False, "regex": r"^\d{6}$"},
#         "Country": {"type": "string", "required": False, "default": "India"},
#         "Landmark": {"type": "string", "required": False},
#         "Address Type": {"type": "string", "required": False},
#         "Duration at Address": {"type": "int", "required": False}
#     },
#     "Inquiry Information": {
#         "Loan Purpose": {"type": "string", "required": False},
#         "Loan Amount Requested": {"type": "decimal", "required": False, "min": 1000},
#         "Source": {"type": "string", "required": False},
#         "Follow-up Notes": {"type": "string", "required": False},
#         "Inquiry Status": {"type": "enum", "required": False, "default": "Open", "choices": ["Open", "Converted", "Dropped"]}
#     }
# }

#-------------------------------------------------------------------------------

loan_application_FIELD_DEFINITIONS = {
    "Employment Details": {
        "Employment Type": {"type": "str", "required": False, "choices": ["Salaried", "Self-employed"]},
        "Occupation": {"type": "str", "required": False},
        "Company Name": {"type": "str", "required_if": {"Employment Type": "Salaried"}},
        "Industry Type": {"type": "str", "required": False},
        "Work Experience": {"type": "int", "required": False},
        "Employer Duration": {"type": "int", "required": False},
        "Office Address": {"type": "str", "required": False},
        "Office Phone Number": {"type": "str", "required": False},
        "Monthly Income": {"type": "float", "required": False, "min": 0},
        "Annual Income": {"type": "float", "auto_calculate": "12 * Monthly Income"}
    },
    "Banking Information": {
        "Bank Name": {"type": "str", "required": False},
        "Branch Name": {"type": "str", "required": False},
        "Account Number": {"type": "str", "required": False},
        "IFSC Code": {"type": "str", "required": False},
        "Account Type": {"type": "str", "required": False, "choices": ["Saving", "Current"]}
    },
    "Loan Details": {
        "Loan Tenure": {"type": "int", "required": False},
        "Repayment Mode": {"type": "str", "required": False, "choices": ["ECS", "Online", "Cash"]},
        "Co-Applicant": {"type": "bool", "required": False},
        "Guarantor Required": {"type": "bool", "required": False}
    },
    "Guarantor Details": {
        "Guarantor Name": {"type": "str", "required_if": {"Guarantor Required": False}},
        "Guarantor Mobile": {"type": "str", "required_if": {"Guarantor Required": False}},
        "Guarantor Email": {"type": "str", "required": False},
        "Guarantor Address": {"type": "str", "required_if": {"Guarantor Required": False}},
        "Guarantor PAN Number": {"type": "str", "required_if": {"Guarantor Required": False}},
        "Guarantor Aadhaar Number": {"type": "str", "required_if": {"Guarantor Required": False}},
        "Guarantor PAN Card Copy": {"type": "file", "required_if": {"Guarantor Required": False}},
        "Guarantor Aadhaar Card Copy": {"type": "file", "required_if": {"Guarantor Required": False}},
        "Guarantor Bank Statement": {"type": "file", "required_if": {"Guarantor Required": False}},
        "Existing Loans": {"type": "bool", "required": False},
        "EMI Amount (Existing)": {"type": "float", "required_if": {"Existing Loans": False}},
    }
}
