from db_api import *
import json
from icecream import ic
from bitrix import BitrixApi
from kaspi import KaspiApi
import time


def add_customer_to_db(user_json):
    return add_customer(full_name=user_json['full_name'], cell_phone=user_json['cell_phone'],
                        user_kid=user_json['user_kid'])


def add_order_to_db(order_json):
    user_id = get_customer(order_json['user_kid'])
    return add_order(kaspi_id=order_json['kaspi_id'], kaspi_code=order_json['kaspi_code'], status=order_json['status'],
                     customer_id=user_id, price=order_json['price'])


def load_price_json():
    with open('price.json', 'r') as json_file:
        price_json = json.load(json_file)
        ic(price_json)
        return price_json


if __name__ == '__main__':
    kaspi = KaspiApi()
    bx_24 = BitrixApi()
    tm = int(round((time.time() * 1000) - 864000000, 0))

    for k in kaspi.get_orders(tm)['data']:
        customer_json = kaspi.get_customer_data(k)
        order_json = kaspi.get_order_data(k)
        add_customer_to_db(customer_json)
        add_order_to_db(order_json)
        order_id = get_order(order_json['kaspi_id'])
        ic(order_json)
        if get_bitrix_note(order_id):
            ic('уже есть такая сделка заебал')
            break
        else:
            customer = get_customer(customer_json['user_kid'])
            contact = get_contact(customer_id=customer)
            if contact:
                bitrix_did = bx_24.add_deal(
                    contact_id=contact.bitrix_cid,
                    price=order_json['price'],
                    name=order_json['name']
                )
                adding_order_to_db = add_bitrix_note(order_id=order_id, customer_id=customer,
                                                     contact_id=get_contact(customer_id=customer),
                                                     bitrix_did=bitrix_did)
                if adding_order_to_db is True:
                    ic("добавили")
                else:
                    ic('такая сделка уже была ващета')
                break
            else:
                ic('нет контакта добавляю ->')
                bitrix_cid = bx_24.add_contact(
                    name=customer_json['full_name'].split(' ')[0],
                    second_name=customer_json['full_name'].split(' ')[1],
                    phone_number=customer_json['cell_phone']
                )
                adding_contact_to_db = add_contact(bitrix_cid, customer_id=customer)
                ic(bitrix_cid)
                bitrix_did = bx_24.add_deal(
                    contact_id=bitrix_cid,
                    price=order_json['price'],
                    name=order_json['name']
                )

                adding_order_to_db = add_bitrix_note(order_id=order_id, customer_id=customer,
                                                     contact_id=get_contact(customer_id=customer),
                                                     bitrix_did=bitrix_did)
                if adding_order_to_db is True:
                    ic("добавили")
                else:
                    ic('такая сделка уже была ващета')
                break
    # kaspi = KaspiApi()
    # tm = int(round((time.time() * 1000) - 864000000, 0))
    # kaspi_orders = kaspi.get_orders(tm)
    # first_diff = set(get_kaspi_ids(kaspi_orders).items()) - set(get_db_orders().items())
    # second_diff = set(get_db_orders().items()) - set(get_kaspi_ids(kaspi_orders).items())
    # if second_diff != set():
    #     for elem in second_diff:
    #         new_status = kaspi.get_status_by_code(elem[0])
    #         change_st = change_status(elem[0], new_status)
    #         ic('changed')
    # if first_diff != set():
    #     adding_to_db = add_orders_to_db(first_diff)
    #
    # ic(first_diff)
    # ic(second_diff)

# Vadim KZ:
# https://igspace.bitrix24.kz/stream/?current_fieldset=SOCSERV
#
# general.xpm@mail.ru
#
# 97554321Ss2!

# 6DBe8/35nYhQDyCnlglOI/QZOA8ooBDt+42wVso2yy8=
