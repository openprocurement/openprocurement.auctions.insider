# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.insider.views.other.bid import (
    AuctionBidResource,
)


@opresource(name='dgfFinancialAssets:Auction Bids',
            collection_path='/auctions/{auction_id}/bids',
            path='/auctions/{auction_id}/bids/{bid_id}',
            auctionsprocurementMethodType="dgfFinancialAssets",
            description="Financial auction bids")
class FinancialAuctionBidResource(AuctionBidResource):
    pass
