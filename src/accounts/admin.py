from django.contrib import admin
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.core.cache import cache
from accounts.cryptography import CryptoFernet
from blockchain.authenticate import create_account
from blockchain.electionAdmin import ElectionAdmin
from . import models 
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'is_voter', 'is_verified')
    search_fields = ('first_name', 'last_name')
    radio_fields = {'gender': admin.HORIZONTAL}
    change_form_template = "admin/accounts/profile/change_form.html"

    def first_name(self, obj):
        return obj.user.first_name[:10]

    def last_name(self, obj):
        return obj.user.last_name[:10]

    def response_change(self, request, obj):
        if "generate-id" in request.POST:
            if obj.public_key:
                messages.error(request, f"Public key for current user already exists.")
                return HttpResponseRedirect('.')
            try:
                account = create_account()
                obj.public_key = account.address
                key = cache.get(f"{obj.user.id}_user")
                fernet = CryptoFernet(key)
                cipher_private_key = fernet.encrypt(account.privateKey.hex())
                obj.private_key =  cipher_private_key
                obj.save()
                self.message_user(request, f"Public key for {obj.user.first_name} is {account.address}")

                return HttpResponseRedirect('.')
            except:
                messages.error(request, "Error occured. Please try again")
        
        if 'add-to-chain' in request.POST:
            admin = ElectionAdmin()
            recipt = admin.add_voter(obj.public_key)
            txn_hash = recipt['transactionHash'].hex()
            url = f'https://rinkeby.etherscan.io/tx/{txn_hash}'
            if recipt['status']:
                self.message_user(
                    request, mark_safe(
                        f'Successfully added voter to blockchain eth-net.\
                        Find more in <a href={url}>{url}</a>'
                    )
                )
                obj.is_voter = True
                obj.save()
                return HttpResponseRedirect('.')
            else:
                self.message_user(
                    request, mark_safe(
                        f'Cannot add voter to blockchain eth-net.\
                        Find more in <a href={url}>{url}</a>'
                    )
                )
            
        return super().response_change(request, obj)
    

class CandidateAdmin(admin.ModelAdmin):
    change_form_template = "admin/accounts/candidates/change_form.html"
    list_display = ('id', 'first_name', 'last_name', 'is_candidate')
    fields = ('first_name', 'last_name', 'public_key', 'party', 'bio', 'plans', 'is_candidate')


    def response_change(self, request, obj):
        if 'add-to-chain' in request.POST:
            admin = ElectionAdmin()
            recipt = admin.add_candidate(obj.public_key)
            txn_hash = recipt['transactionHash'].hex()
            url = f'https://rinkeby.etherscan.io/tx/{txn_hash}'
            if recipt['status']:
                
                obj.is_candidate = True
                obj.save()
                self.message_user(
                    request, mark_safe(
                        f'Successfully added voter to blockchain eth-net.\
                        Find more in <a href={url}>{url}</a>'
                    )
                )
                
                return HttpResponseRedirect('.')
        
        if "generate-id" in request.POST:
            if obj.public_key:
                messages.error(request, f"Public key for current user already exists.")
                return HttpResponseRedirect('.')
            try:
                account = create_account()
                obj.public_key = account.address
                obj.save()
                self.message_user(request, f"Public key for {obj.first_name} is {account.address}")

                return HttpResponseRedirect('.')
            except Exception as e:
                messages.error(request, "Error occured. Please try again. ", e)
        
        return super().response_change(request, obj)

admin.site.register(models.Users)
admin.site.register(models.RSAKeys)
admin.site.register(models.Party)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Candidate, CandidateAdmin)
admin.site.register(models.TemporaryAddress)
admin.site.register(models.PermanentAddress)

admin.site.site_header = 'BallotChain'
admin.site.index_title = 'Admin Panel For BallotChain'
