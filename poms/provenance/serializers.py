from rest_framework import serializers

from poms.common.serializers import (
    ModelWithUserCodeSerializer,
)
from poms.provenance.models import Source, Provider, ProviderVersion, SourceVersion


class ProviderSerializer(ModelWithUserCodeSerializer):
    class Meta:
        model = Provider
        fields = [
            "id",
            "master_user",
            "user_code",
            "name",
            "short_name",
            "public_name",

        ]


class ProviderVersionSerializer(ModelWithUserCodeSerializer):
    class Meta:
        model = ProviderVersion
        fields = [
            "id",
            "master_user",
            "user_code",
            "name",
            "short_name",
            "public_name",
            "provider",

            "version_semantic",
            "version_calendar"

        ]


class SourceSerializer(ModelWithUserCodeSerializer):
    class Meta:
        model = Source
        fields = [
            "id",
            "master_user",
            "user_code",
            "name",
            "short_name",
            "public_name"
        ]


class SourceVersionSerializer(ModelWithUserCodeSerializer):
    class Meta:
        model = SourceVersion
        fields = [
            "id",
            "master_user",
            "user_code",
            "name",
            "short_name",
            "public_name",
            "source",

            "version_semantic",
            "version_calendar"
        ]


class ModelWithProvenanceSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["provider"] = serializers.PrimaryKeyRelatedField(queryset=Provider.objects.all(),
                                                                     allow_null=True, required=False)
        self.fields["provider_object"] = ProviderSerializer(read_only=True)
        self.fields["provider_version"] = serializers.PrimaryKeyRelatedField(queryset=ProviderVersion.objects.all(),
                                                                              allow_null=True,
                                                                             required=False)
        self.fields["provider_version_object"] = ProviderVersionSerializer(read_only=True)

        self.fields["source"] = serializers.PrimaryKeyRelatedField(queryset=Source.objects.all(),
                                                                   allow_null=True, required=False)
        self.fields["source_object"] = SourceSerializer(read_only=True)
        self.fields["source_version"] = serializers.PrimaryKeyRelatedField(queryset=SourceVersion.objects.all(),
                                                                            allow_null=True,
                                                                           required=False)
        self.fields["source_version_object"] = SourceVersionSerializer(read_only=True)

    def validate(self, data):
        return data
