from django.core.validators import RegexValidator


def validate_name():
    return [
        RegexValidator(
            regex=r'^[a-zA-Z0-9_.\s]*$', message="Name doesn't contains special characters.", code='invalid_name'
        )
    ]


def api_response(data=None, message=None, status_code=200, success=True):
    response_data = {'success': success, 'message': message, 'data': data}

    return response_data
