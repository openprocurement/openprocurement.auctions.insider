# -*- coding: utf-8 -*-
import unittest

from openprocurement.auctions.core.tests.question import AuctionQuestionResourceTestMixin

from openprocurement.auctions.insider.tests.base import BaseInsiderAuctionWebTest


class InsiderAuctionQuestionResourceTest(BaseInsiderAuctionWebTest, AuctionQuestionResourceTestMixin):
    pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InsiderAuctionQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
