from flask import Flask, render_template, url_for, abort, jsonify, request
import math
from sympy import isprime
import random
import random
from hashlib import sha256
from cryptography.fernet import Fernet
import base64
import os
# For the AES cipher, algorithm, and mode of operation
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# For the padding schemes (e.g., PKCS7)
from cryptography.hazmat.primitives import padding

# To get the default backend for cryptographic operations
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)

state = {
    'currentPlayer': '',
    'otherPlayer': '',
    'Alice' : {
        'secretKey': '',
        'publicKey': {
            'n': '',
            'e': ''
        },
        'p' : '',
        'q' : '',
        'signedMsg': '', 
        'msg': '',
        'verified': '',
        'receivedMsgs': {}
    },
    'Bob' : {
        'secretKey': '',
        'publicKey': {
            'n': '',
            'e': ''
        },
        'p' : '',
        'q' : '',
        'signedMsg': '',
        'msg': '',
        'verified': '',
        'receivedMsgs': {}
    },
    'currentProcess': '',
    'symmetricKey': '',
    'signedSymKey': '',
    'encrypted_key': ''
}

pageData = {
        'person': '',
        'other_person': '',
        'public_information':  '',
        'received_information': '',
        'own_private_key': '',
        'current_process': ''
}
# Computes the RSA Pair for the player and updates the state accordingly
def computeRSAPair(player):
    p = random.choice([i for i in range(10000, 20000) if isprime(i)])
    q = random.choice([i for i in range(10000, 20000) if isprime(i) and i != p])
    state[f'{player}']['p'] = p
    state[f'{player}']['q'] = q
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = phi_n
    if math.gcd(e, phi_n) != 1:
        for i in range(3, phi_n, 2):
            if math.gcd(i, phi_n) == 1:
                e = i
                break
    d = pow(e, -1, phi_n)
    state[f'{player}']['secretKey'] = d
    state[f'{player}']['publicKey']['e'] = e
    state[f'{player}']['publicKey']['n'] = n

# Computes a valid signed message, message pair for the palyer (sender) and updates the state accordingly
def getValidSignedMsg(player):
    # Required details of the signer
    d = state[f'{player}']['secretKey']
    n = state[f'{player}']['publicKey']['n']
    msg = random.randint(100000, 1000000)
    hashed_msg = sha256(str(msg).encode()).hexdigest()
    truncated = int(hashed_msg, 16)%n
    signedMsg = pow(truncated, d, n)
    state[f'{player}']['signedMsg'] = signedMsg
    state[f'{player}']['msg'] = msg

@app.route('/verify/validCert', methods=['POST'])
def verifyValidSig():
    data = request.get_json()
    player = data.get('player')
    e = state[f'{player}']['publicKey']['e']
    n = state[f'{player}']['publicKey']['n']
    msg = state[f'{player}']['msg']
    signedMsg = state[f'{player}']['signedMsg']

    # Now we check if signedMsg^e = hash(msg)
    # First let's compute hash(msg)
    hashed_msg = sha256(str(msg).encode()).hexdigest()
    hashed_msg = int(hashed_msg, 16)%n

    # Now let's raise the signed message to the other player's public exponent
    raised_msg = pow(int(signedMsg), e, n)
    print("Raised: ", raised_msg)
    print("Hashed: ", hashed_msg)

    # If the sender's certificate is verified then the sender is marked as verified
    state[f'{player}']['verified'] = (raised_msg == hashed_msg)

    eve_intervenes = (random.randint(0, 10) == 9) # Eve intervenes 10% of the time
    if (eve_intervenes): 
        return jsonify({
        'decrypted_hash': raised_msg,
        'recomputed_hash': random.randint(hashed_msg+1, hashed_msg*10),
        'is_verified': False
        })
    else:   
        return jsonify({
            'decrypted_hash': raised_msg,
            'recomputed_hash': hashed_msg,
            'is_verified': True
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/player/<string:person_name>')
def player_view(person_name):
    state['currentProcess'] = 'key_generation'
    if person_name.lower() == 'alice': 
        state['currentPlayer'] = 'Alice'
        state['otherPlayer'] = 'Bob'
        computeRSAPair('Bob')
    elif person_name.lower() == 'bob':
        state['currentPlayer'] = 'Bob'
        state['otherPlayer'] = 'Alice'
        computeRSAPair('Alice')
    else:
        abort(404)

    pageData['person'] = state['currentPlayer']
    pageData['other_person'] = state['otherPlayer']
    pageData['public_information'] = f"{state['otherPlayer']} Public Key: (n = {state[state['otherPlayer']]['publicKey']['n']}, e = {state[state['otherPlayer']]['publicKey']['e']})"
    pageData['received_information'] = 'You have to generate a public key to be able to receive messages!'
    pageData['own_private_key'] = 'Your private key appears here'
    pageData['current_process'] = state['currentProcess']
    return render_template('play.html', data=pageData)


@app.route('/compute/full_rsa_pair', methods=['POST'])
def performKeyGen():
    data = request.get_json()
    player = data.get('player')
    computeRSAPair(player)
    p = state[f'{player}']['p']
    q = state[f'{player}']['q']
    n = state[f'{player}']['publicKey']['n']
    e = state[f'{player}']['publicKey']['e']
    d = state[f'{player}']['secretKey']
    phi_n = (p - 1)*(q - 1)

    return jsonify({
        'p': p,
        'q': q,
        'primes_message': f'p = {p}, q = {q}',
        
        'n': n,
        'phi_n': phi_n,
        'euler_message': f'n = {n}, φ(n) = {phi_n}',
        
        'e': e,
        'e_message': f'e = {e}',
        
        'd': d,
        'd_message': f'{d}'
    })

@app.route('/verifycert/begin', methods=['POST'])
def beginVerifyCert():
    data = request.get_json()
    player = data.get('player')

    if state['currentPlayer'] == player:
        otherPlayer = state['otherPlayer']
    else:
        otherPlayer = state['currentPlayer']

    state['currentProcess'] = 'begin_verify_cert'
    getValidSignedMsg(state['otherPlayer'])
    signedMsg = state[f'{otherPlayer}']['signedMsg']
    msg = state[f'{otherPlayer}']['msg']

    current = state['currentPlayer']
    other = state['otherPlayer']

    pageData['person'] = state['currentPlayer']
    pageData['other_person'] = state['otherPlayer']
    pageData['public_information'] =  f"{other} Public Key: (n = {state[other]['publicKey']['n']}, e = {state[other]['publicKey']['e']}) \n{current} Public Key: (n = {state[current]['publicKey']['n']}, e = {state[current]['publicKey']['e']})"
    pageData['received_information'] = f'Signed message: {signedMsg}, Message: {msg} '
    pageData['own_private_key'] = f'Private key: {state[f"{state["currentPlayer"]}"]["secretKey"]}'
    pageData['current_process'] = state['currentProcess']

    return render_template('play.html', data=pageData)

@app.route('/verifycert/verify', methods=['POST'])
def verifyCert():
    data = request.get_json()
    player = data.get('player')

    if state['currentPlayer'] == player:
        otherPlayer = state['otherPlayer']
    else:
        otherPlayer = state['currentPlayer']

    signedMsg = state[f'{otherPlayer}']['signedMsg']
    msg = state[f'{otherPlayer}']['msg']

    state['currentProcess'] = 'verify_cert'

    current = state['currentPlayer']
    other = state['otherPlayer']

    pageData['person'] = state['currentPlayer']
    pageData['other_person'] = state['otherPlayer']
    pageData['public_information'] =  f"{other} Public Key: (n = {state[other]['publicKey']['n']}, e = {state[other]['publicKey']['e']}) \n{current} Public Key: (n = {state[current]['publicKey']['n']}, e = {state[current]['publicKey']['e']})"
    pageData['received_information'] = f'Signed message: {signedMsg}, Message: {msg} '
    pageData['own_private_key'] = f'Private key: {state[f"{state["currentPlayer"]}"]["secretKey"]}'
    pageData['current_process'] = state['currentProcess']

    return render_template('play.html', data=pageData)

@app.route('/symmetrickey/getKey', methods=['POST'])
def make_sym_key():
    state['currentProcess'] = 'gen_symmetric_key'
    pageData['current_process'] = state['currentProcess']
    pageData['received_information'] = 'Waiting for messages...'
    print(pageData)
    return render_template('play.html', data=pageData)

@app.route('/symmetrickey/generatekey/', methods=['POST'])
def generateKeyData():
    raw_key = os.urandom(3)  # 3 bytes = max 2^24 = 16 million
    key_int = int.from_bytes(raw_key, byteorder='big')

    # Optional: Base64 encode for display/debugging
    key_bytes = base64.urlsafe_b64encode(raw_key)

    print("key_int", key_int)
    n_other = state[state['otherPlayer']]['publicKey']['n']
    e_other = state[state['otherPlayer']]['publicKey']['e']
    encrypted = pow(key_int, e_other, n_other) 

    own_n = state[state['currentPlayer']]['publicKey']['n']
    own_d = state[state['currentPlayer']]['secretKey']

    encrypted_bytes = encrypted.to_bytes((encrypted.bit_length() + 7) // 8, byteorder='big')
    hashed = int(sha256(encrypted_bytes).hexdigest(), 16) % own_n

    signed = pow(hashed, own_d, own_n)

    result = {
        'symmetricKey': key_bytes.decode(),  # for debugging, you probably won't send this
        'encryptedKey': encrypted,
        'hashed': hashed,
        'signature': signed
    }

    return result

@app.route('/sendkey', methods=['POST'])
def sendSymKey():
    data = request.get_json()
    print(data)
    signed_key = data.get('signature')
    key = data.get('symmetricKey')
    state['signedSymKey'] = signed_key
    state['symmetricKey'] = key
    state['encryptedKey'] = data.get('encryptedKey')
    state['hashedKey'] = data.get('hashed')
    pageData['own_private_key'] += f'\nPrivate symmetric key: {key}'

    return jsonify({'status': 'ok'})

@app.route('/viewother', methods=['POST'])
def viewOtherPerspective():
    p = state[f'{state['otherPlayer']}']['p']
    q = state[f'{state['otherPlayer']}']['q']
    bobSecret = state[f'{state['otherPlayer']}']['secretKey']
    bobn = p*q
    signed_key = state['signedSymKey']
    e = state[f'{state['currentPlayer']}']['publicKey']['e']
    n = state[f'{state['currentPlayer']}']['publicKey']['n']
    raised_key = pow(signed_key, e, n)
    encrypted_key = int(state['encryptedKey'])
    print("encrypted key", encrypted_key)
    decrypted_key = pow(int(encrypted_key), bobSecret, bobn)
    print("decrypted key", decrypted_key)
    raw_key = decrypted_key.to_bytes(3, byteorder='big')
    raw_key = base64.urlsafe_b64encode(raw_key)
    raw_key = raw_key.decode()
    print("raw key", raw_key)

    pageData["other_person"] = state['otherPlayer']
    pageData["other_person_primes"] = (p, q)
    pageData["other_person_n"] = p * q
    pageData["other_person_e"] = state[state['otherPlayer']]['publicKey']['e']
    pageData["other_person_private_key"] = state[state['otherPlayer']]['secretKey']
    pageData["other_person_msg"] = state[state['otherPlayer']]['msg']
    pageData["other_person_signed_msg"] = state[state['otherPlayer']]['signedMsg']
    pageData["symmetricKey"] = state['symmetricKey']
    pageData["key_raised"] = raised_key
    pageData["hashed_key"] = state['hashedKey']
    pageData["decrypted_key"] = raw_key
    pageData['current_process'] = 'other_perspective'
    pageData['signedSymKey'] = state['signedSymKey']
    return render_template('other_perspective.html', data=pageData)

@app.route('/message/send', methods=['POST'])
def sendMessage():
    data = request.get_json()
    message = data.msg
    key = state['symmetricKey']
    fernet = Fernet(key.encode())
    message_bytes = message.encode()
    encrypted = fernet.encrypt(message_bytes)
    encrypted_str = encrypted.decode()
    other = state['otherPlayer']
    state[other]['receivedMsgs'] = encrypted_str

    return jsonify({'status': 'ok'})

@app.route('/message/get', methods=['POST'])
def getMessage():
    messages = [
        'My bank no. is A/c 32939004343',
        'My DOB is 04/09/06',
        'The murderer is John Keats',
        'The next deal will be secured for a billion dollars',
        'I know about the insider trading'
    ]
    message = random.choice(messages)
    key = state['symmetricKey']
    valid_key = sha256(key.encode()).digest()[:16]
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(valid_key), modes.CBC(iv), backend=default_backend())
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    encryptor = cipher.encryptor()
    ct_bytes = encryptor.update(padded_data) + encryptor.finalize()
    iv_b64_str = base64.b64encode(iv).decode('utf-8')
    ct_b64_str = base64.b64encode(ct_bytes).decode('utf-8')
    encrypted_str = f"{iv_b64_str}:{ct_b64_str}"
    print("ENCRYPTING WITH: ", valid_key, "IV: ", iv_b64_str, "padded_data: ", padded_data, "Encrypted_str: ", encrypted_str)
    pageData['receivedMessage'] = encrypted_str
    pageData['current_process'] = 'receive_message'
    pageData['received_information'] = f'(1) New message from {state['otherPlayer']}!'

    return render_template('play.html', data=pageData)

@app.route('/message/decrypt', methods=['POST'])    
def decryptSKMessage():
    data = request.get_json()
    encrypted_message = data['msg'] 
    key = state['symmetricKey']
    valid_key = sha256(key.encode()).digest()[:16]
    print("DECRYPTING WITH: ", valid_key)
    print("Encrypted message received on backend: ", encrypted_message)
    iv_b64_str, ct_b64_str = encrypted_message.split(':')
    iv = base64.b64decode(iv_b64_str)
    ct_bytes = base64.b64decode(ct_b64_str)
    cipher = Cipher(algorithms.AES(valid_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(ct_bytes) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    plaintext = decrypted_data.decode('utf-8')
    print("DECRYPTING WITH: ", valid_key, "IV: ", iv_b64_str, "padded_data: ", decrypted_padded_data)
    print("plaintext: ", plaintext)
    return jsonify({'decrypted_message': plaintext})

@app.route('/learn', methods=['GET'])
def loadLearnPage():
    return render_template('learn.html')

if __name__ == '__main__':
    app.run(debug=True)
    