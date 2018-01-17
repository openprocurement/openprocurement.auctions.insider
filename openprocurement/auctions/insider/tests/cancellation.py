# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.insider.tests.base import (
    BaseInsiderAuctionWebTest, test_financial_bids,
    test_insider_auction_data, test_financial_organization,
)
from openprocurement.auctions.core.tests.cancellation import (
    AuctionCancellationResourceTestMixin,
    AuctionCancellationDocumentResourceTestMixin
)


class InsiderAuctionCancellationResourceTest(BaseInsiderAuctionWebTest,
                                             AuctionCancellationResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_financial_bids


class InsiderAuctionCancellationDocumentResourceTest(BaseInsiderAuctionWebTest,
                                                     AuctionCancellationDocumentResourceTestMixin):

    def setUp(self):
        super(InsiderAuctionCancellationDocumentResourceTest, self).setUp()
        # Create cancellation
        response = self.app.post_json('/auctions/{}/cancellations'.format(
            self.auction_id), {'data': {'reason': 'cancellation reason'}})
        cancellation = response.json['data']
        self.cancellation_id = cancellation['id']


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InsiderAuctionCancellationResourceTest))
    suite.addTest(unittest.makeSuite(InsiderAuctionCancellationDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
