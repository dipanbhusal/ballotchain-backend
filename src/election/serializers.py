from rest_framework import serializers

from accounts.models import Candidate, Party
from .models import Election

class PartySerializer(serializers.ModelSerializer):
    # logo_url = serializers.SerializerMethodField('get_photo_url')
    class Meta:
        model = Party
        fields = ('id', 'name', 'description', 'logo', 'plans', 'vote_count',)

    # def get_photo_url(self, instance):
    #     print(self.context)
    #     request = self.context.get('request')
    #     photo_url = instance.logo.url
    #     return request.build_absolute_uri(photo_url)

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'party', 'public_key')

    def to_representation(self, instance):
        self.fields['party'] = PartySerializer(read_only=True)
        return super(CandidateSerializer, self).to_representation(instance)


class VoteCastSerializer(serializers.Serializer):
    pw = serializers.CharField()
    candidate_id = serializers.CharField()
    election_address = serializers.CharField()
    

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = '__all__'


