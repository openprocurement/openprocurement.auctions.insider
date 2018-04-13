import unittest

from uuid import uuid4
from openprocurement.api.utils import get_now

from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.plugins.awarding.v3.tests.migration import (
    MigrateAwardingV2toV3Mixin
)
from openprocurement.auctions.insider.tests.base import (
    test_financial_bids as test_bids
)
from openprocurement.auctions.insider.tests.base import (
    BaseInsiderAuctionWebTest,
)
from openprocurement.auctions.insider.migration import (
    migrate_data,
    set_db_schema_version
)
from openprocurement.auctions.insider.tests.blanks.migration_blanks import (
    migrate_pendingVerification_pending_one_bid,
    migrate_pendingPayment_active_one_bid
)


class MigrateTestFrom2To3WithTwoBids(BaseInsiderAuctionWebTest, MigrateAwardingV2toV3Mixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    @staticmethod
    def migrate_data(registry, destination=None):
        return migrate_data(registry, destination)

    def setUp(self):
        super(MigrateTestFrom2To3WithTwoBids, self).setUp()
        migrate_data(self.app.app.registry)
        set_db_schema_version(self.db, 0)

    test_migrate_pendingVerification_pending_one_bid = snitch(
        migrate_pendingVerification_pending_one_bid
    )
    test_migrate_pendingPayment_active_one_bid = snitch(
        migrate_pendingVerification_pending_one_bid
    )


class MigrateTestFrom2To3Schema(BaseInsiderAuctionWebTest):
    initial_status = 'active.awarded'
    initial_bids = test_bids

    def test_migrate_one_pending_contract(self):
        auction = self.db.get(self.auction_id)
        del auction['awardPeriod']['endDate']
        award = {
            'id': uuid4().hex,
            "date": get_now().isoformat(),
            "bid_id": auction['bids'][1]['id'],
            'suppliers': auction['bids'][1]['tenderers'],
            'value': auction['value'],
            "status": "active",
            "complaintPeriod": {
                "startDate": get_now().isoformat(),
            },
            "signingPeriod": {
                "startDate": get_now().isoformat(),
                "endDate": get_now().isoformat(),
            }
        }
        contract = {
            'id': uuid4().hex,
            'awardID': award['id'],
            'suppliers': award['suppliers'],
            'value': award['value'],
            'date': get_now().isoformat(),
            'status': 'pending',
            'items': auction['items'],
            'contractID': '{}-{}'.format(
                auction['auctionID'],
                len(auction.get('contracts', [])) + 1
            ),
            'signingPeriod': award['signingPeriod']
        }

        auction['awards'] = [award]
        auction['contracts'] = [contract]
        auction.update(auction)
        self.db.save(auction)
        migrate_data(self.app.app.registry, 2)

        auction = self.app.get('/auctions/{}'.format(self.auction_id)).json['data']
        self.assertEqual(auction['awards'][0]['status'], 'active')
        self.assertIn('endDate', auction['awardPeriod'])
        self.assertIn('endDate', auction['awards'][0]['complaintPeriod'])
        self.assertEqual(auction['status'], 'active.awarded')

        response = self.app.post('/auctions/{}/contracts/{}/documents'.format(
            self.auction_id, contract['id']), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        response = self.app.patch_json('/auctions/{}/contracts/{}'.format(self.auction_id, auction['contracts'][0]['id']),
                                       {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'active')

        response = self.app.get('/auctions/{}'.format(self.auction_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['status'], u'complete')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MigrateTestFrom2To3WithTwoBids))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
