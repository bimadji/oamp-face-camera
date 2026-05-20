import qrcode

# Teks yang ingin dijadikan QR Code
data = "aw Afandi"

# Membuat QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(data)
qr.make(fit=True)

# Membuat gambar QR
img = qr.make_image(fill_color="black", back_color="white")

# Simpan gambar
img.save("qrcode.png")

print("QR Code berhasil dibuat!")