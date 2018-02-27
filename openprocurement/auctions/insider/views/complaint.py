# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.financial.complaint import (
    FinancialAuctionComplaintResource,
)


@opresource(name='dgfInsider:Auction Complaints',
            collection_path='/auctions/{auction_id}/complaints',
            path='/auctions/{auction_id}/complaints/{complaint_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction complaints")
class InsiderAuctionComplaintResource(FinancialAuctionComplaintResource):
    pass
