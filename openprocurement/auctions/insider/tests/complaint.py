# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.insider.tests.base import (
    BaseInsiderAuctionWebTest, test_financial_bids,
    test_insider_auction_data, test_financial_organization,
)
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.complaint import (
    AuctionComplaintResourceTestMixin,
    InsiderAuctionComplaintDocumentResourceTestMixin
)


class InsiderAuctionComplaintResourceTest(BaseInsiderAuctionWebTest, AuctionComplaintResourceTestMixin):
    """Test Case for Auction Complaint resource"""


class InsiderAuctionComplaintDocumentResourceTest(BaseInsiderAuctionWebTest, InsiderAuctionComplaintDocumentResourceTestMixin):

    def setUp(self):
        super(InsiderAuctionComplaintDocumentResourceTest, self).setUp()
        # Create complaint
        response = self.app.post_json('/auctions/{}/complaints'.format(
            self.auction_id), {'data': {'title': 'complaint title', 'description': 'complaint description', 'author': self.initial_organization}})
        complaint = response.json['data']
        self.complaint_id = complaint['id']
        self.complaint_owner_token = response.json['access']['token']


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InsiderAuctionComplaintDocumentResourceTest))
    suite.addTest(unittest.makeSuite(InsiderAuctionComplaintResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
