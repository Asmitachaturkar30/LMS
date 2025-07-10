from django.apps import apps

def field_exists_in_model(model_name, field_name):
    for model in apps.get_models():
        if model.__name__ == model_name:
            return field_name in [field.name for field in model._meta.get_fields()]
    return False
