import flask

from flask import Flask
from werkzeug.datastructures import ImmutableMultiDict
from config import *
from bitrix import BitrixApi
from kaspi import KaspiApi
from db_api import db, add_deal, get_deal, get_deals, change_status

app = Flask(__name__)
bx = BitrixApi(BitrixWebHook)
kaspi_obj = KaspiApi()


def check_auth(form_data: ImmutableMultiDict):
    """
    :param form_data: werkzeug.datastructures.ImmutableMultiDict: Request form data
    :return: bool: is authorize or not
    """
    auth_keys = ['auth[domain]', 'auth[client_endpoint]', 'auth[server_endpoint]', 'auth[member_id]',
                 'auth[application_token]']
    request_from_bitrix = [key in form_data for key in auth_keys]
    if False in request_from_bitrix:
        return False
    return (client_endpoint == form_data['auth[client_endpoint]']) \
           and (server_endpoint == form_data['auth[server_endpoint]']) \
           and (domain == form_data['auth[domain]']) \
           and (member_id == form_data['auth[member_id]']) \
           and (application_token == form_data['auth[application_token]'])


@app.route('/kaspi_update', methods=['GET', 'POST'])
def kaspi_update():
    if flask.request.method == 'POST':
        form_data = flask.request.form
        print(form_data)
        if check_auth(form_data):
            bitrix_id = form_data['data[FIELDS][ID]']
            deal_data = bx.get_deal(bitrix_id)
            if deal_data['CATEGORY_ID'] == str(CATEGORY_ID):
                kid = deal_data[kId]
                kaspi_code = deal_data[kaspicode]
                stage = deal_data['STAGE_ID']
                if form_data['event'] == 'ONCRMDEALADD':
                    add_deal(
                        kaspi_id=kid,
                        kaspi_code=kaspi_code,
                        bitrix_id=bitrix_id,
                        bitrix_status=stage
                    )
                else:
                    deal_obj = get_deal(bitrix_id=bitrix_id)
                    if deal_obj:
                        if deal_obj.bitrix_status == stage:
                            pass
                        else:
                            change_status(bitrix_id=bitrix_id, status=stage)
                            if stage == 'C22:LOSE':
                                reason = cancel_reasons[str(deal_data[cancel_reasons_field])]
                                print(reason)
                                kaspi_response = kaspi_obj.cancel_order(kid=kid, kaspi_code=kaspi_code,
                                                                        cancel_reason=reason)
                                if kaspi_response:
                                    pass
                                else:
                                    pass
                            elif stage == 'C22:UC_N5PMEW':
                                kaspi_response = kaspi_obj.send_sms(kid=kid, kaspi_code=kaspi_code)

                                if kaspi_response:
                                    pass
                                else:
                                    pass

                            elif stage == 'C22:WON':
                                kaspi_response = kaspi_obj.complete_order(kid=kid, kaspi_code=kaspi_code,
                                                                          customer_code=deal_data[customer_secret_code])
                                if kaspi_response:
                                    pass
                                else:
                                    pass
                    else:
                        add_deal(
                            kaspi_id=kid,
                            kaspi_code=kaspi_code,
                            bitrix_id=bitrix_id,
                            bitrix_status=stage
                        )
    return 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
