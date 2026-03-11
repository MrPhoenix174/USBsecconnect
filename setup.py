import serial.tools.list_ports


def generate_keys():
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization

    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    #  Экспорт в формате PEM для сохранеия на флешку
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )

    #pem_public = public_key.public_bytes(
    #    encoding=serialization.Encoding.PEM,
    #    format=serialization.PublicFormat.SubjectPublicKeyInfo
    #)   

    #print("Приватный ключ (PEM):\n", pem_private.decode())
    print("Публичный ключ (PEM):\n", pem_public.decode())

    #  Получение байтов (32)
    #raw_private = private_key.private_bytes(
    #    encoding=serialization.Encoding.Raw,
    #    format=serialization.PrivateFormat.Raw,
    #    encryption_algorithm=serialization.NoEncryption()
    #)
    raw_public = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    #print("Сырой приватный ключ (hex):", raw_private.hex())
    print("Сырой публичный ключ (hex):", raw_public.hex())


def setup_usb(main_dict: dict):
    print("Выберите устройство для работы (ID)")
    print("> ",end="")
    d_id = int(input())
    if d_id < 0:
        print("Неправильный ID")
    else:
        print("Вы выбрали:")
        print(main_dict[d_id]["Device"])
        print("Все верно?(y/n)")
        c = input().strip()
        if "y" in c:
            hwid = main_dict[d_id]["HWID"]
            ser_num = main_dict[d_id]['SerialNumber']
            device = main_dict[d_id]['Device']
            vid = main_dict[d_id]["VID"]
            pid = main_dict[d_id]["PID"]
            id_str = str(hwid) + str(vid) + str(pid) + str(ser_num)






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

    if found == False:
        print("USB не найден")
    return my_dict



        

if __name__ == "__main__":
    dictt = get_usb_flash_hwid()
    setup_usb(dictt)


