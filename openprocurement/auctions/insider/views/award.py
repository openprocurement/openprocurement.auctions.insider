# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.core.awarding_2_0.views import (
    AuctionAwardResource,
)


@opresource(name='dgfInsider:Auction Awards',
            collection_path='/auctions/{auction_id}/awards',
            path='/auctions/{auction_id}/awards/{award_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction awards")
class InsiderAuctionAwardResource(AuctionAwardResource):
    pass
