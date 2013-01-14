import commonware.log

from cached import Resource
from lib.bango.forms import NotificationForm
from lib.transactions.constants import STATUS_COMPLETED

log = commonware.log.getLogger('s.bango')


class NotificationResource(Resource):
    """
    Process a Bango notification. Here is an example of a successful Bango
    redirect URL query string:

    ?ResponseCode=OK&ResponseMessage=Success&BangoUserId=412448521
    &MerchantTransactionId=86c8a8fa-d45a-43ff-8291-012ca1e26a51
    &BangoTransactionId=668694391
    &TransactionMethods=USA_TMOBILE%2cT-Mobile+USA%2cTESTPAY%2cTest+Pay
    &BillingConfigurationId=2830&MozSignature
    =0dfa157725e7f20f5928951154de919c347b1dbcf41b8f406b7a44d193a81bbb&P=
    """

    class Meta(Resource.Meta):
        resource_name = 'payment_notice'
        list_allowed_methods = ['post']

    def obj_create(self, bundle, request, **kwargs):
        form = NotificationForm(bundle.data)
        bill_conf_id = form.data.get('billing_config_id')
        log.info('Received notification for billing_config_id %r: '
                 'bango_response_code: %r; bango_response_message: %r; '
                 'bango_trans_id: %r'
                 % (bill_conf_id,
                    form.data.get('bango_response_code'),
                    form.data.get('bango_response_message'),
                    form.data.get('bango_trans_id')))

        if not form.is_valid():
            log.info('Notification invalid: %s' % bill_conf_id)
            raise self.form_errors(form)

        trans = form.cleaned_data['moz_transaction']
        if form.cleaned_data['bango_response_code'] == 'OK':
            log.info('Transaction completed: %s' % trans.uuid)
            trans.status = STATUS_COMPLETED

        else:
            log.info('Transaction failed: %s' % trans.uuid)
            raise NotImplementedError('Failures will be in bug 828513')

        trans.save()
        return bundle
