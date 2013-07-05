#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import urllib
from tornado import escape, httpclient, auth
from tornado.web import asynchronous
from torext.handlers import BaseHandler
from torext import settings


class GithubMixin(auth.OAuth2Mixin):
    """Github authentication using API v3 and OAuth2."""
    _OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    _OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    _OAUTH_NO_CALLBACKS = False
    _API_URL = 'https://api.github.com'

    def get_auth_http_client(self):
        """Returns the AsyncHTTPClient instance to be used for auth requests.

        May be overridden by subclasses to use an http client other than
        the default.
        """
        return httpclient.AsyncHTTPClient()

    def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                               code, callback, extra_fields=None):
        http = self.get_auth_http_client()
        args = {
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        http.fetch(
            self._oauth_request_token_url(**args),
            self.async_callback(self._on_access_token, callback))

    def _on_access_token(self, callback, response):
        if response.error:
            logging.warning('Github auth error: %s' % str(response))
            callback(None)
            return

        args = escape.parse_qs_bytes(escape.native_str(response.body))
        logging.info('Got access token: %s', args)
        access_token = args['access_token'][0]
        token_type = args['token_type'][0]

        self.github_request(
            '/user',
            access_token=access_token,
            callback=self.async_callback(
                self._on_get_user_info, callback, access_token, token_type))

    def _on_get_user_info(self, callback, access_token, token_type, user):
        if user is None:
            callback(None)
            return

        user['access_token'] = access_token
        user['token_type'] = token_type
        callback(user)

    def github_request(self, path,
                       access_token=None,
                       data=None,
                       callback=None,
                       **kwargs):
        url = self._API_URL + path
        all_args = {}
        if access_token:
            all_args["access_token"] = access_token
            all_args.update(kwargs)

        if all_args:
            url += "?" + urllib.urlencode(all_args)
        callback = self.async_callback(self._on_github_request, callback)
        http = self.get_auth_http_client()
        if data is not None:
            http.fetch(url, method="POST", body=urllib.urlencode(data),
                       callback=callback)
        else:
            http.fetch(url, callback=callback)

    def _on_github_request(self, callback, response):
        if response.error:
            logging.warning("Error response %s fetching %s", response.error,
                            response.request.url)
            callback(None)
            return
        callback(escape.json_decode(response.body))


class HomeHandler(BaseHandler):
    def get(self):
        self.write('test')


class LoginHandler(BaseHandler, GithubMixin):
    @asynchronous
    def get(self):
        code = self.get_argument('code', None)
        if not code:
            self.authorize_redirect(
                redirect_uri=settings['GITHUB_REDIRECT_URI'],
                client_id=settings['GITHUB_CLIENT_ID'])
            return
        self.get_authenticated_user(
            redirect_uri=settings['GITHUB_REDIRECT_URI'],
            client_id=settings['GITHUB_CLIENT_ID'],
            client_secret=settings['GITHUB_CLIENT_SECRET'],
            code=code,
            callback=self._on_parsed_access_token)

    def _on_parsed_access_token(self, token_dict):
        if not token_dict:
            self.finish('login with github failed')
            return
        print token_dict
        self.finish(token_dict)


handlers = [
    ('/', HomeHandler),
    ('/login', LoginHandler),
]
