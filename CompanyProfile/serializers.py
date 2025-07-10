from rest_framework import serializers
from Masters.models import Country, Currency
from Masters.serializers import CountrySerializer, CurrencySerializer
from .models import CompanyProfile

class CompanyProfileSerializer(serializers.ModelSerializer):
    # These handle both read and write cleanly
    CountryId = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all()
    )
    CurrencyId = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all()
    )

    class Meta:
        model = CompanyProfile
        fields = '__all__'
        extra_kwargs = {
            # Required fields
            'OwnerId': {'required': True},
            'BranchId': {'required': True},
            'DepartmentId': {'required': True},

            # Optional fields with allow_null = True
            'AddressLine2': {'allow_null': True},
            'CountryId': {'allow_null': True},
            'CurrencyId': {'allow_null': True},
            'Logo': {'allow_null': True},
            'UserProfileImage': {'allow_null': True},
            'TermsAndConditions': {'allow_null': True},
            'CurrentPassword': {'allow_null': True},
            'NewPassword': {'allow_null': True},
            'ConfirmPassword': {'allow_null': True},
        }
    def to_representation(self, instance):
        """Customize output to return nested country & currency details."""
        data = super().to_representation(instance)
        data['CountryId'] = CountrySerializer(instance.CountryId).data if instance.CountryId else None
        data['CurrencyId'] = CurrencySerializer(instance.CurrencyId).data if instance.CurrencyId else None
        return data

    def validate(self, data):
        if self.instance is None:  # Only for create
            owner = data.get('OwnerId')
            branch = data.get('BranchId')
            department = data.get('DepartmentId')
            company_name = data.get('CompanyName')

            if CompanyProfile.objects.filter(
                OwnerId=owner,
                BranchId=branch,
                DepartmentId=department,
                CompanyName__iexact=company_name.strip()
            ).exists():
                raise serializers.ValidationError({
                    'message': "Company profile with the same Owner, Branch, Department, and CompanyName already exists."
                })
        return data
