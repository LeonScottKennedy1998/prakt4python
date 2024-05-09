from web3 import Web3
import re
from web3.middleware import geth_poa_middleware
from account_info import abi,contract_address

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=contract_address, abi=abi)

def auth():
    public_key = input("Введите публичный ключ: ")
    password = input("Введите пароль: ")
    try:
        w3.geth.personal.unlock_account(public_key,password)
        print("Авторизация прошла успешно")
        return public_key
    except Exception as e:
        print(e)
        return None

def is_strong_password(password):
    if len(password) < 12:
        return False

    if not re.search(r'[A-Z]', password):
        return False

    if not re.search(r'[a-z]', password):
        return False

    if not re.search(r'\d', password):
        return False

    if not re.search(r'[!@#$%^&*()-_+=\[\]{};:\'",.<>?/~`|\\]', password):
        return False

    return True

def registration():
    while True:
        password = input("Введите пароль: ")

        if is_strong_password(password):
            break
        else:
            print("Пароль должен содержать не менее 12 символов, включая заглавные и строчные буквы, цифры и специальные символы.")

    address = w3.geth.personal.new_account(password)
    print(f"Адрес нового аккаунта: {address}")
    return address


def create_estate(account):
    name = input("Введите название недвижимости: ")
    address = input("Введите адрес недвижимости: ")

    while True:
        estate_type = input("Введите тип недвижимости (House, Apartments, Flat, Loft): ")
        if estate_type in ["House", "Apartments", "Flat", "Loft"]:
            break
        else:
            print("Пожалуйста, выберите один из предложенных вариантов.")

    while True:
        rooms_input = input("Введите количество комнат: ")
        if rooms_input.isdigit():
            rooms = int(rooms_input)
            break
        else:
            print("Пожалуйста, введите целое число для количества комнат.")

    describe = input("Введите описание недвижимости: ")

    estate_type_map = {"House": 0, "Apartments": 1, "Flat": 2, "Loft": 3}
    estate_type_uint8 = estate_type_map.get(estate_type)

    try:
        tx_hash = contract.functions.createEstate(name, address, estate_type_uint8, rooms, describe).transact({
            "from": account
        })
        print("Недвижимость успешно создана. ID транзакции: ", tx_hash.hex())
    except Exception as e:
        print("Ошибка при создании недвижимости: ", e)


def create_ad(account):
    while True:
        estate_id_input = input("Введите ID недвижимости, для которой хотите создать объявление: ")
        if estate_id_input.isdigit():
            estate_id = int(estate_id_input)
            break
        else:
            print("Пожалуйста, введите целое число для ID недвижимости.")

    while True:
        price_input = input("Введите цену недвижимости: ")
        if price_input.isdigit():
            price = int(price_input)
            break
        else:
            print("Пожалуйста, введите целое число для цены недвижимости.")

    date_time = input("Введите дату(в циферках): ")

    try:
        tx_hash = contract.functions.createAd(estate_id, price, int(date_time)).transact({
            "from": account
        })
        print("Объявление успешно создано. ID транзакции: ", tx_hash.hex())
    except Exception as e:
        print("Ошибка при создании объявления: ", e)

def update_estate_status(account):
    while True:
        estate_id_input = input("Введите ID недвижимости, статус которой хотите обновить: ")
        if estate_id_input.isdigit():
            estate_id = int(estate_id_input)
            break
        else:
            print("Пожалуйста, введите целое число для ID недвижимости.")
    new_status = input("Введите новый статус недвижимости (true/false): ").lower()

    try:
        if new_status == "true":
            new_status = True
        elif new_status == "false":
            new_status = False
        else:
            raise ValueError("Неверное значение. Введите true или false.")
        tx_hash = contract.functions.updateEstateStatus(estate_id, new_status).transact({
            "from": account
        })
        print("Статус недвижимости успешно обновлен. ID транзакции: ", tx_hash.hex())
    except Exception as e:
        print("Ошибка при обновлении статуса недвижимости: ", e)

def update_ad_status(account):
    while True:
        ad_id_input = input("Введите ID объявления, статус которого хотите изменить: ")
        if ad_id_input.isdigit():
            ad_id = int(ad_id_input)
            break
        else:
            print("Пожалуйста, введите целое число для ID объяления.")

    new_status = input("Введите новый статус объявления (Opened/Closed): ").capitalize()

    try:
        if new_status == "Opened":
            new_status_enum = 0
        elif new_status == "Closed":
            new_status_enum = 1
        else:
            raise ValueError("Неверное значение. Введите Opened или Closed.")

        tx_hash = contract.functions.updateAdStatus(ad_id, new_status_enum).transact({
            "from": account
        })
        print("Статус объявления успешно обновлен. ID транзакции: ", tx_hash.hex())
    except Exception as e:
        print("Ошибка при обновлении статуса объявления: ", e)

def view_ad_by_id():
    while True:
        ad_id_input = input("Введите ID объявления: ")
        if ad_id_input.isdigit():
            ad_id = int(ad_id_input)
            break
        else:
            print("Пожалуйста, введите целое число для ID объяления.")
    try:
        ad_info = contract.functions.ads(ad_id).call()
        print("Информация об объявлении:")
        print("ID: ", ad_info[6])
        print("Владелец: ", ad_info[0])
        print("Цена: ", ad_info[2])
        print("Статус: ", "Opened" if ad_info[3] == 0 else "Closed")
        print("ID недвижимости: ", ad_info[4])
        print("Дата/Время: ", ad_info[5])
    except Exception as e:
        print("Ошибка при просмотре объявления: ", e)

def view_estate_by_id():
    while True:
        estate_id_input = input("Введите ID недвижимости: ")
        if estate_id_input.isdigit():
            estate_id = int(estate_id_input)
            break
        else:
            print("Пожалуйста, введите целое число для ID объяления.")
    try:
        estate_info = contract.functions.estates(estate_id).call()
        print("Информация о недвижимости:")
        print("ID: ", estate_info[2])
        print("Название: ", estate_info[0])
        print("Адрес: ", estate_info[1])
        print("Тип: ", estate_info[3])
        print("Количество комнат: ", estate_info[4])
        print("Описание: ", estate_info[5])
        print("Владелец: ", estate_info[6])
        print("Активность: ", "Active" if estate_info[7] else "Inactive")
    except Exception as e:
        print("Ошибка при просмотре недвижимости: ", e)

def get_balance(account):
    try:
        balance = contract.functions.getBalance().call({
            'from': account
        })
        print("Баланс на смарт-контракте: ", balance, "WEI")
    except Exception as e:
        print("Ошибка при получении баланса: ", e)

def purchase_estate(account):
    while True:
        ad_id_input = input("Введите ID объявления, по которому хотите совершить покупку: ")
        if ad_id_input.isdigit():
            ad_id = int(ad_id_input)
            break
        else:
            print("Пожалуйста, введите целое число для ID объяления.")

    try:
        ad_info = contract.functions.ads(ad_id).call()
        price_wei = ad_info[2] * 10**18

        balance_wei = w3.eth.get_balance(account)

        if balance_wei < price_wei:
            raise ValueError("Недостаточно средств для покупки недвижимости")

        tx_hash = contract.functions.purchaseEstate(ad_id).transact({
            "from": account,
            "value": price_wei
        })
        print("Недвижимость успешно куплена. ID транзакции: ", tx_hash.hex())
    except Exception as e:
        print("Ошибка при покупке недвижимости: ", e)

def withdraw_funds(account):
    try:
        balance_wei = contract.functions.getBalance().call({
            'from': account
        })

        if balance_wei == 0:
            print("На вашем балансе нет средств для вывода")
            return

        tx_hash = contract.functions.withdraw(balance_wei).transact({
            'from': account
        })
        print("Средства успешно выведены. ID транзакции: ", tx_hash.hex())
    except Exception as e:
        print("Ошибка при выводе средств: ", e)

def get_account_balance(account):
    try:
        balance_wei = w3.eth.get_balance(account)
        print("Баланс аккаунта: ", balance_wei, "WEI")
    except Exception as e:
        print("Ошибка при выводе средств: ", e)

def main():
    account = ""
    is_auth = False
    while True:
        if not is_auth:
            choice = input("Выберите:\n1. Авторизация\n2. Регистрация\n")
            match choice:
                case "1":
                    account = auth()
                    if account is not None:
                        is_auth = True
                case  "2":
                    registration()
        else:
            choice = input("Выберите:\n1. Создать недвижимость\n2. Создать объявление\n3. Изменить статус недвижимости\n4. Изменить статус объявления\n5. Посмотреть недвижимость по id\n6. Посмотреть объявление по id\n7. Посмотреть баланс смарт-контракта\n8. Посмотреть баланс аккаунта\n9. Купить недижимость\n10. Вывести средства на аккаунт\n11. Выйти\n")
            match choice:
                case "1":
                    create_estate(account)
                case "2":
                    create_ad(account)
                case "3":
                    update_estate_status(account)
                case "4":
                    update_ad_status(account)
                case "5":
                    view_estate_by_id()
                case "6":
                    view_ad_by_id()
                case "7":
                    get_balance(account)
                case "8":
                    get_account_balance(account)
                case "9":
                    purchase_estate(account)
                case "10":
                    withdraw_funds(account)
                case "11":
                    is_auth = False
                case _:
                    print("Введите корректное число")


if __name__ == "__main__":
    main()