import unittest
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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MigrateTestFrom2To3WithTwoBids))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
