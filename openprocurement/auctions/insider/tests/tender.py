# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

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

from openprocurement.auctions.core.constants import DGF_ELIGIBILITY_CRITERIA

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
    eligibility_criteria = DGF_ELIGIBILITY_CRITERIA
    test_financial_organization = test_financial_organization

    test_create_auction_invalid = snitch(create_auction_invalid)
    test_create_auction_auctionPeriod = snitch(create_auction_auctionPeriod)
    test_create_auction_generated = snitch(create_auction_generated)
    test_create_auction = snitch(create_auction)


class InsiderAuctionProcessTest(BaseInsiderAuctionWebTest):
    def test_auctionParameters(self):
        data = deepcopy(self.initial_data)
        self.app.authorization = ('Basic', ('broker', ''))

        # Create auction with invalid auctionParameters
        data['auctionParameters'] = {'dutchSteps': 42, 'type': 'dutch'}
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {
                "location": "body", "name": "auctionParameters", "description": {
                    "type": ["Value must be one of ['insider']."],
                    "dutchSteps": ["Value must be one of [10, 20, 30, 40, 50, 60, 70, 80, 90, 99, 100]."]
                }
            }
        ])

        data['auctionParameters'] = {'dutchSteps': 112, 'type': 'insider'}
        response = self.app.post_json('/auctions', {'data': data}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'], [
            {
                "location": "body", "name": "auctionParameters", "description": {
                    "dutchSteps": ["Value must be one of [10, 20, 30, 40, 50, 60, 70, 80, 90, 99, 100]."]
                }
            }
        ])

        # Create auction with default auctionParameters values
        del data['auctionParameters']
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['auctionParameters']['dutchSteps'], 80)
        self.assertEqual(response.json['data']['auctionParameters']['type'], 'insider')

        data['auctionParameters'] = {'dutchSteps': 70, 'type': 'insider'}
        response = self.app.post_json('/auctions', {'data': data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['auctionParameters']['dutchSteps'], 70)
        self.assertEqual(response.json['data']['auctionParameters']['type'], 'insider')
        auction_id = self.auction_id = response.json['data']['id']
        owner_token = response.json['access']['token']


        #  Patch auctionParameters (Not allowed)
        response = self.app.patch_json('/auctions/{}?acc_token={}'.format(auction_id, owner_token), {
            'data': {'auctionParameters': {'dutchSteps': 50, 'type': 'insider'}}
        })
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['auctionParameters']['dutchSteps'], 70)
        self.assertEqual(response.json['data']['auctionParameters']['type'], 'insider')

        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/auctions/{}'.format(auction_id), {
            'data': {'auctionParameters': {'dutchSteps': 99, 'type': 'insider'}}
        })
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['auctionParameters']['dutchSteps'], 99)
        self.assertEqual(response.json['data']['auctionParameters']['type'], 'insider')

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
