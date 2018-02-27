# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.financial.complaint_document import (
    FinancialComplaintDocumentResource,
)


@opresource(name='dgfInsider:Auction Complaint Documents',
            collection_path='/auctions/{auction_id}/complaints/{complaint_id}/documents',
            path='/auctions/{auction_id}/complaints/{complaint_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction complaint documents")
class InsiderComplaintDocumentResource(FinancialComplaintDocumentResource):
    pass
