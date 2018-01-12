# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.auctions.core.utils import (
    opresource,
)
from openprocurement.auctions.dgf.views.financial.bid_document import (
    FinancialAuctionBidDocumentResource,
)
from openprocurement.auctions.insider.constants import TENDER_PERIOD_STATUSES


@opresource(name='dgfInsider:Auction Bid Documents',
            collection_path='/auctions/{auction_id}/bids/{bid_id}/documents',
            path='/auctions/{auction_id}/bids/{bid_id}/documents/{document_id}',
            auctionsprocurementMethodType="dgfInsider",
            description="Insider auction bidder documents")
class InsiderAuctionBidDocumentResource(FinancialAuctionBidDocumentResource):

    def validate_bid_document(self, operation):
        auction = self.request.validated['auction']
        if self.request.validated['auction_status'] not in TENDER_PERIOD_STATUSES and self.request.validated['auction_status'] != 'active.qualification':
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) auction status'.format(operation, auction.status))
            self.request.errors.status = 403
            return
        if auction.status in TENDER_PERIOD_STATUSES and not (auction.tenderPeriod.startDate < get_now() < auction.tenderPeriod.endDate):
            self.request.errors.add('body', 'data', 'Document can be {} only during the tendering period: from ({}) to ({}).'.format('added' if operation == 'add' else 'updated', auction.tenderPeriod.startDate.isoformat(), auction.tenderPeriod.endDate.isoformat()))
            self.request.errors.status = 403
            return
        if auction.status == 'active.qualification' and not [i for i in auction.awards if 'pending' in i.status and i.bid_id == self.request.validated['bid_id']]:
            self.request.errors.add('body', 'data', 'Can\'t {} document because award of bid is not in pending state'.format(operation))
            self.request.errors.status = 403
            return
        return True
