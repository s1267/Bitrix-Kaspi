import time

import requests
from icecream import ic
from config import x_auth_token


class KaspiApi:
    api_request_headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        'Content-Type': 'application/vnd.api+json',
        'X-Auth-Token': x_auth_token
    }

    @staticmethod
    def _request(*args, **kwargs):
        response = requests.request(*args, **kwargs)
        if response.status_code == 200:
            return response.json()
        print(response.text)

    @staticmethod
    def get_customer_data(order_json):
        """
        This function serves as an interface to retrieve information about the customer
        :param order_json: dict: Information about the customer in Kaspi
        :return: dict or None
        """
        try:
            customer = order_json['attributes']['customer']
            return {'full_name': customer['firstName'] + ' ' + customer['lastName'], 'user_kid': customer['id'],
                    'cell_phone': customer['cellPhone']}
        except KeyError as ke:
            return None

    def get_data_by_code(self, code):
        """
        :param code: int or str: Order code in Kaspi
        :return: str: Order state
        """
        url = f'https://kaspi.kz/shop/api/v2/orders?filter[orders][code]={code}'
        return self._request(method='get', url=url, headers=self.api_request_headers)

    def get_orders(self, timestamp, state):
        """
        :param state: str:  - NEW - new order
                            - SIGN_REQUIRED - order is being signed
                            - PICKUP - pickup
                            - DELIVERY - delivery
                            - KASPI_DELIVERY - Kaspi Delivery
                            - ARCHIVE - archive order
        :param timestamp: int or str : Date the last order was created (maximum 10 days ago)
        :return: dict: response from Kaspi
        """
        url = f'https://kaspi.kz/shop/api/v2/orders?page[number]=0&page[size]=20&filter[orders][state]={state}&filter[orders][creationDate][$ge]={timestamp}&filter[orders][status]=CANCELLED'
        return self._request(method='get', url=url, headers=self.api_request_headers)

    def get_order_values(self, code):
        url = f'https://kaspi.kz/shop/api/v2/orders?filter[orders][code]={code}'
        return self._request(method='get', url=url, headers=self.api_request_headers)

    def get_order_goods(self, order_json):
        try:
            order = order_json['attributes']
            entries_url = order_json['relationships']['entries']['links']['self']
            entries_id = self._request(method='get', url=entries_url, headers=self.api_request_headers)
            if entries_id:
                name_url = f'https://kaspi.kz/shop/api/v2/orderentries/{entries_id}/product'
                entries_resp = self._request(method='get', url=name_url, headers=self.api_request_headers)
                return {'entries': entries_id, 'entries_data': entries_resp}
        except KeyError as ke:
            return None

    def cancel_order(self, kid, kaspi_code, cancel_reason):
        url = 'https://kaspi.kz/shop/api/v2/orders'
        json_data = {
            "data": {
                "type": "orders",
                "id": kid,
                "attributes": {
                    "code": kaspi_code,
                    "status": "CANCELLED",
                    "cancellationReason": cancel_reason
                }
            }
        }
        return self._request(method='post', url=url, json=json_data, headers=self.api_request_headers)

    def send_sms(self, kid, kaspi_code):
        url = 'https://kaspi.kz/shop/api/v2/orders'
        json_data = {
            "data": {
                "type": "orders",
                "id": kid,
                "attributes": {
                    "code": kaspi_code,
                    "status": "COMPLETED"
                }
            }
        }
        return self._request(method='post', url=url, json=json_data, headers=self.api_request_headers)

    def change_status(self, kid, kaspi_code, status):
        url = 'https://kaspi.kz/shop/api/v2/orders'
        json_data = {
            "data": {
                "type": "orders",
                "id": kid,
                "attributes": {
                    "code": kaspi_code,
                    "status": status
                }
            }
        }
        return self._request(method='post', url=url, json=json_data, headers=self.api_request_headers)


    def complete_order(self, kid, kaspi_code, customer_code):
        url = 'https://kaspi.kz/shop/api/v2/orders'
        json_data = {
            "data": {
                "type": "orders",
                "id": kid,
                "attributes": {
                    "code": kaspi_code,
                    "status": "COMPLETED"
                }
            }
        }
        headers = self.api_request_headers
        headers.update({
            'X-Security-Code': customer_code,
            'X-Send-Code': 'true',
        })
        return self._request(method='post', url=url, json=json_data, headers=headers)
