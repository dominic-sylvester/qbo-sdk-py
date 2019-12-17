"""
Quickbooks online Python SDK
"""
import json
import base64
import requests
from future.moves.urllib.parse import urlencode

from .exceptions import *
from .apis import *


class QuickbooksOnlineSDK:
    """
    Quickbooks Online SDK
    """
    TOKEN_URL = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'

    def __init__(self, client_id: str, client_secret: str,
                 refresh_token: str, realm_id: str, environment: str):
        """
        Initialize connection to Quickbooks Online
        :param client_id: Quickbooks online client_Id
        :param client_secret: Quickbooks online client_secret
        :param refresh_token: Quickbooks online refresh_token
        :param realm_id: Quickbooks onliine realm / company id
        :param environment: production or sandbox
        """
        # Initializing variables
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.refresh_token = refresh_token

        if environment.lower() == 'production':
            self.__base_url = 'https://quickbooks.api.intuit.com/v3/company/{0}'.format(realm_id)
            self.web_app_url = 'https://app.qbo.intuit.com'
        elif environment.lower() == 'sandbox':
            self.__base_url = 'https://sandbox-quickbooks.api.intuit.com/v3/company/{0}'.format(realm_id)
            self.web_app_url = 'https://app.sandbox.qbo.intuit.com'
        else:
            raise ValueError('environment can only be prodcution / sandbox')

        self.__access_token = None

        self.Accounts = Accounts()
        self.Departments = Departments()
        self.Classes = Classes()
        self.Employees = Employees()

        self.update_server_url()
        self.update_access_token()

    def update_server_url(self):
        base_url = self.__base_url

        self.Accounts.set_server_url(server_url=base_url)
        self.Departments.set_server_url(server_url=base_url)
        self.Classes.set_server_url(server_url=base_url)
        self.Employees.set_server_url(server_url=base_url)

    def update_access_token(self):
        """
        Update the access token and change it in all API objects.
        """
        self.__get_access_token()
        access_token = self.__access_token

        self.Accounts.change_access_token(access_token)
        self.Departments.change_access_token(access_token)
        self.Classes.change_access_token(access_token)
        self.Employees.change_access_token(access_token)

    def __get_access_token(self):
        """Get the access token using a HTTP post.

        Returns:
            A new access token.
        """

        api_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        auth = '{0}:{1}'.format(self.__client_id, self.__client_secret)
        auth = base64.b64encode(auth.encode('utf-8'))

        request_header = {
            'Accept': 'application/json',
            'Content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {0}'.format(
                str(auth.decode())
            )
        }

        token_url = QuickbooksOnlineSDK.TOKEN_URL.format(self.__base_url)
        response = requests.post(url=token_url, data=urlencode(api_data), headers=request_header)

        if response.status_code == 200:
            auth = json.loads(response.text)
            self.__access_token = auth['access_token']
            self.refresh_token = auth['refresh_token']

        elif response.status_code == 401:
            raise UnauthorizedClientError('Wrong client secret or/and refresh token', response.text)

        elif response.status_code == 404:
            raise NotFoundClientError('Client ID doesn\'t exist', response.text)

        elif response.status_code == 500:
            raise InternalServerError('Internal server error', response.text)

        else:
            raise QuickbooksOnlineSDK('Error: {0}'.format(response.status_code), response.text)