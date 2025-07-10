def calculate_emi_schedule(principal, annual_rate, tenure_months, method):
    from decimal import Decimal, ROUND_HALF_UP
    from simpleeval import simple_eval

    principal = float(principal)
    annual_rate = float(annual_rate)
    tenure_months = int(tenure_months)
    monthly_rate = (annual_rate / 12) / 100
    schedule = []
    emi = 0

    if method == 'reducing':
        emi = principal * monthly_rate * (1 + monthly_rate) * tenure_months / ((1 + monthly_rate) * tenure_months - 1)
        emi = round(emi, 2)
        balance = principal
        for i in range(1, tenure_months + 1):
            interest = round(balance * monthly_rate, 2)
            principal_payment = round(emi - interest, 2)
            balance = round(balance - principal_payment, 2)
            schedule.append({
                "month": i,
                "emi": emi,
                "interest": interest,
                "principal": principal_payment,
                "remaining_balance": max(balance, 0)
            })

    elif method == 'flat':
        total_interest = principal * (annual_rate / 100) * (tenure_months / 12)
        total_emi = principal + total_interest
        monthly_interest = round(total_interest / tenure_months, 2)
        monthly_principal = round(principal / tenure_months, 2)
        balance = principal
        for i in range(1, tenure_months + 1):
            if i == tenure_months:
                principal_payment = round(balance, 2)
                emi = round(principal_payment + monthly_interest, 2)
                balance = 0
            else:
                principal_payment = monthly_principal
                emi = round(principal_payment + monthly_interest, 2)
                balance = round(balance - principal_payment, 2)

            schedule.append({
                "month": i,
                "emi": emi,
                "interest": monthly_interest,
                "principal": principal_payment,
                "remaining_balance": max(balance, 0)
            })

    elif method == 'interest_only':
        interest = round(principal * monthly_rate, 2)
        for i in range(1, tenure_months + 1):
            schedule.append({
                "month": i,
                "emi": interest,
                "interest": interest,
                "principal": 0,
                "remaining_balance": principal
            })
        schedule.append({
            "month": tenure_months + 1,
            "emi": principal,
            "interest": 0,
            "principal": principal,
            "remaining_balance": 0
        })
        emi = interest

    elif method == 'ipp':
        emi = round(principal / tenure_months, 2)
        balance = principal
        for i in range(1, tenure_months + 1):
            if i == tenure_months:
                principal_payment = round(balance, 2)
                emi_actual = principal_payment
                balance = 0
            else:
                principal_payment = emi
                emi_actual = emi
                balance = round(balance - principal_payment, 2)

            schedule.append({
                "month": i,
                "emi": emi_actual,
                "interest": 0,
                "principal": principal_payment,
                "remaining_balance": max(balance, 0)
            })

    elif method == 'custom':
        formula_text = "principal * monthly_rate * (1 + monthly_rate) * tenure_months / ((1 + monthly_rate) * tenure_months - 1)"
        allowed_names = {
            "principal": principal,
            "annual_rate": annual_rate,
            "tenure_months": tenure_months,
            "monthly_rate": monthly_rate,
        }
        total_interest = round(simple_eval(formula_text, names=allowed_names), 2)
        total_amount = principal + total_interest
        emi = round(total_amount / tenure_months, 2)

        monthly_interest = round(total_interest / tenure_months, 2)
        monthly_principal = round(principal / tenure_months, 2)
        balance = principal
        for i in range(1, tenure_months + 1):
            if i == tenure_months:
                principal_payment = round(balance, 2)
                emi = round(principal_payment + monthly_interest, 2)
                balance = 0
            else:
                principal_payment = monthly_principal
                balance = round(balance - principal_payment, 2)

            schedule.append({
                "month": i,
                "emi": emi,
                "interest": monthly_interest,
                "principal": principal_payment,
                "remaining_balance": max(balance, 0)
            })

    return round(emi, 2), schedule
