# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.tender import (
    AuctionResourceTestMixin, DgfInsiderResourceTestMixin
)
from openprocurement.auctions.core.tests.blanks.tender_blanks import (
    # AuctionTest
    simple_add_auction,
    # AuctionProcessTest
    one_valid_bid_auction,
    one_invalid_bid_auction,
)

from openprocurement.auctions.dgf.constants import ELIGIBILITY_CRITERIA

from openprocurement.auctions.insider.models import DGFInsider
from openprocurement.auctions.insider.tests.base import (
    test_insider_auction_data,
    test_organization, test_financial_organization,
    BaseInsiderAuctionWebTest, BaseInsiderWebTest,
)
from openprocurement.auctions.insider.tests.blanks.tender_blanks import (
    # InsiderAuctionTest
    create_role,
    edit_role,
    # InsiderAuctionResourceTest
    create_auction_invalid,
    create_auction_auctionPeriod,
    create_auction_generated,
    create_auction,
    # InsiderAuctionProcessTest
    first_bid_auction,
    auctionUrl_in_active_auction,
    suspended_auction
)


class InsiderAuctionTest(BaseInsiderWebTest):
    auction = DGFInsider
    initial_data = test_insider_auction_data

    test_simple_add_auction = snitch(simple_add_auction)
    test_create_role = snitch(create_role)
    test_edit_role = snitch(edit_role)


class InsiderAuctionResourceTest(BaseInsiderWebTest, AuctionResourceTestMixin, DgfInsiderResourceTestMixin):
    initial_status = 'active.tendering'
    initial_data = test_insider_auction_data
    initial_organization = test_organization
    eligibility_criteria = ELIGIBILITY_CRITERIA
    test_financial_organization = test_financial_organization

    test_create_auction_invalid = snitch(create_auction_invalid)
    test_create_auction_auctionPeriod = snitch(create_auction_auctionPeriod)
    test_create_auction_generated = snitch(create_auction_generated)
    test_create_auction = snitch(create_auction)


class InsiderAuctionProcessTest(BaseInsiderAuctionWebTest):

    test_financial_organization = test_financial_organization

    #setUp = BaseInsiderWebTest.setUp
    def setUp(self):
        super(InsiderAuctionProcessTest.__bases__[0], self).setUp()

    test_one_valid_bid_auction = unittest.skip('option not available')(snitch(one_valid_bid_auction))
    test_one_invalid_bid_auction = unittest.skip('option not available')(snitch(one_invalid_bid_auction))
    test_first_bid_auction = snitch(first_bid_auction)
    test_auctionUrl_in_active_auction = snitch(auctionUrl_in_active_auction)
    test_suspended_auction = snitch(suspended_auction)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(InsiderAuctionTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionProcessTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
