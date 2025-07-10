# views.py
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail

import json
access_token = 'EAADyZCz8hYlABO9ixv0uhxJuZBdbjTzcZCHSR7Hq7XnvKPbtPGsSUAUfdTOjXfDZC1VS1on5cHPRhOCfp4qFZAvw6U9WPQXo3LZCK6mGF6g6Vto4BTvWA9owb8ejRVZBfrO47ddMDHV65L1ZCOFZCb1ISkRZBwwxztSiv9lFrW5RFbbNu7zYaVJXiorlESXDpEXVxkUEA7q2UJ9uEbZCmIgdA9YhmGDNieuzFGi3wZCxw9JothI4OpMUt29kdSZCnGt1aFAZDZD'
PHONE_NUMBER_ID = '235809312951861'

@api_view(['POST'])
def send_whatsapp_message(request):
    try:
        phone = request.data.get("phone")  # without +91
        template_name = request.data.get("template_name")
        language_code = request.data.get("language_code", "en")
        body_params = request.data.get("body_params", [])

        # Validate required inputs
        if not all([phone, template_name, body_params]):
            return Response({
                "result": False,
                "message": "Missing one or more required fields: phone, template_name, body_params"
            }, status=400)

        # Convert parameters into WhatsApp format
        body_parameters = [{"type": "text", "text": str(param)} for param in body_params]

        # Build payload
        payload = {
            "messaging_product": "whatsapp",
            "to": "91" + phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": body_parameters
                    }
                ]
            }
        }

        # Make request to WhatsApp API
        url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.post(url, headers=headers, json=payload)
        return Response(response.json(), status=response.status_code)

    except Exception as e:
        return Response({
            "result": False,
            "message": "Unexpected error occurred",
            "error": str(e)
        }, status=500)





@api_view(['POST'])
def send_email(request):
    user_email = request.data.get('email')
    subject = request.data.get('subject')
    message = request.data.get('message')

    # Validate input
    if not user_email or not subject or not message:
        return Response({'success': False, 'message': 'Email, subject, and message are required in request body.'})

    from_email = None  # Will use DEFAULT_FROM_EMAIL from settings
    recipient_list = [user_email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return Response({'success': True, 'message': f'Email sent to {user_email}'})
    except Exception as e:
        return Response({'success': False, 'message': str(e)})




