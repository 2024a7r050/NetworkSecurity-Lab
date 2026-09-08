# Caesar Cipher

text = input("Enter message: ")
key = int(input("Enter key: "))

encrypted = ""

for ch in text:
    encrypted += chr((ord(ch) - 65 + key) % 26 + 65)

print("\nCaesar Cipher")
print("encrypted :", encrypted)

decrypted = ""

for ch in encrypted:
    decrypted += chr((ord(ch) - 65 - key) % 26 + 65)

print("decrypted :", decrypted)


# Vigenere Cipher

key = input("\nEnter keyword: ").upper()
encrypted = ""
j = 0

for ch in text:
    shift = ord(key[j % len(key)]) - 65
    encrypted += chr((ord(ch) - 65 + shift) % 26 + 65)
    j += 1

print("\nVigenere Cipher")
print("encrypted :", encrypted)

decrypted = ""
j = 0

for ch in encrypted:
    shift = ord(key[j % len(key)]) - 65
    decrypted += chr((ord(ch) - 65 - shift) % 26 + 65)
    j += 1

print("decrypted :", decrypted)
