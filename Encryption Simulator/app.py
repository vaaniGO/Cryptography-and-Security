from flask import Flask, render_template, url_for, abort, jsonify, request
import math
import random
import random
from hashlib import sha256

app = Flask(__name__)

state = {
    'person': '',
    'other_person': '',
    'public_information': '',
    'received_information': '',
    'own_private_key': '',
    'current_process': '',
    'other_private_key': '',
    'symmetric_key': ''
}

def computeRSAPair():
    p = random.choice([i for i in range(1000, 2000) if is_prime(i)])
    q = random.choice([i for i in range(1000, 2000) if is_prime(i) and i != p])
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = phi_n
    if math.gcd(e, phi_n) != 1:
        for i in range(3, phi_n, 2):
            if math.gcd(i, phi_n) == 1:
                e = i
                break
    d = pow(e, -1, phi_n)
    state['other_private_key'] = d
    state['public_information'] += f'hi {d}'
    return n, e

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/player/<string:person_name>')
def player_view(person_name):
    if person_name.lower() == 'alice': 
        nBob, eBob = computeRSAPair()
        state['person'] = 'Alice'
        state['other_person'] = 'Bob'
        state['public_information'] += f'\nBob Public Key: n: {nBob} e: {eBob}'
        state['received_information'] = ''
        state['own_private_key'] = 'Your private key will be generated here.'
        state['current_process'] = 'key_generation'
    elif person_name.lower() == 'bob':
        nAlice, eAlice = computeRSAPair()
        state['person'] = 'Bob'
        state['other_person'] = 'Alice'
        state['public_information'] = f'Alice Public Key: n: {nAlice} e: {eAlice}'
        state['received_information'] = 'Waiting for message from Alice...'
        state['own_private_key'] = 'Your private key will be generated here.'
        state['current_process'] = 'key_generation'
    else:
        abort(404)

    return render_template('play.html', data=state)

def is_prime(n):
    if n <= 1: return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0: return False
    return True

@app.route('/compute/primes', methods=['POST'])
def compute_primes():
    # In a real app, you'd pick much larger primes
    p = random.choice([i for i in range(1000, 2000) if is_prime(i)])
    q = random.choice([i for i in range(1000, 2000) if is_prime(i) and i != p])
    return jsonify({
        'p': p, 
        'q': q,
        'message': f'p = {p}, q = {q}'
    })

@app.route('/compute/euler', methods=['POST'])
def compute_euler():
    data = request.get_json()
    if not data or 'p' not in data or 'q' not in data:
        abort(400, 'Missing p or q in request') # Bad request
    
    p = data['p']
    q = data['q']
    n = p * q
    state['public_information'] += f' \n Alice Public Key: n: {n}'
    phi_n = (p - 1) * (q - 1)
    return jsonify({
        'n': n,
        'phi_n': phi_n,
        'message': f'n = {n}, φ(n) = {phi_n}'
    })

@app.route('/compute/e', methods=['POST'])
def compute_e():
    data = request.get_json()
    if not data or 'phi_n' not in data:
        abort(400, 'Missing phi_n in request')
        
    phi_n = data['phi_n']
    e = phi_n
    if math.gcd(e, phi_n) != 1:
        for i in range(3, phi_n, 2):
            if math.gcd(i, phi_n) == 1:
                e = i
                break
    state['public_information'] += f' e: {e}'
    return jsonify({'e': e, 'message': f'e = {e}'})

def estimate_time_to_break(n):
    OPS_PER_SECOND = 1e18 
    GNFS_CONSTANT_C = math.pow(64/9, 1/3)
    SECONDS_IN_A_YEAR = 31557600

    if n <= 1:
        return 0

    try:
        log_n = math.log(n)
        log_log_n = math.log(log_n)
        exponent = GNFS_CONSTANT_C * math.pow(log_n, 1/3) * math.pow(log_log_n, 2/3)
        total_operations = math.exp(exponent)
        total_seconds = total_operations / OPS_PER_SECOND
        years = total_seconds / SECONDS_IN_A_YEAR
        return years
        
    except ValueError:
        return 0

@app.route('/compute/d', methods=['POST'])
def compute_d():
    data = request.get_json()
    if not data or 'e' not in data or 'phi_n' not in data or 'n' not in data:
        abort(400, 'Missing e, phi_n, or n in request')

    e = data['e']
    phi_n = data['phi_n']
    n = data['n']
    d = pow(e, -1, phi_n)

    # Call our new helper function
    years_to_break = estimate_time_to_break(n)

    # Create a user-friendly message
    if years_to_break < 1e-9: # Less than a nanosecond
        time_message = "Instantly (less than a microsecond)."
    else:
        # Format the number for readability (e.g., 1.23e+50 years)
        time_message = f"An estimated {years_to_break:.2e} years."

    state['own_private_key'] = f'My Private Key = {d}'
    return jsonify({
        'd': d, 
        'message': f'{d}',
        'time_to_break_exact': time_message, # Our new "exact" message
    })

def truncate_hash_to_fit(hex_digest, modulus_n):
    """
    Reduces a large hash integer to be smaller than the modulus n.
    This is a simplified approach for educational purposes.
    """
    hash_int = int(hex_digest, 16)
    # This simple modulo operation ensures the number fits.
    # In real life, more complex padding schemes are used.
    return hash_int % modulus_n

def getValidSignedMsg():
    # We want to sign a msg with 'other private key'
    msg = random.randint(1000, 2000)
    d = state['other_private_key']
    n = state['public_information'].split(':')[2].split()[0]  # Extract n from public information
    hashed = sha256(str(msg).encode()).hexdigest()
    truncated = int(hashed, 16)
    s = pow(truncated, d, int(n))  # Sign the hashed message
    return msg, s

@app.route('/compute/raisesignedmsg', methods=['POST'])
def sign_e():
    print(state)
    signedMsg = state['received_information'].split(':')[1].split()[0]
    e = int(state['public_information'].split(':')[3].split()[0])
    n = int(state['public_information'].split(':')[2].split()[0] )
    result = pow(int(signedMsg), e, int(n))
    return jsonify({'result': result})

@app.route('/compute/getHash', methods=['POST'])
def get_hash():
    msg = state['received_information'].split(':')[2].split()[0]
    hashed = sha256(str(msg).encode()).hexdigest()
    n = state['public_information'].split(':')[2].split()[0]
    truncated = int(hashed, 16)%int(n)
    return jsonify({'result': truncated})

@app.route('/verifycert/begin')
def verifycert_begin():
    state['current_process'] = 'begin_verify_cert'
    s, m = getValidSignedMsg()
    state['received_information'] = f'Signed message: {s} \nMessage: {m}'
    return render_template('play.html', data=state)

@app.route('/verifycert/compute')
def verifycert():
    state['current_process'] = 'verify_cert'
    return render_template('play.html', data=state)

if __name__ == '__main__':
    app.run(debug=True)