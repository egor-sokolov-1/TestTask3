from rest_framework import serializers
from .models import Payout


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = [
            'id',
            'amount', 
            'currency',
            'recipient',
            'status',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
        
    def validate_currency(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Currency code must be 3 characters")
        return value.upper()
    