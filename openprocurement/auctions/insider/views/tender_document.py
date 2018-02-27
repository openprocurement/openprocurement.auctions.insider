# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.financial.tender_document import (
    FinancialAuctionDocumentResource,
)


@opresource(name='dgfInsider:Auction Documents',
            collection_path='/auctions/{auction_id}/documents',
            path='/auctions/{auction_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction related binary files (PDFs, etc.)")
class InsiderAuctionDocumentResource(FinancialAuctionDocumentResource):
    pass
