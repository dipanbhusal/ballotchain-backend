from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from blockchain.authenticate import create_account

from blockchain.electionAdmin import ElectionAdmin
from blockchain.contractFunctions import state as st, admin as adm

from . import models 


class ElectionsAdmin(admin.ModelAdmin):
    change_form_template = "admin/election/election/change_form.html"
    list_display = ('id','title', 'status', 'start_time', 'end_time', 'added_to_chain')
    fields = ('title', 'description', 'start_time', 'end_time', 'status', 'public_key')
    readonly_fields = ['public_key',]

    def response_change(self, request, obj):

        #Start election
        if 'start-election' in request.POST:
            admin = ElectionAdmin()
            recipt = admin.start_election(obj.public_key)
            txn_hash = recipt['transactionHash'].hex()
            url = f"https://rinkeby.etherscan.io/tx/{txn_hash}"
            obj.status = "started"
            obj.save()
            if recipt['status']:
                self.message_user(request, mark_safe(
                    f'<p style="color:green;"> Successfully started the election. \
                    Visit <a href={url}>{url}</a> for more details. </p>'
                    ))
            else:
                self.message_user(request,  mark_safe(
                    f'<p style="color:red;"> Error occured while starting the election. \
                    Visit <a href={url}>{url}</a> for more details. </p>'
                    ))
        
        #Ending election
        if "end-election" in request.POST:
            admin = ElectionAdmin()
            recipt = admin.end_election(obj.public_key)
            txn_hash = recipt['transactionHash'].hex()
            url = f"https://rinkeby.etherscan.io/tx/{txn_hash}"
            obj.status = "ended"
            obj.save()
            if recipt['status']:
                self.message_user(request, mark_safe(
                    f'<p style="color:green;"> Successfully ended the election. \
                    Visit <a href={url}>{url}</a> for more details. </p>'
                    )
                )
            else:
                self.message_user(request, mark_safe(
                    f'<p style="color:red;"> Error occured while ending the election. \
                    Visit <a href={url}>{url}</a> for more details. </p>'
                    ))


        if 'add-to-chain' in request.POST:
            admin = ElectionAdmin()
            recipt = admin.add_election(obj.public_key)
            txn_hash = recipt['transactionHash'].hex()
            url = f'https://rinkeby.etherscan.io/tx/{txn_hash}'
            if recipt['status']:
                
                obj.save()
                self.message_user(
                    request, mark_safe(
                        f'Successfully added election to blockchain eth-net.\
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
                self.message_user(request, f"Public key for {obj.title} is {account.address}")

                return HttpResponseRedirect('.')
            except Exception as e:
                messages.error(request, "Error occured. Please try again. ", e)
        
        return super().response_change(request, obj)

admin.site.register(models.Election, ElectionsAdmin)