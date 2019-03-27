# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.auction_blanks import (
    get_auction_auction_not_found,
    post_auction_auction_document,
    koatuu_additional_classification
)
from openprocurement.auctions.insider.tests.base import (
    BaseInsiderAuctionWebTest,
    test_bids,
    test_organization,
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
    post_auction_one_valid_bid,
    # InsiderAuctionDraftBidAuctionResourceTest
    post_auction_all_draft_bids,
    # InsiderAuctionSameValueAuctionResourceTest
    post_auction_auction_not_changed,
    post_auction_auction_reversed,
    # InsiderAuctionNoBidsResourceTest
    post_auction_no_bids,
    # InsiderAuctionBridgePatchPeriod
    set_auction_period,
    reset_auction_period
)
from openprocurement.auctions.core.tests.auctions import (
    AuctionRectificationPeriodTestMixin,
)


class InsiderAuctionAuctionResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids

    test_get_auction_auction_not_found = snitch(get_auction_auction_not_found)
    test_get_auction_auction = snitch(get_auction_auction)
    test_post_auction_auction = snitch(post_auction_auction)
    test_patch_auction_auction = snitch(patch_auction_auction)
    test_post_auction_auction_document = snitch(post_auction_auction_document)
    test_koatuu_additional_classification = snitch(koatuu_additional_classification)


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
    test_post_auction_one_valid_bid = snitch(post_auction_one_valid_bid)


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
            'status': 'draft'
        }
        for i in range(3)
    ]

    test_post_auction_all_draft_bids = snitch(post_auction_all_draft_bids)


class InsiderAuctionSameValueAuctionResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.auction'
    initial_bids = [
        {
            "tenderers": [
                test_organization
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


class InsiderAuctionRectificationPeriodTest(BaseInsiderAuctionWebTest, AuctionRectificationPeriodTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_bids


class InsiderAuctionBridgePatchPeriod(BaseInsiderAuctionWebTest):
    initial_status = 'active.tendering'

    test_set_auction_period = snitch(set_auction_period)
    test_reset_auction_period = snitch(reset_auction_period)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(InsiderAuctionAuctionResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionBidInvalidationAuctionResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionDraftBidAuctionResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionSameValueAuctionResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionNoBidsResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionRectificationPeriodTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionBridgePatchPeriod))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
