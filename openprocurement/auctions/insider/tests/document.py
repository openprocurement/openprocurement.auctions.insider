# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.dgf.models import DGF_PLATFORM_LEGAL_DETAILS_FROM
from openprocurement.auctions.insider.tests.base import BaseInsiderAuctionWebTest
from openprocurement.auctions.core.tests.base import snitch
from openprocurement.auctions.core.tests.document import (
    AuctionDocumentResourceTestMixin,
    AuctionDocumentWithDSResourceTestMixin
)
from openprocurement.auctions.core.tests.blanks.document_blanks import (
    # InsiderAuctionDocumentWithDSResourceTest
    create_auction_document_vdr,
    put_auction_document_vdr,
)


class InsiderAuctionDocumentResourceTest(BaseInsiderAuctionWebTest, AuctionDocumentResourceTestMixin):
    docservice = False
    dgf_platform_legal_details_from = DGF_PLATFORM_LEGAL_DETAILS_FROM


class InsiderAuctionDocumentWithDSResourceTest(InsiderAuctionDocumentResourceTest, AuctionDocumentWithDSResourceTestMixin):
    docservice = True

    test_create_auction_document_vdr = snitch(create_auction_document_vdr)
    test_put_auction_document_vdr = snitch(put_auction_document_vdr)


def suite():
    tests = unittest.TestSuite()
    tests.addTest(unittest.makeSuite(InsiderAuctionDocumentResourceTest))
    tests.addTest(unittest.makeSuite(InsiderAuctionDocumentWithDSResourceTest))
    return tests


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
