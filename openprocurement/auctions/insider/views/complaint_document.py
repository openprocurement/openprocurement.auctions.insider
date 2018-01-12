# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    upload_file,
    json_view,
    context_unpack,
)
from openprocurement.api.validation import validate_file_upload
from openprocurement.auctions.core.utils import (
    opresource,
    save_auction,
)
from openprocurement.auctions.dgf.views.financial.complaint_document import (
    FinancialComplaintDocumentResource,
)
from openprocurement.auctions.insider.constants import TENDER_PERIOD_STATUSES


STATUS4ROLE = {
    'complaint_owner': ['draft', 'answered'],
    'reviewers': ['pending'],
    'auction_owner': ['claim'],
}


@opresource(name='dgfInsider:Auction Complaint Documents',
            collection_path='/auctions/{auction_id}/complaints/{complaint_id}/documents',
            path='/auctions/{auction_id}/complaints/{complaint_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction complaint documents")
class InsiderComplaintDocumentResource(FinancialComplaintDocumentResource):

    @json_view(validators=(validate_file_upload,), permission='edit_complaint')
    def collection_post(self):
        """Auction Complaint Document Upload
        """
        if self.request.validated['auction_status'] not in TENDER_PERIOD_STATUSES and self.request.validated['auction_status'] not in ['active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) auction status'.format(
                self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if self.context.status not in STATUS4ROLE.get(self.request.authenticated_role, []):
            self.request.errors.add('body', 'data',
                                    'Can\'t add document in current ({}) complaint status'.format(self.context.status))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        document.author = self.request.authenticated_role
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction complaint document {}'.format(document.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_complaint_document_create'},
                                                  {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route,
                                                                                       document_id=document.id,
                                                                                       _query={})
            return {'data': document.serialize("view")}
