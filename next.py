
# import libraries
import sys
import numpy as np
from PIL import Image
from flask import Flask, render_template, request

np.set_printoptions(threshold=sys.maxsize)

# encoding function
password = ""
def Encode(src, message, dest, password):
    img = Image.open(src, 'r')
    width, height = img.size
    array = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n = 3
    elif img.mode == 'RGBA':
        n = 4

    total_pixels = array.size//n

    message += password
    b_message = ''.join([format(ord(i), "08b") for i in message])
    req_pixels = len(b_message)

    if req_pixels > (total_pixels * 3):
        return "ERROR: Need larger file size"

    else:
        index=0
        for p in range(total_pixels):
            for q in range(0, 3):
                if index < req_pixels:
                    array[p][q] = int(bin(array[p][q])[2:9] + b_message[index], 2)
                    index += 1

        array=array.reshape(height, width, n)
        enc_img = Image.fromarray(array.astype('uint8'), img.mode)
        enc_img.save(dest)
        return "Image Encoded Successfully"


# decoding function
def Decode(src, password):
    img = Image.open(src, 'r')
    array = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n = 3
    elif img.mode == 'RGBA':
        n = 4

    total_pixels = array.size//n

    hidden_bits = ""
    for p in range(total_pixels):
        for q in range(0, 3):
            hidden_bits += (bin(array[p][q])[2:][-1])

    hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]

    message = ""
    hiddenmessage = ""
    for i in range(len(hidden_bits)):
        x = len(password)
        if message[-x:] == password:
            break
        else:
            message += chr(int(hidden_bits[i], 2))
            message = f'{message}'
            hiddenmessage = message
    # verifying the password
    if password in message:
        return hiddenmessage[:-x]
    else:
        return "You entered the wrong password: Please Try Again"

# initialize Flask app
app = Flask(__name__)

# home page
@app.route('/')
def home():
    return render_template('home.html')

# encoding page
@app.route('/encode')
def encode():
    return render_template('encode.html')

# decoding page
@app.route('/decode')
def decode():
    return render_template('decode.html')

# encode function
@app.route('/do_encode', methods=['POST'])
def do_encode():
    src = request.files['source-image']
    message = request.form['message']
    dest = request.form['destination-image']
    password = request.form['password']
    src.save('src.png')
    result = Encode('src.png', message, dest, password)
    return render_template('result.html', result=result)

# decode function
@app.route('/do_decode', methods=['POST'])
def do_decode():
    src = request.files['source-image']
    password = request.form['password']
    src.save('src.png')
    result = Decode('src.png',password)
    return render_template('result.html',result=result)
    
if __name__ == '__main__':
    app.run()

