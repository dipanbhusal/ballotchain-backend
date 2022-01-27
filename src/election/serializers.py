from rest_framework import serializers

from accounts.models import Candidate, Party

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('id', 'name', 'description', 'logo', 'plans', 'vote_count')

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ('id', 'first_name', 'last_name', 'party')

    def to_representation(self, instance):
        self.fields['party'] = PartySerializer(read_only=True)
        return super(CandidateSerializer, self).to_representation(instance)


class VoteCastSerializer(serializers.Serializer):
    pw = serializers.CharField()
    candidate_id = serializers.CharField()
    