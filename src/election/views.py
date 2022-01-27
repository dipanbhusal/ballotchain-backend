from uuid import UUID
from django.contrib.auth.hashers import check_password
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.cryptography import CryptoFernet
from accounts.extraModules import crypOperation, getSHA256Hash
from accounts.middleware import get_user
from accounts.models import Candidate, Party, Profile
from rest_framework_simplejwt.authentication import JWTAuthentication
from blockchain.contractFunctions import candidate, electionResult, state, totalCandidates, totalVoters, totalVotes, voter

from blockchain.electionVoter import Voter

from .serializers import CandidateSerializer, PartySerializer, VoteCastSerializer
# Create your views here.

class CandidatesListView(generics.ListAPIView):
    """
    View for list of candidates
    """
    authentication_classes = (JWTAuthentication, )

    def dispatch(self, *args, **kwargs):
        self.message = {
            'message': None, 'details': {}
        }
        return super().dispatch( *args, **kwargs)

    def get(self, request, *args, **kwargs):
        candidates = Candidate.objects.all()
        candidates_serializer = CandidateSerializer(candidates, many=True)
        self.message['details'] = candidates_serializer.data
        return Response(self.message, status=status.HTTP_200_OK)


class CandidateDetailView(generics.RetrieveAPIView):
    """
    View for retrieving detail of candidate
    """
    authentication_classes = (JWTAuthentication, )

    def dispatch(self, *args, **kwargs):
        self.message = {
            'message': None, 'details': {}
        }
        return super().dispatch( *args, **kwargs)

    def get(self, request, *args, **kwargs):
        candidates = Candidate.objects.get(id=request.GET.get('id'))
        candidates_serializer = CandidateSerializer(candidates)
        self.message['details'] = candidates_serializer.data
        return Response(self.message, status=status.HTTP_200_OK)


class PartiesListView(generics.ListAPIView):
    """
    View for list of candidates
    """
    authentication_classes = (JWTAuthentication, )

    def dispatch(self, *args, **kwargs):
        self.message = {
            'message': None, 'details': {}
        }
        return super().dispatch( *args, **kwargs)

    #list of parties
    def get(self, request, *args, **kwargs):
        party_obj = Party.objects.all()
        party_serializer = PartySerializer(party_obj, many=True)

        self.message['details'] = party_serializer.data
        return Response(self.message, status=status.HTTP_200_OK)


class PartyDetailView(generics.RetrieveAPIView):
    """
    View for list of candidates
    """
    authentication_classes = (JWTAuthentication, )
    
    def dispatch(self, *args, **kwargs):
        self.message = {
            'message': None, 'details': {}
        }
        return super().dispatch( *args, **kwargs)

    def get(self, request, *args, **kwargs):
        party = Party.objects.get(id=request.GET.get('id'))
        party_serializer = PartySerializer(party)
        self.message['details'] = party_serializer.data
        return Response(self.message, status=status.HTTP_200_OK)


class CastVoteView(APIView):
    """
    View for casting vote by voters
    """
    authentication_classes = (JWTAuthentication, )
    def dispatch(self, *args, **kwargs):
        self.message = {
            'message': None, 'details': {}
        }
        return super().dispatch( *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        serializer = VoteCastSerializer(data=request.data)
        prof = Profile.objects.filter(user=get_user())
        if prof.exists() and not prof.first().has_voted :
            if serializer.is_valid():
                input_pw = serializer.data['pw'] #raw password from post request
                key = getSHA256Hash(input_pw)
                user_pw = get_user().password #hashed form of current user's password
                is_pw_valid = check_password(input_pw, user_pw)

                if is_pw_valid:
                    ferent = CryptoFernet(key)
                    private_key_cipher = prof.first().private_key
                    private_key_plain = ferent.decrypt(private_key_cipher)
                    candidate_obj = Candidate.objects.get(public_key=serializer.data['candidate_id'])
                    voter_obj = Voter(private_key_plain)
                    from blockchain.authenticate import w3
                    acnt = w3.eth.account.privateKeyToAccount(private_key_plain)

                    try:
                        recipt = voter_obj.castVote(candidate_obj.public_key)
                    except ValueError as e:
                        print(e)
                        self.message['message'] = "No sufficient funds"
                        return Response(self.message, status=status.HTTP_400_BAD_REQUEST)
                    txn_status = recipt['status']

                    txn_hash = recipt['transactionHash'].hex()
                    if not txn_status:
                        voter_acc = voter(prof.first().public_key)
                        if voter_acc[2]:
                            self.message['message'] = "User has already voted."
                        else:
                            self.message['message'] = "Voting not successful"
                            self.message['details'] = {
                                'status' : False,
                                'link': f'https://rinkeby.etherscan.io/tx/{txn_hash}'
                            }
                        return Response(self.message, status=status.HTTP_400_BAD_REQUEST)
                    candidate_obj.vote_count += 1
                    candidate_obj.party.vote_count += 1
                    candidate_obj.party.save()
                    candidate_obj.save()
                    user = get_user()
                    
                    user.profile.has_voted=True
                    user.profile.save()
                    #todo ->> send mail after voting successful
                    self.message['message'] = "Voted successfully"
                    self.message['details'] = {
                        'status' : True,
                        'link' : f'https://rinkeby.etherscan.io/tx/{txn_hash}'
                    }
                    return Response(self.message, status=status.HTTP_200_OK)

                else:
                    self.message['message'] = "Password is not valid"
                    return Response(self.message, status=status.HTTP_401_UNAUTHORIZED)
            else:
                self.message['message'] = "Error Occured"
                self.message['details'] = serializer.errors
                return Response(self.message, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.message['message'] = "Already voted"

            return Response(self.message, status=status.HTTP_400_BAD_REQUEST)


class ElectionResultView(APIView):
    def dispatch(self, *args, **kwargs):
        self.message = {
            'message': None, 'details': {}
        }
        return super().dispatch( *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        candidates_list = Candidate.objects.all()
        candidate_serializer = CandidateSerializer(candidates_list, many=True)
        election_state = state()
        if election_state == 1:

            election_state = "On Voting Proces"

            counts = {
                "total_votes_count": totalVotes(),
                "total_voters_count": totalVoters(),
                "total_candidates_count": totalCandidates(),
                "election_state": election_state
            }

            election_result = electionResult()

            final_data = []
            for each in election_result:
                data = each[0]
                candidate = Candidate.objects.get(public_key=data[1])
                data = {
                    "from": data[0], 
                    "to": {"public_key": candidate.public_key, "first_name": candidate.first_name, "last_name": candidate.last_name, }
                }
                final_data.append(data)

            summary = {**counts}
            summary['votes'] = final_data
            summary['candidates_data'] = candidate_serializer.data
            summary['party_data'] = PartySerializer(Party.objects.all(), many=True).data
            self.message['message'] = "Result data loaded successfully"
            self.message['details'] = summary
            return Response(self.message, status=status.HTTP_200_OK)
        elif election_state == 0:
            self.message['message'] = "Election is not started"
            return Response(self.message)
        #Failed txn
        # {
        #     'blockHash': HexBytes('0xbc0aa1649ccaf95d63c9d3dd18e8990b1bdbb02ecb2a0670df2e534689e15694'), 
        #     'blockNumber': 10064630, 
        #     'contractAddress': None, 
        #     'cumulativeGasUsed': 12415760, 
        #     'effectiveGasPrice': 1000000016, 
        #     'from': '0xC9D699B106D1A0986741B597be4B52E7bD09D95B', 
        #     'gasUsed': 24411, 
        #     'logs': [], 
        #     'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'), 
        #     'status': 0, 
        #     'to': '0x5aE08F85e970f3b63dE8889dA7979CE19e5f37c0', 
        #     'transactionHash': HexBytes('0x9e4598016215ef1109a4de10228641502dcd7240b341df7c4e5d7ec434660bb1'), 
        #     'transactionIndex': 36, 
        #     'type': '0x0'
        # }

        #Successful TXN
        # {
        #     'blockHash': HexBytes('0x54a7811bdaf343d66fc776de545384583edc0fcae891b341ca3dc004d40cd125'), 'blockNumber': 10064642, 
        #     'contractAddress': None, 
        #     'cumulativeGasUsed': 6004962, 
        #     'effectiveGasPrice': 1000000012, 
        #     'from': '0xC9D699B106D1A0986741B597be4B52E7bD09D95B', 
        #     'gasUsed': 92259, 'logs': [], 
        #     'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'), 
        #     'status': 1, 
        #     'to': '0x5aE08F85e970f3b63dE8889dA7979CE19e5f37c0', 
        #     'transactionHash': HexBytes('0xd08b071fa8b567536eaf3edacde08bbab421aee227f93bff6ae6e2a286aa22b8'), 
        #     'transactionIndex': 35, 
        #     'type': '0x0'
        # }