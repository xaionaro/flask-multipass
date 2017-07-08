# This file is part of Flask-Multipass.
# Copyright (C) 2015 - 2017 CERN
#
# Flask-Multipass is free software; you can redistribute it
# and/or modify it under the terms of the Revised BSD License.

from __future__ import unicode_literals

from cas_client import CASClient
from flask import current_app, url_for, session, request, redirect

from flask_multipass.auth import AuthProvider
from flask_multipass.data import AuthInfo, IdentityInfo
from flask_multipass.exceptions import MultipassException, AuthenticationFailed, IdentityRetrievalFailed
from flask_multipass.identity import IdentityProvider
from flask_multipass.util import login_view

import sys

class CASAuthProvider(AuthProvider):
    """Provides authentication using CAS

    The type name to instantiate this provider is *cas*.
    """

    def __init__(self, *args, **kwargs):
        super(CASAuthProvider, self).__init__(*args, **kwargs)
        self.settings.setdefault('callback_uri', '/cas_auth/{}'.format(self.name))
        if not self.settings.get('cas_url_base'):
            raise MultipassException("`cas_url_base` must be specified in the provider settings")
        self.cas_client = CASClient(self.settings['cas_url_base'], auth_prefix='')
        self.cas_endpoint = '_flaskmultipass_cas_' + self.name
        current_app.add_url_rule(self.settings['callback_uri'], self.cas_endpoint,
                                 self._authorize_callback, methods=('GET', 'POST'))

    @property
    def cas_callback_url(self):
        return request.url_root + self.settings['callback_uri']

    def initiate_external_login(self):
        cas_login_url = self.cas_client.get_login_url(service_url=self.cas_callback_url)
        return redirect(cas_login_url)

    def process_logout(self, return_url):
        cas_logout_url = self.cas_client.get_logout_url(service_url=self.cas_callback_url)
        return redirect(cas_logout_url)

    def _make_auth_info(self, resp):
        return AuthInfo(self, token=resp[self.settings['token_field']])

    @login_view
    def _authorize_callback(self):
        ticket = request.args.get('ticket')

        if not ticket:
            raise AuthenticationFailed('ticket is not provided')

        cas_response = self.cas_client.perform_service_validate(
            ticket=ticket,
            service_url=self.cas_callback_url,
            )

        if cas_response and cas_response.success:
            auth_info = cas_response.attributes
            auth_info['_username'] = cas_response.user
            return self.multipass.handle_auth_success(AuthInfo(self, **auth_info))

        raise AuthenticationFailed("CAS result: Access denied")


class CASIdentityProvider(IdentityProvider):
    """Provides identity information using CAS.

    The type name to instantiate this provider is *cas*.
    """

    #: If the provider supports getting identity information based from
    #: an identifier
    supports_get = False

    def __init__(self, *args, **kwargs):
        super(CASIdentityProvider, self).__init__(*args, **kwargs)

    def get_identity_from_auth(self, auth_info):
        identifier = auth_info.data.get('_username')
        if not identifier:
            raise IdentityRetrievalFailed("Identifier missing in CAS response")
        return IdentityInfo(self, identifier=identifier, **auth_info.data)

