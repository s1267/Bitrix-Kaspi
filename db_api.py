import traceback

from peewee import *

db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db


class Deals(BaseModel):
    id = AutoField(primary_key=True)
    kaspi_id = CharField()
    kaspi_code = CharField()
    bitrix_id = CharField()
    bitrix_status = CharField()


def get_deal(bitrix_id):
    with db:
        try:
            deal_obj = Deals.get(Deals.bitrix_id == bitrix_id)
            return deal_obj
        except Exception as exc:
            return None
            # traceback.print_exc(exc)


def get_deals():
    with db:
        try:
            deal_obj = Deals().select()
            return deal_obj
        except Exception as exc:
            # traceback.print_exc(exc)
            return None


def add_deal(kaspi_id, kaspi_code, bitrix_id, bitrix_status):
    with db:
        if not get_deal(kaspi_id):
            deal_obj = Deals()
            deal_obj.kaspi_id = kaspi_id
            deal_obj.kaspi_code = kaspi_code
            deal_obj.bitrix_id = bitrix_id
            deal_obj.bitrix_status = bitrix_status
            deal_obj.save()
            return True
        else:
            return False


def change_status(bitrix_id, status):
    with db:
        try:
            deal_obj = Deals.get(Deals.bitrix_id == bitrix_id)
            deal_obj.bitrix_status = status
            deal_obj.save()
            return True
        except:
            return None

try:
    db.create_tables([Deals])
except Exception as e:
    traceback.print_exc(e)
