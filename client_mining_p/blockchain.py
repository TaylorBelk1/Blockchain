
import hashlib
import json
from time import time
from flask import Flask, jsonify, request
from uuid import uuid4
# Paste your version of blockchain.py from the basic_block_gp
# folder here
class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block)
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        raw_hash = hashlib.sha256(block_string)

        hash_string = raw_hash.hexdigest()
        return hash_string

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # TODO
        guess = block_string + str(proof)
        guess = guess.encode()
        hash_value = hashlib.sha256(guess).hexdigest()

        # return True or False
        return hash_value[:10] == '0000000000'


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()



# create a new route
@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()

    # check to make sure the request's response returned a proof or id
    if 'proof' not in data or  'id' not in data:
        response = {
            'status': 400,
            'message': 'No ID or Proof was provided'
        }

        return jsonify(response), 400

    # pull the proof from our requested data
    proof = data['proof']
    # grab the last block from the blockchain
    last_block = blockchain.last_block
    # change it from json to string format and sort it by it's keys
    last_block_string = json.dumps(last_block, sort_keys=True)
    # hash the last_block
    prev_hash = blockchain.hash(last_block)
    # create a new block using the proof and previous block (hashed)
    block = blockchain.new_block(proof, prev_hash)

    try:
        block = blockchain.new_block(last_block_string, proof)

        response = {
            'message': "New Block Created",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }

    except ValueError:
        response = {
            'success' : False,
            'message' : 'Bad Proof'
        }



    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        'len': len(blockchain.chain),
        'chain': blockchain.chain
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last_block' : blockchain.chain[-1]
    }

    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)