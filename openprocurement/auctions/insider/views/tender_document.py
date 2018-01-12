# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
)
from openprocurement.api.validation import validate_file_upload
from openprocurement.auctions.core.utils import (
    opresource,
    save_auction,
)
from openprocurement.auctions.dgf.utils import upload_file
from openprocurement.auctions.dgf.views.financial.tender_document import (
    FinancialAuctionDocumentResource,
)
from openprocurement.auctions.insider.constants import TENDER_PERIOD_STATUSES


@opresource(name='dgfInsider:Auction Documents',
            collection_path='/auctions/{auction_id}/documents',
            path='/auctions/{auction_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction related binary files (PDFs, etc.)")
class InsiderAuctionDocumentResource(FinancialAuctionDocumentResource):

    @json_view(permission='upload_auction_documents', validators=(validate_file_upload,))
    def collection_post(self):
        """Auction Document Upload"""
        if self.request.authenticated_role != 'auction' and self.request.validated['auction_status'] != 'active.tendering' or \
           self.request.authenticated_role == 'auction' and 'active.auction' not in self.request.validated['auction_status']\
                                                        and self.request.validated['auction_status'] != 'active.qualification':
            self.request.errors.add('body', 'data', 'Can\'t add document in current ({}) auction status'.format(self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}
