# -*- coding: utf-8 -*-
import unittest
from datetime import timedelta

from openprocurement.api.models import get_now
from openprocurement.auctions.insider.tests.base import (
    BaseInsiderAuctionWebTest, test_financial_bids,
)
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.blanks.chronograph_blanks import (
    # InsiderAuctionSwitchAuctionResourceTest
    switch_to_auction,
    # InsiderAuctionDontSwitchSuspendedAuction2ResourceTest
    switch_suspended_auction_to_auction,
)
from openprocurement.auctions.core.plugins.awarding.v3.tests.chronograph import (
    AuctionAwardSwitchResourceTestMixin,
    AuctionDontSwitchSuspendedAuctionResourceTestMixin
)
from openprocurement.auctions.core.plugins.awarding.v3.tests.blanks.chronograph_blanks import (
    # AuctionAwardSwitch2ResourceTest
    switch_verification_to_unsuccessful_2,
    switch_active_to_unsuccessful_2,
)


from openprocurement.auctions.insider.tests.blanks.chronograph_blanks import (
    # InsiderAuctionAuctionPeriodResourceTest
    set_auction_period,
    reset_auction_period
)


class InsiderAuctionSwitchAuctionResourceTest(BaseInsiderAuctionWebTest):
    initial_bids = test_financial_bids

    test_switch_to_auction = snitch(switch_to_auction)


class InsiderAuctionAuctionPeriodResourceTest(BaseInsiderAuctionWebTest):
    initial_bids = test_financial_bids

    test_set_auction_period = snitch(set_auction_period)
    test_reset_auction_period = snitch(reset_auction_period)


class InsiderAuctionAwardSwitchResourceTest(BaseInsiderAuctionWebTest, AuctionAwardSwitchResourceTestMixin):
    initial_status = 'active.auction'
    initial_bids = test_financial_bids

    def setUp(self):
        super(InsiderAuctionAwardSwitchResourceTest, self).setUp()
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('auction', ''))
        now = get_now()
        response = self.app.get('/auctions/{}'.format(self.auction_id))
        self.assertEqual(response.status, '200 OK')
        auction = response.json['data']
        value_threshold = auction['value']['amount'] + auction['minimalStep']['amount']

        now = get_now()
        auction_result = {
            'bids': [
                {
                    "id": b['id'],
                    "date": (now - timedelta(seconds=i)).isoformat(),
                    "value": {"amount": value_threshold * 2},

                }
                for i, b in enumerate(self.initial_bids)
            ]
        }

        response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': auction_result})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertEqual('active.qualification', auction["status"])
        self.award = self.first_award = auction['awards'][0]
        self.second_award = auction['awards'][1]
        self.award_id = self.first_award_id = self.first_award['id']
        self.second_award_id = self.second_award['id']
        self.app.authorization = authorization


class InsiderAuctionAwardSwitch2ResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.auction'
    initial_bids = test_financial_bids

    def setUp(self):
        super(InsiderAuctionAwardSwitch2ResourceTest, self).setUp()
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('auction', ''))

        response = self.app.get('/auctions/{}'.format(self.auction_id))
        self.assertEqual(response.status, '200 OK')
        auction = response.json['data']
        value_threshold = auction['value']['amount'] + auction['minimalStep']['amount']

        now = get_now()

        auction_result = {
            'bids': [
                {
                    "id": b['id'],
                    "date": (now - timedelta(seconds=i)).isoformat(),
                    "value": {"amount": 101 * (i + 1)},

                }
                for i, b in enumerate(self.initial_bids)
            ]
        }

        response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': auction_result})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertEqual('active.qualification', auction["status"])
        self.award = self.first_award = auction['awards'][0]
        # self.second_award = auction['awards'][1]
        self.award_id = self.first_award_id = self.first_award['id']
        # self.second_award_id = self.second_award['id']
        self.app.authorization = authorization

    test_switch_verification_to_unsuccessful = snitch(switch_verification_to_unsuccessful_2)
    test_switch_active_to_unsuccessful = snitch(switch_active_to_unsuccessful_2)


class InsiderAuctionDontSwitchSuspendedAuction2ResourceTest(BaseInsiderAuctionWebTest):
    initial_bids = test_financial_bids

    test_switch_suspended_auction_to_auction = snitch(switch_suspended_auction_to_auction)


class InsiderAuctionDontSwitchSuspendedAuctionResourceTest(BaseInsiderAuctionWebTest,
                                                           AuctionDontSwitchSuspendedAuctionResourceTestMixin):
    initial_status = 'active.auction'
    initial_bids = test_financial_bids

    def setUp(self):
        super(InsiderAuctionDontSwitchSuspendedAuctionResourceTest, self).setUp()
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('auction', ''))
        now = get_now()
        response = self.app.get('/auctions/{}'.format(self.auction_id))
        self.assertEqual(response.status, '200 OK')
        auction = response.json['data']
        value_threshold = auction['value']['amount'] + auction['minimalStep']['amount']

        now = get_now()
        auction_result = {
            'bids': [
                {
                    "id": b['id'],
                    "date": (now - timedelta(seconds=i)).isoformat(),
                    "value": {"amount": value_threshold * 2},

                }
                for i, b in enumerate(self.initial_bids)
            ]
        }

        response = self.app.post_json('/auctions/{}/auction'.format(self.auction_id), {'data': auction_result})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        auction = response.json['data']
        self.assertEqual('active.qualification', auction["status"])
        self.award = self.first_award = auction['awards'][0]
        self.second_award = auction['awards'][1]
        self.award_id = self.first_award_id = self.first_award['id']
        self.second_award_id = self.second_award['id']
        self.app.authorization = authorization


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(InsiderAuctionSwitchAuctionResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionAuctionPeriodResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionAwardSwitchResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionAwardSwitch2ResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionDontSwitchSuspendedAuction2ResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionDontSwitchSuspendedAuctionResourceTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
