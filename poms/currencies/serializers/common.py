from poms.common.serializers import ModelWithTimeStampSerializer, ModelWithUserCodeSerializer
from poms.currencies.models import Currency
from poms.users.fields import MasterUserField


class CurrencyEvalSerializer(ModelWithUserCodeSerializer, ModelWithTimeStampSerializer):
    master_user = MasterUserField()

    class Meta:
        model = Currency
        fields = [
            "id",
            "master_user",
            "user_code",
            "name",
            "short_name",
            "notes",
            "reference_for_pricing",
            "pricing_condition",
            "default_fx_rate",
            "is_deleted",
            "is_enabled",
        ]

        read_only_fields = fields
