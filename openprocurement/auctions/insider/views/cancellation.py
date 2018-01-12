# -*- coding: utf-8 -*-

from openprocurement.auctions.core.utils import (
    opresource,
    add_next_award,
)
from openprocurement.auctions.dgf.views.financial.cancellation import (
    FinancialAuctionCancellationResource,
)
from openprocurement.auctions.insider.constants import TENDER_PERIOD_STATUSES


@opresource(name='dgfInsider:Auction Cancellations',
            collection_path='/auctions/{auction_id}/cancellations',
            path='/auctions/{auction_id}/cancellations/{cancellation_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction cancellations")
class InsiderAuctionCancellationResource(FinancialAuctionCancellationResource):

    def cancel_auction(self):
        auction = self.request.validated['auction']
        if auction.status in TENDER_PERIOD_STATUSES:
            auction.bids = []
        auction.status = 'cancelled'

    def cancel_lot(self, cancellation=None):

        if not cancellation:
            cancellation = self.context
        auction = self.request.validated['auction']
        [setattr(i, 'status', 'cancelled') for i in auction.lots if i.id == cancellation.relatedLot]
        statuses = set([lot.status for lot in auction.lots])
        if statuses == set(['cancelled']):
            self.cancel_auction()
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            auction.status = 'unsuccessful'
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            auction.status = 'complete'
        if 'active.auction' in auction.status and all([
            i.auctionPeriod and i.auctionPeriod.endDate
            for i in self.request.validated['auction'].lots
            if i.numberOfBids > 1 and i.status == 'active'
        ]):
            add_next_award(self.request)
