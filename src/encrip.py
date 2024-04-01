def encrypt(text, key):
    encrypted_text = ""
    for char in text:
        if char.isalpha():
            shifted = ord(char) + key
            if char.islower():
                if shifted > ord('z'):
                    shifted -= 26
            elif char.isupper():
                if shifted > ord('Z'):
                    shifted -= 26
            encrypted_text += chr(shifted)
        else:
            encrypted_text += char
    return encrypted_text

def decrypt(encrypted_text):
    decrypted_text = ""
    key = 3
    for char in encrypted_text:
        if char.isalpha():
            shifted = ord(char) - key
            if char.islower():
                if shifted < ord('a'):
                    shifted += 26
            elif char.isupper():
                if shifted < ord('A'):
                    shifted += 26
            decrypted_text += chr(shifted)
        else:
            decrypted_text += char
    return decrypted_text




if __name__ == "__main__":
    mensaje = "mysql+pymysql://root:@127.0.0.1/proyectGalleta"
    clave = 3

    mensaje_encriptado = encrypt(mensaje, clave)
    mensaje_encriptado1 = "pbvto+sbpbvto://urrw:@127.0.0.1/surbhfwJdoohwd"
    print("Mensaje encriptado:", mensaje_encriptado)

    mensaje_desencriptado = decrypt(mensaje_encriptado)
    print("Mensaje desencriptado:", mensaje_desencriptado)
