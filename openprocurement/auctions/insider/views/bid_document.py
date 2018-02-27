# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.financial.bid_document import (
    FinancialAuctionBidDocumentResource,
)


@opresource(name='dgfInsider:Auction Bid Documents',
            collection_path='/auctions/{auction_id}/bids/{bid_id}/documents',
            path='/auctions/{auction_id}/bids/{bid_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction bidder documents")
class InsiderAuctionBidDocumentResource(FinancialAuctionBidDocumentResource):
    pass
