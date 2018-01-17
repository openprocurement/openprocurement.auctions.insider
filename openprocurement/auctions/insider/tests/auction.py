# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.auction_blanks import (
    get_auction_auction_not_found,
    post_auction_auction_document
)
from openprocurement.auctions.insider.tests.base import (
    BaseInsiderAuctionWebTest,
    test_organization,
    test_financial_bids,
    test_financial_organization,
    test_insider_auction_data
)
from openprocurement.auctions.insider.tests.blanks.auction_blanks import (
    # InsiderAuctionAuctionResourceTest
    get_auction_auction,
    post_auction_auction,
    patch_auction_auction,
    # InsiderAuctionBidInvalidationAuctionResourceTest
    post_auction_all_invalid_bids,
    post_auction_one_bid_without_value,
    post_auction_zero_bids,
    # InsiderAuctionDraftBidAuctionResourceTest
    post_auction_all_draft_bids,
    # InsiderAuctionSameValueAuctionResourceTest
    post_auction_auction_not_changed,
    post_auction_auction_reversed,
    # InsiderAuctionNoBidsResourceTest
    post_auction_no_bids
)


class InsiderAuctionAuctionResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_financial_bids

    test_get_auction_auction_not_found = snitch(get_auction_auction_not_found)
    test_get_auction_auction = snitch(get_auction_auction)
    test_post_auction_auction = snitch(post_auction_auction)
    test_patch_auction_auction = snitch(patch_auction_auction)
    test_post_auction_auction_document = snitch(post_auction_auction_document)


class InsiderAuctionBidInvalidationAuctionResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.auction'
    initial_data = test_insider_auction_data
    initial_bids = [
        {
            "tenderers": [
                test_organization
            ],
            'qualified': True,
            "eligible": True
        }
        for i in range(3)
    ]

    test_post_auction_all_invalid_bids = unittest.skip("zero minimalstep")(snitch(post_auction_all_invalid_bids))
    test_post_auction_one_bid_without_value = snitch(post_auction_one_bid_without_value)
    test_post_auction_zero_bids = snitch(post_auction_zero_bids)


class InsiderAuctionDraftBidAuctionResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.auction'
    # initial_data = test_insider_auction_data
    initial_bids = [
        {
            "tenderers": [
                test_organization
            ],
            'qualified': True,
            "eligible": True,
            'status' : 'draft'
        }
        for i in range(3)
    ]

    test_post_auction_all_draft_bids = snitch(post_auction_all_draft_bids)


class InsiderAuctionSameValueAuctionResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.auction'
    initial_bids = [
        {
            "tenderers": [
                test_financial_organization
            ],
            'qualified': True,
            'eligible': True
        }
        for i in range(3)
    ]

    test_post_auction_auction_not_changed = snitch(post_auction_auction_not_changed)
    test_post_auction_auction_reversed = snitch(post_auction_auction_reversed)


class InsiderAuctionNoBidsResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.auction'

    test_post_auction_zero_bids = snitch(post_auction_no_bids)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InsiderAuctionAuctionResourceTest))
    suite.addTest(unittest.makeSuite(InsiderAuctionBidInvalidationAuctionResourceTest))
    suite.addTest(unittest.makeSuite(InsiderAuctionSameValueAuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
