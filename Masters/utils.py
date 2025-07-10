def get_invalid_fields(request_data, allowed_fields):
    incoming_fields = set(request_data.keys())
    invalid = list(incoming_fields - allowed_fields)
    return invalid


#--------------------------------- EMI Calculation logic----------------------------

import math

def calculate_fixed_emi(principal, annual_rate, tenure_months):
    """
    Fixed interest based on simple interest formula:
    EMI = (P + (P * I * T) / 100) / (T * 12)
    """
    time_years = tenure_months / 12
    total_amount = principal + (principal * annual_rate * time_years) / 100
    emi = total_amount / tenure_months
    return round(emi, 2)

def calculate_reducing_emi(principal, annual_rate, tenure_months):
    """
    Standard reducing balance EMI formula.
    EMI = [P * r * (1 + r)^N] / [(1 + r)^N - 1]
    """
    monthly_rate = (annual_rate / 100) / 12
    emi = (principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)) / \
          (math.pow(1 + monthly_rate, tenure_months) - 1)
    return round(emi, 2)

def calculate_custom_formula(principal, rate, time, formula):
    """
    Evaluate custom EMI formula.
    Variables allowed in formula: P (principal), R (rate), T (tenure in months)
    """
    try:
        allowed_names = {"P": principal, "R": rate, "T": time}
        emi = eval(formula, {"__builtins__": {}}, allowed_names)
        return round(emi, 2)
    except Exception as e:
        raise ValueError(f"Invalid formula: {str(e)}")


