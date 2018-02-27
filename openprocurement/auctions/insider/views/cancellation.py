# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.financial.cancellation import (
    FinancialAuctionCancellationResource,
)


@opresource(name='dgfInsider:Auction Cancellations',
            collection_path='/auctions/{auction_id}/cancellations',
            path='/auctions/{auction_id}/cancellations/{cancellation_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction cancellations")
class InsiderAuctionCancellationResource(FinancialAuctionCancellationResource):
    pass
