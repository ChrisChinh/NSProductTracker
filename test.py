from database.database import Database
from database.userdb import UserDB


def test_db():
    db = Database()
    db.connect()
    serial = db.new_serial()
    print('Serial: ', serial)
    test_obj = {'SerialNumber': serial, 'PartNumber': 'model_t', 'DesignVersion': '1.0', 'CreationParameters': 'test',
                'PurchaseOrder': 'test.pdf', 'DeliveryRecords': 'test', 'Feedback': 'bad', 'Images': 'test.jpg', 'MFGSuccess': False,
                'PerfSuccess': False, 'CustomerSuccess': False, 'CriticalFrequency': 0, 'Bandwidth': 0}
    assert db.add_item(test_obj, serial)
    print('Added item successfully')
    item = db.get_item(serial)
    assert isinstance(item, dict)
    print('Retrieved item successfully')
    print('Test passed')
    print('Item: ', item)


def test_userdb():
    userdb = UserDB()
    userdb.connect()
    userdb.create_table()
    user = 'test_user'
    password = 'test_password'
    assert userdb.add_user(user, password)
    print('Added user successfully')
    assert userdb.get_user(user) == password
    print('Retrieved user successfully')


def main():
    test_userdb()


if __name__ == '__main__':
    main()
