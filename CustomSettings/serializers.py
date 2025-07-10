from rest_framework import serializers
from .models import CustomSetting
from rest_framework import serializers

class CaseInsensitiveChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            for key in self.choices.keys():
                if key.lower() == data.lower():
                    return key
        self.fail("invalid_choice", input=data)

    def to_representation(self, value):
        return super().to_representation(value)


class CustomSettingSerializer(serializers.ModelSerializer):
    Type = CaseInsensitiveChoiceField(choices=CustomSetting._meta.get_field('Type').choices)

    class Meta:
        model = CustomSetting
        fields = '__all__'
        extra_kwargs = {
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},
            'ModuleId': {'required': True},
            'UDF_ID': {'allow_null': True},
            'FieldLabelName': {'allow_null': True},
            'IsMandatory': {'allow_null': True},
            'IsVisible': {'allow_null': True},
            'Type': {'allow_null': True}
        }
    def validate(self, data):
        module_id = data.get('ModuleId')
        owner_id = data.get('OwnerId')
        branch_id = data.get('BranchId')
        department_id = data.get('DepartmentId')
        udf_id = data.get('UDF_ID')
        field_label = data.get('FieldLabelName')

        if CustomSetting.objects.filter(
            ModuleId=module_id,
            OwnerId=owner_id,
            BranchId=branch_id,
            DepartmentId=department_id,
            UDF_ID=udf_id,
            FieldLabelName=field_label
        ).exists():
            raise serializers.ValidationError({
                "message": "Custom Setting with the same Module, UDF ID, and Field Label already exists."
            })

        return data
