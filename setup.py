import serial.tools.list_ports
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import os 
import json 
import pyudev
import time

def find_usb_mount_path(target_serial):
    context = pyudev.Context()
    # поисск среди блочных устройств
    for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
        # серийный номер родительского устройства
        parent = device.find_parent('usb', 'usb_device')
        if parent and parent.get('ID_SERIAL_SHORT') == target_serial:
            # ищем устройство в системее
            # !! На винде не будет рабоать
            # TODO: сделать норм замену что бы работало на винде
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    if device.device_node in line:
                        return line.split()[1] #  путь монтирования
    return None



def save_to_s_db(id_str: str, public_key_hex, db_path="server_db.json"):
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = []
    else:
        db = []

    db = [entry for entry in db if entry.get("id") != id_str]

    db.append({
        "id": id_str, "public_key_hex": public_key_hex
    })


    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    
    print(f"Данные успешно сохранены в {db_path}")

def generate_keys():
    # ключи ed25519
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # OpenSSH формат 
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )
    raw_public = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    
    return pem_private, raw_public


def setup_usb(main_dict: dict):
    print("Выберите устройство для работы (ID)")
    print("> ",end="")
    #d_id = int(input())
    try:
        d_id = int(input("> "))
    except ValueError:
        print("Ошибка: введите корректный ID устройства")
        return 
    if d_id < 0:
        print("Неправильный ID")
    else:
        print("Вы выбрали:")
        print(main_dict[d_id]["Device"])
        print("Все верно?(y/n)")
        c = input().strip()
        if "y" in c:
            hwid = main_dict[d_id]["HWID"] # TODO: почистить
            ser_num = main_dict[d_id]['SerialNumber']
            device = main_dict[d_id]['Device']
            vid = main_dict[d_id]["VID"]
            pid = main_dict[d_id]["PID"]
            #id_str = str(hwid) + str(vid) + str(pid) + str(ser_num)
            id_str = f"{main_dict[d_id]['VID']}:{main_dict[d_id]['PID']}:{main_dict[d_id]['SerialNumber']}"
            priv_key, pub_key_raw = generate_keys()
            #path_to_usb = f"/run/media/user/{FLASH_NAME}/private_key.pem"
            #with open(path_to_usb, "wb") as f: f.write(priv_key)
            print(" Поиск точки монтирования...")
            usb_path = find_usb_mount_path(ser_num) 

            #if usb_path:
            #    print(f"[OK] Флешка найдена: {usb_path}")
            #    full_path = os.path.join(usb_path, "private_key.pem")
            #    with open(usb_path, "wb") as f: f.write(priv_key)
            #    print(f"Приватный ключ сохранен в {full_path}")
            if usb_path:
                print(f"[OK] Флешка найдена: {usb_path}")
                full_path = os.path.join(usb_path, "private_key.pem")
                # Исправлено: открываем full_path
                with open(full_path, "wb") as f: 
                    f.write(priv_key)
                print(f"Приватный ключ сохранен в {full_path}")

                # запись ключа
            else:
                usb_path = input("Путь до флешки не найден, ведите путь к примонтированной флешке вручную: ")
                full_path = os.path.join(usb_path, "private_key.pem")
            print(f"Ключи сгенерированы для ID: {id_str}")
            save_to_s_db(id_str, pub_key_raw.hex())
            time.sleep(2)
            print("Все готово")
            #======================
            # Пока все готово тут =
            #======================







def get_usb_flash_hwid() -> dict:
    #  список всех доступных  портов
    ports = serial.tools.list_ports.comports()

    found = False
    num = 0
    my_dict = dict()
    i = 0
    for port in ports:

        if "USB" in port.hwid:
            found = True
            num+=1
            print(f"[HELP] ID = {i}")
            print(f"Device: {port.description}")
            print(f"HWID: {port.hwid}")
            print(f"Vendor ID (VID): {port.vid}")
            print(f"Product ID (PID): {port.pid}")
            print(f"Serial Number: {port.serial_number}")
            print("-" * 20)
            my_dict[i] = {
                "Device": port.description,
                "HWID": port.hwid,
                "VID": port.vid,
                "PID": port.pid,
                "SerialNumber": port.serial_number
            }

            i+=1

    if not found :
        print("USB не найден")
    return my_dict



        

if __name__ == "__main__":
    dictt = get_usb_flash_hwid()
    setup_usb(dictt)


