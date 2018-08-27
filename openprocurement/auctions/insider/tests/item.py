# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.insider.tests.base import (
    BaseInsiderAuctionWebTest,
)
from openprocurement.auctions.core.tests.items import (
    DgfItemsResourceTestMixin,
)


class InsiderItemsResourceTest(BaseInsiderAuctionWebTest, DgfItemsResourceTestMixin):
    initial_status = 'active.tendering'


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DgfInsiderItemsResourceTest))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
