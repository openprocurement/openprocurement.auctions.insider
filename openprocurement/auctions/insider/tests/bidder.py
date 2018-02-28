# -*- coding: utf-8 -*-
import unittest
from urllib import unquote
from base64 import b64decode
from libnacl.sign import Signer, Verifier
from openprocurement.auctions.insider.tests.base import (
    BaseInsiderAuctionWebTest, test_financial_bids,
    test_insider_auction_data, test_financial_organization,
)

class InsiderAuctionBidderResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.tendering'

    def test_create_auction_bidder_invalid(self):
        response = self.app.post_json('/auctions/some_id/bids',
            {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'auction_id'}
        ])

        request_path = '/auctions/{}/bids'.format(self.auction_id)
        response = self.app.post(request_path, 'data', status=415)
        self.assertEqual(response.status, '415 Unsupported Media Type')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description':
                u"Content-Type header should be one of ['application/json']", u'location': u'header', u'name': u'Content-Type'}
        ])

        response = self.app.post(
            request_path, 'data', content_type='application/json', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Expecting value: line 1 column 1 (char 0)',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, 'data', status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(
            request_path, {'not_data': {}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Data not available',
                u'location': u'body', u'name': u'data'}
        ])

        response = self.app.post_json(request_path, {'data': {
                                      'invalid_field': 'invalid_value'}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Rogue field', u'location':
                u'body', u'name': u'invalid_field'}
        ])

        response = self.app.post_json(request_path, {
                                      'data': {'tenderers': [{'identifier': 'invalid_value'}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': {u'identifier': [
                u'Please use a mapping for this field or Identifier instance instead of unicode.']}, u'location': u'body', u'name': u'tenderers'}
        ])

        response = self.app.post_json(request_path, {
                                      'data': {'tenderers': [{'identifier': {}}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertIn({u"location": u"body", u"name": u"qualified", u"description": [u"This field is required."]}, response.json['errors'])
        self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'eligible'}, response.json['errors'])
        self.assertIn({u'description': [{u'contactPoint': [u'This field is required.'], u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.']}, u'name': [u'This field is required.'], u'address': [u'This field is required.']}], u'location': u'body', u'name': u'tenderers'}, response.json['errors'])

        response = self.app.post_json(request_path, {'data': {'tenderers': [{
            'name': 'name', 'identifier': {'uri': 'invalid_value'}}]}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertIn({u"location": u"body", u"name": u"qualified", u"description": [u"This field is required."]}, response.json['errors'])
        self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'eligible'}, response.json['errors'])
        self.assertIn({u'description': [{u'contactPoint': [u'This field is required.'], u'identifier': {u'scheme': [u'This field is required.'], u'id': [u'This field is required.'], u'uri': [u'Not a well formed URL.']}, u'address': [u'This field is required.']}], u'location': u'body', u'name': u'tenderers'}, response.json['errors'])

        if self.initial_organization == test_financial_organization:
            response = self.app.post_json(request_path, {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json(request_path, {'data': {'tenderers': [self.initial_organization], 'qualified': True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')

        if self.initial_organization == test_financial_organization:
            response = self.app.post_json(request_path, {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500, 'valueAddedTaxIncluded': False}, 'qualified': True, 'eligible': True}}, status=422)
        else:
            response = self.app.post_json(request_path, {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500, 'valueAddedTaxIncluded': False}, 'qualified': True}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertIn({u'description': [u'valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of auction'], u'location': u'body', u'name': u'value'}, response.json['errors'])

        if self.initial_organization == test_financial_organization:
            response = self.app.post_json(request_path, {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500, 'currency': "USD"}, 'qualified': True, 'eligible': True}}, status=422)
        else:
            response = self.app.post_json(request_path, {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500, 'currency': "USD"}, 'qualified': True}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertIn({u'description': [u'currency of bid should be identical to currency of value of auction'], u'location': u'body', u'name': u'value'}, response.json['errors'])

        if self.initial_organization == test_financial_organization:
            response = self.app.post_json(request_path, {'data': {'tenderers': self.initial_organization, "value": {"amount": 500}, 'qualified': True, 'eligible': True}}, status=422)
        else:
            response = self.app.post_json(request_path, {'data': {'tenderers': self.initial_organization, "value": {"amount": 500}, 'qualified': True}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        if self.initial_organization == test_financial_organization:
            self.assertIn({u'description': u"invalid literal for int() with base 10: 'additionalIdentifiers'", u'location': u'body', u'name': u'data'}, response.json['errors'])
        else:
            self.assertIn({u'description': u"invalid literal for int() with base 10: 'contactPoint'", u'location': u'body', u'name': u'data'}, response.json['errors'])

        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}}}, status=422)
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}}}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertIn({u'description': [u'This field is required.'], u'location': u'body', u'name': u'qualified'}, response.json['errors'])

    def test_create_auction_bidder(self):
        dateModified = self.db.get(self.auction_id).get('dateModified')

        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        self.assertEqual(bidder['tenderers'][0]['name'], self.initial_organization['name'])
        self.assertIn('id', bidder)
        self.assertIn(bidder['id'], response.headers['Location'])

        self.assertEqual(self.db.get(self.auction_id).get('dateModified'), dateModified)

        self.set_status('complete')

        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True, 'eligible': True}}, status=403)
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "value": {"amount": 500}, 'qualified': True}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (complete) auction status")

    def test_create_auction_bidder_without_value(self):
        dateModified = self.db.get(self.auction_id).get('dateModified')

        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        self.assertEqual(bidder['tenderers'][0]['name'], self.initial_organization['name'])
        self.assertIn('id', bidder)
        self.assertIn(bidder['id'], response.headers['Location'])

        self.assertEqual(self.db.get(self.auction_id).get('dateModified'), dateModified)

        self.set_status('complete')

        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}}, status=403)
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add bid in current (complete) auction status")

    def test_patch_auction_bidder(self):
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "status": "draft", 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], "status": "draft", 'qualified': True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']

        response = self.app.patch_json('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), {"data": {'tenderers': [{"name": u"Державне управління управлінням справами"}]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['date'], bidder['date'])
        self.assertNotEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        response = self.app.patch_json('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), {"data": {'tenderers': [self.initial_organization]}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['date'], bidder['date'])
        self.assertEqual(response.json['data']['tenderers'][0]['name'], bidder['tenderers'][0]['name'])

        response = self.app.patch_json('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), {"data": {"status": "active"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["status"], "active")

        response = self.app.patch_json('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), {"data": {"status": "draft"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can\'t update bid to (draft) status")

        response = self.app.patch_json('/auctions/{}/bids/some_id'.format(self.auction_id), {"data":{'tenderers': [self.initial_organization]}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.patch_json('/auctions/some_id/bids/some_id', {"data": {'tenderers': [self.initial_organization]}}, status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'auction_id'}
        ])

        self.set_status('complete')

        response = self.app.patch_json('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), {"data": {'tenderers': [self.initial_organization]}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update bid in current (complete) auction status")

    def test_get_auction_bidder(self):
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']
        bid_token = response.json['access']['token']

        response = self.app.get('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid in current (active.tendering) auction status")

        response = self.app.get('/auctions/{}/bids/{}?acc_token={}'.format(self.auction_id, bidder['id'], bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'], bidder)
        bidder_data = response.json['data']
        self.assertIn(u'participationUrl', bidder_data)

        self.set_status('active.qualification')

        response = self.app.get('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        bidder_data = response.json['data']
        #self.assertIn(u'participationUrl', bidder_data)
        #bidder_data.pop(u'participationUrl')
        self.assertEqual(bidder_data, bidder)

        response = self.app.get('/auctions/{}/bids/some_id'.format(self.auction_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.get('/auctions/some_id/bids/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'auction_id'}
        ])

        response = self.app.delete('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        # self.assertEqual(response.json['errors'][0]["description"], "Can't delete bid in current (active.qualification) auction status")

    def test_bid_id_signature_verified_active_bid(self):
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True}})
        bidder = response.json['data']
        signature = bidder['participationUrl']
        before, sep, sig = signature.partition('signature=')
        sig = b64decode(unquote(str(sig)))
        signer = Signer('fe3b3b5999a08e68dfe62687c2ae147f62712ceace58c1ffca8ea819eabcb5d1'.decode('hex'))
        ver = Verifier(signer.hex_vk())
        verified = ver.verify(sig + str('{}_{}'.format(self.auction_id, bidder['id'])))
        self.assertEqual(verified, '{}_{}'.format(self.auction_id, bidder['id']))

    def test_bid_id_signature_verified_draft_active_bid(self):
        if self.initial_organization == test_financial_organization:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True, 'status': "draft"}})
        else:
            response = self.app.post_json('/auctions/{}/bids'.format(
                self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True}})
        bidder = response.json['data']
        response = self.app.patch_json('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), {'data': {'status': 'active'}})
        signature = response.json['data']['participationUrl']
        before, sep, sig = signature.partition('signature=')
        sig = b64decode(unquote(sig))
        signer = Signer('fe3b3b5999a08e68dfe62687c2ae147f62712ceace58c1ffca8ea819eabcb5d1'.decode('hex'))
        ver = Verifier(signer.hex_vk())
        verified = ver.verify(sig + str('{}_{}'.format(self.auction_id, bidder['id'])))
        self.assertEqual(verified, '{}_{}'.format(self.auction_id, bidder['id']))

    def test_delete_auction_bidder(self):
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}})

        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']

        response = self.app.delete('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        # self.assertEqual(response.status, '200 OK')
        # self.assertEqual(response.content_type, 'application/json')
        # self.assertEqual(response.json['data'], bidder)

        # revisions = self.db.get(self.auction_id).get('revisions')
        # self.assertTrue(any([i for i in revisions[-2][u'changes'] if i['op'] == u'remove' and i['path'] == u'/bids']))
        # self.assertTrue(any([i for i in revisions[-1][u'changes'] if i['op'] == u'add' and i['path'] == u'/bids']))

        response = self.app.delete('/auctions/{}/bids/some_id'.format(self.auction_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.delete('/auctions/some_id/bids/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'auction_id'}
        ])

    def test_get_auction_auctioners(self):
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']

        response = self.app.get('/auctions/{}/bids'.format(self.auction_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bids in current (active.tendering) auction status")

        self.set_status('active.qualification')

        response = self.app.get('/auctions/{}/bids'.format(self.auction_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data'][0], bidder)

        response = self.app.get('/auctions/some_id/bids', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'auction_id'}
        ])

    def test_bid_Administrator_change(self):
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bidder = response.json['data']

        self.app.authorization = ('Basic', ('administrator', ''))
        response = self.app.patch_json('/auctions/{}/bids/{}'.format(self.auction_id, bidder['id']), {"data": {
            'tenderers': [{"identifier": {"id": "00000000"}}]
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["tenderers"][0]["identifier"]["id"], "00000000")


class InsiderAuctionBidderDocumentResourceTest(BaseInsiderAuctionWebTest):
    initial_status = 'active.tendering'

    def setUp(self):
        super(InsiderAuctionBidderDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']

    def test_not_found(self):
        response = self.app.post('/auctions/some_id/bids/some_id/documents', status=404, upload_files=[
                                 ('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'auction_id'}
        ])

        response = self.app.post('/auctions/{}/bids/some_id/documents'.format(self.auction_id), status=404, upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.post('/auctions/{}/bids/{}/documents'.format(self.auction_id, self.bid_id), status=404, upload_files=[
                                 ('invalid_value', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.get('/auctions/some_id/bids/some_id/documents', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'auction_id'}
        ])

        response = self.app.get('/auctions/{}/bids/some_id/documents'.format(self.auction_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.get('/auctions/some_id/bids/some_id/documents/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'auction_id'}
        ])

        response = self.app.get('/auctions/{}/bids/some_id/documents/some_id'.format(self.auction_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.get('/auctions/{}/bids/{}/documents/some_id'.format(self.auction_id, self.bid_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'document_id'}
        ])

        response = self.app.put('/auctions/some_id/bids/some_id/documents/some_id', status=404,
                                upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'auction_id'}
        ])

        response = self.app.put('/auctions/{}/bids/some_id/documents/some_id'.format(self.auction_id), status=404, upload_files=[
                                ('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.put('/auctions/{}/bids/{}/documents/some_id'.format(
            self.auction_id, self.bid_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

        self.app.authorization = ('Basic', ('invalid', ''))
        response = self.app.put('/auctions/{}/bids/{}/documents/some_id'.format(
            self.auction_id, self.bid_id), status=404, upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'document_id'}
        ])

    def test_create_auction_bidder_document(self):
        response = self.app.post('/auctions/{}/bids/{}/documents'.format(
            self.auction_id, self.bid_id), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        response = self.app.get('/auctions/{}/bids/{}/documents'.format(self.auction_id, self.bid_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid documents in current (active.tendering) auction status")

        response = self.app.get('/auctions/{}/bids/{}/documents?acc_token={}'.format(self.auction_id, self.bid_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/auctions/{}/bids/{}/documents?all=true&acc_token={}'.format(self.auction_id, self.bid_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?download=some_id&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}'.format(
            self.auction_id, self.bid_id, doc_id, key), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) auction status")

        if self.docservice:
            response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
                self.auction_id, self.bid_id, doc_id, key, self.bid_token))
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
                self.auction_id, self.bid_id, doc_id, key, self.bid_token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 7)
            self.assertEqual(response.body, 'content')

        response = self.app.get('/auctions/{}/bids/{}/documents/{}'.format(
            self.auction_id, self.bid_id, doc_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) auction status")

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        self.set_status('active.awarded', {'status': 'active.tendering'})

        response = self.app.post('/auctions/{}/bids/{}/documents'.format(
            self.auction_id, self.bid_id), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn("Document can be added only during the tendering period: from", response.json['errors'][0]["description"])

        self.set_status('active.awarded')

        response = self.app.post('/auctions/{}/bids/{}/documents'.format(
            self.auction_id, self.bid_id), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.awarded) auction status")

        response = self.app.get('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        if self.docservice:
            self.assertIn('http://localhost/get/', response.json['data']['url'])
            self.assertIn('Signature=', response.json['data']['url'])
            self.assertIn('KeyID=', response.json['data']['url'])
            self.assertNotIn('Expires=', response.json['data']['url'])
        else:
            self.assertIn('download=', response.json['data']['url'])

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, key, self.bid_token))
        if self.docservice:
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 7)
            self.assertEqual(response.body, 'content')

    def test_put_auction_bidder_document(self):
        response = self.app.post('/auctions/{}/bids/{}/documents'.format(
            self.auction_id, self.bid_id), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id),
                                status=404,
                                upload_files=[('invalid_name', 'name.doc', 'content')])
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'body', u'name': u'file'}
        ])

        response = self.app.put('/auctions/{}/bids/{}/documents/{}'.format(
            self.auction_id, self.bid_id, doc_id), upload_files=[('file', 'name.doc', 'content2')])
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, key, self.bid_token))
        if self.docservice:
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content2')

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put('/auctions/{}/bids/{}/documents/{}'.format(
            self.auction_id, self.bid_id, doc_id), 'content3', content_type='application/msword')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, key, self.bid_token))
        if self.docservice:
            self.assertEqual(response.status, '302 Moved Temporarily')
            self.assertIn('http://localhost/get/', response.location)
            self.assertIn('Signature=', response.location)
            self.assertIn('KeyID=', response.location)
            self.assertIn('Expires=', response.location)
        else:
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.content_type, 'application/msword')
            self.assertEqual(response.content_length, 8)
            self.assertEqual(response.body, 'content3')

        self.set_status('active.awarded')

        response = self.app.put('/auctions/{}/bids/{}/documents/{}'.format(
            self.auction_id, self.bid_id, doc_id), upload_files=[('file', 'name.doc', 'content3')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.awarded) auction status")

    def test_patch_auction_bidder_document(self):
        response = self.app.post('/auctions/{}/bids/{}/documents'.format(
            self.auction_id, self.bid_id), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.patch_json('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id), {"data": {
            "documentOf": "lot"
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'This field is required.'], u'location': u'body', u'name': u'relatedItem'},
        ])

        response = self.app.patch_json('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id), {"data": {
            "documentOf": "lot",
            "relatedItem": '0' * 32
        }}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'relatedItem should be one of lots'], u'location': u'body', u'name': u'relatedItem'}
        ])

        response = self.app.patch_json('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id), {"data": {"description": "document description"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('document description', response.json["data"]["description"])

        self.set_status('active.awarded')

        response = self.app.patch_json('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.awarded) auction status")

    def test_create_auction_bidder_document_nopending(self):
        response = self.app.post_json('/auctions/{}/bids'.format(
            self.auction_id), {'data': {'tenderers': [self.initial_organization], 'qualified': True, 'eligible': True}})
        bid = response.json['data']
        bid_id = bid['id']

        response = self.app.post('/auctions/{}/bids/{}/documents'.format(
            self.auction_id, bid_id), upload_files=[('file', 'name.doc', 'content')])
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        self.set_status('active.qualification')

        response = self.app.patch_json('/auctions/{}/bids/{}/documents/{}'.format(
            self.auction_id, bid_id, doc_id), {"data": {"description": "document description"}}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document because award of bid is not in pending state")

        response = self.app.put('/auctions/{}/bids/{}/documents/{}'.format(
            self.auction_id, bid_id, doc_id), 'content3', content_type='application/msword', status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document because award of bid is not in pending state")

        response = self.app.post('/auctions/{}/bids/{}/documents'.format(
            self.auction_id, bid_id), upload_files=[('file', 'name.doc', 'content')], status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document because award of bid is not in pending state")


class InsiderAuctionBidderDocumentWithDSResourceTest(InsiderAuctionBidderDocumentResourceTest):
    docservice = True

    def test_create_auction_bidder_document_json(self):
        response = self.app.post_json('/auctions/{}/bids/{}/documents'.format(self.auction_id, self.bid_id),
            {'data': {
                'title': 'name.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])
        self.assertEqual('name.doc', response.json["data"]["title"])
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

        response = self.app.get('/auctions/{}/bids/{}/documents'.format(self.auction_id, self.bid_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid documents in current (active.tendering) auction status")

        response = self.app.get('/auctions/{}/bids/{}/documents?acc_token={}'.format(self.auction_id, self.bid_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/auctions/{}/bids/{}/documents?all=true&acc_token={}'.format(self.auction_id, self.bid_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"][0]["id"])
        self.assertEqual('name.doc', response.json["data"][0]["title"])

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?download=some_id&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, self.bid_token), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}'.format(
            self.auction_id, self.bid_id, doc_id, key), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) auction status")

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)

        response = self.app.get('/auctions/{}/bids/{}/documents/{}'.format(
            self.auction_id, self.bid_id, doc_id), status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't view bid document in current (active.tendering) auction status")

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.post_json('/auctions/{}/bids/{}/documents'.format(self.auction_id, self.bid_id),
            {'data': {
                'title': 'name.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn(response.json["data"]['id'], response.headers['Location'])
        self.assertEqual('name.doc', response.json["data"]["title"])

        self.set_status('active.awarded')

        response = self.app.post_json('/auctions/{}/bids/{}/documents'.format(self.auction_id, self.bid_id),
            {'data': {
                'title': 'name.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.awarded) auction status")

        response = self.app.get('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id))
        self.assertEqual(response.status, '200 OK')
        self.assertIn('http://localhost/get/', response.json['data']['url'])
        self.assertIn('Signature=', response.json['data']['url'])
        self.assertIn('KeyID=', response.json['data']['url'])
        self.assertNotIn('Expires=', response.json['data']['url'])

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?download={}&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)

    def test_put_auction_bidder_document_json(self):
        response = self.app.post_json('/auctions/{}/bids/{}/documents'.format(self.auction_id, self.bid_id),
            {'data': {
                'title': 'name.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        doc_id = response.json["data"]['id']
        self.assertIn(doc_id, response.headers['Location'])

        response = self.app.put_json('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id),
            {'data': {
                'title': 'name.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, self.bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        self.assertEqual('name.doc', response.json["data"]["title"])

        response = self.app.put_json('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id),
            {'data': {
                'title': 'name.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(doc_id, response.json["data"]["id"])
        key = response.json["data"]["url"].split('?')[-1]

        response = self.app.get('/auctions/{}/bids/{}/documents/{}?{}&acc_token={}'.format(
            self.auction_id, self.bid_id, doc_id, key, self.bid_token))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertIn('Expires=', response.location)

        self.set_status('active.awarded')

        response = self.app.put_json('/auctions/{}/bids/{}/documents/{}'.format(self.auction_id, self.bid_id, doc_id),
            {'data': {
                'title': 'name.doc',
                'url': self.generate_docservice_url(),
                'hash': 'md5:' + '0' * 32,
                'format': 'application/msword',
            }}, status=403)
        self.assertEqual(response.status, '403 Forbidden')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.awarded) auction status")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InsiderAuctionBidderResourceTest))
    suite.addTest(unittest.makeSuite(InsiderAuctionBidderDocumentResourceTest))
    suite.addTest(unittest.makeSuite(InsiderAuctionBidderDocumentWithDSResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
