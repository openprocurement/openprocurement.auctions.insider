# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.core.awarding_2_0.views import (
    AuctionAwardComplaintResource,
)

@opresource(name='dgfInsider:Auction Award Complaints',
            collection_path='/auctions/{auction_id}/awards/{award_id}/complaints',
            path='/auctions/{auction_id}/awards/{award_id}/complaints/{complaint_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction award complaints")
class InsiderAuctionAwardComplaintResource(AuctionAwardComplaintResource):
    pass
