# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.financial.bid import (
    FinancialAuctionBidResource,
)


@opresource(name='dgfInsider:Auction Bids',
            collection_path='/auctions/{auction_id}/bids',
            path='/auctions/{auction_id}/bids/{bid_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction bids")
class InsiderAuctionBidResource(FinancialAuctionBidResource):
    pass

