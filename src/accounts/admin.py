from django.contrib import admin
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.core.cache import cache
from accounts.cryptography import CryptoFernet
from accounts.extraModules import getSHA256Hash
from blockchain.authenticate import create_account
from blockchain.electionAdmin import ElectionAdmin
from . import models 
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'is_voter', 'is_verified', 'added_to_chain')
    search_fields = ('first_name', 'last_name')
    radio_fields = {'gender': admin.HORIZONTAL}
    exclude = ('private_key','added_to_chain', 'is_voter', )
    readonly_fields = ['citizenship_image_front_preview', 'citizenship_image_back_preview', 'public_key', ]
    # change_form_template = "admin/accounts/profile/change_form.html"

    def citizenship_image_front_preview(self, obj):
        return format_html('<img src="{}" width="auto" height="200px" />'.format(obj.citizenship_image_front.url))
    
    def citizenship_image_back_preview(self, obj):
        return format_html('<img src="{}" width="auto" height="200px" />'.format(obj.citizenship_image_back.url))

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
                fernet = CryptoFernet(getSHA256Hash(key))
                cipher_private_key = fernet.encrypt(account.privateKey.hex())
                obj.private_key =  cipher_private_key
                obj.save()
                self.message_user(request, f"Public key for {obj.user.first_name} is {account.address}")

                return HttpResponseRedirect('.')
            except Exception as e:
                print(e)
                messages.error(request, "Error occured. Please try again")
        
        if 'add-to-chain' in request.POST:
            admin = ElectionAdmin()
            recipt = admin.add_voter(obj.public_key, obj.enrolled_election.public_key)
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
                obj.added_to_chain = True
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
    # change_form_template = "admin/accounts/candidates/change_form.html"
    list_display = ('id', 'first_name', 'last_name', 'added_to_chain')
    fields = ('first_name', 'last_name', 'party', 'bio', 'plans', 'enrolled_election',)
    readonly_fields = ('public_key', )


    def response_change(self, request, obj):
        if 'add-to-chain' in request.POST:
            admin = ElectionAdmin()
            recipt = admin.add_candidate(obj.public_key, obj.enrolled_election.public_key)
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
admin.site.register(models.Party)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Candidate, CandidateAdmin)

admin.site.site_header = 'BallotChain'
admin.site.index_title = 'Admin Panel For BallotChain'
