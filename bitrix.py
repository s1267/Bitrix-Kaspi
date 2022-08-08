from typing import Union

import fast_bitrix24


class BitrixApi:

    def __init__(self, bx):
        self.bx = fast_bitrix24.Bitrix(bx)

    def get_products(self, deal_id: Union[int, str]):
        """
        :param deal_id: str or int
        :return: list: List of dicts products
        """
        method = 'crm.deal.productrows.get'
        fields = {
            'id': deal_id
        }
        products = self.bx.call(method, fields)
        if products:
            return products
        else:
            return None

    def get_deal(self, deal_id: Union[int, str]):
        method = 'crm.deal.get'
        fields = {
            'id': deal_id
        }
        deal = self.bx.call(method, fields)
        if deal:
            return deal
        else:
            return None

    def update_deal(self, deal_id: Union[int, str], field_for_update: str, value_for_field: Union[int, str, float]):
        """
        :param deal_id:int or str: Deal ID
        :param field_for_update: str: Field for updating
        :param value_for_field: str or int or float : Value for updating
        :return:
        """
        method = 'crm.deal.update'
        fields = {
            'id': deal_id,
            'fields': {
                field_for_update: value_for_field
            }
        }
        is_updated = self.bx.call(method, fields)
        print(is_updated)

    def update_deal_fields(self, deal_id: Union[int, str], dict_of_fields: dict):
        """
        :param deal_id: int or str: Deal id
        :param dict_of_fields: dict: Dict of fields for updating
        :return: None
        """
        method = 'crm.deal.update'
        fields = {
            'id': deal_id,
            'fields': dict_of_fields
        }
        is_updated = self.bx.call(method, fields)
        print(is_updated)

    def add_contact(self, name, second_name, phone_number):
        fields = {
            'fields': {
                'NAME': name,
                'LAST_NAME': second_name,
                'PHONE': [{
                    'VALUE': phone_number,
                    'VALUE_TYPE': 'WORK'
                }],
            }
        }
        contact_id = self.bx.call('crm.contact.add', fields)
        return contact_id

    def add_deal(self, contact_id, price, name):
        field = {
            'fields': {
                "TITLE": name,
                'CONTACT_ID': contact_id,
                'OPPORTUNITY': price,
                "STAGE_ID": "C22:NEW",
                'UF_CRM_1633354544234': name,
                "CATEGORY_ID": "22",
                "TYPE_ID": "SALE",
                "CURRENCY_ID": "KZT",
            }
        }
        lead_id = self.bx.call('crm.deal.add', field)
        return lead_id

