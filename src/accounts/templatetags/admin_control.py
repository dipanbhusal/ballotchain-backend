from django import template
from django.utils.safestring import mark_safe

from blockchain.electionAdmin import ElectionAdmin
from blockchain.contractFunctions import state as st, admin as adm

register = template.Library()

@register.inclusion_tag('admin/admin_control.html', takes_context=True)
def admin_control(context):
    admin = ElectionAdmin()
    request = context['request']
    state = st()
    el_admin = adm()
    if state == 0:
        el_state = "Not Started"
    elif state == 1:
        el_state = "Voting Started"
    else:
        el_state = f"Voting progress {state}"
    data = {'state': el_state, 'admin': el_admin}

    if "start-election" in request.POST:
        recipt = admin.start_election()
        txn_hash = recipt['transactionHash'].hex()
        url = f"https://rinkeby.etherscan.io/tx/{txn_hash}"
        state = st()
        if recipt['status']:
            data['message'] = mark_safe(
                f'<p style="color:green;"> Successfully started the election. \
                Visit <a href={url}>{url}</a> for more details. </p>'
                )
            return data
        else:
            data['message'] = mark_safe(
                f'<p style="color:red;"> Error occured while starting the election. \
                Visit <a href={url}>{url}</a> for more details. </p>'
                )
            return data
    
    if "end-election" in request.POST:
        recipt = admin.end_election()
        txn_hash = recipt['transactionHash'].hex()
        url = f"https://rinkeby.etherscan.io/tx/{txn_hash}"
        state = st()
        if recipt['status']:
            data['message'] = mark_safe(
                f'<p style="color:green;"> Successfully ended the election. \
                Visit <a href={url}>{url}</a> for more details. </p>'
                )

        else:
            data['message'] = mark_safe(
                f'<p style="color:red;"> Error occured while ending the election. \
                Visit <a href={url}>{url}</a> for more details. </p>'
                )
    return data
