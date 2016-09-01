import argparse
parser = argparse.ArgumentParser(
    description='Sample from trained model file',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    'vocab_file',
    type=argparse.FileType('r'),
    help="Vocabulary file generated by vocab.py."
)
parser.add_argument(
    'model_file',
    type=str,
    help="Model file generated by train.py."
)

parser.add_argument(
    '--temperature', '-t',
    type=float,
    default=1.0,
    help="Temperature of softmax during sampling."
)
parser.add_argument(
    '--prime', '-p',
    type=str,
    default="",
    help="String to prime the network with."
)

args = parser.parse_args()


import sys
import numpy as np
import cPickle as pickle

import theano
import theano.tensor as T
import numpy as np

import vocab
import model
from theano_toolkit.parameters import Parameters

if __name__ == "__main__":
    model_file = args.model_file
    temp_input = args.temperature
    id2char = pickle.load(args.vocab_file)
    char2id = vocab.load(args.vocab_file.name)
    prime_str = args.prime

    P = Parameters()
    sampler = model.build_sampler(P,
                                  character_count=len(char2id) + 1,
                                  embedding_size=20,
                                  hidden_size=100
                                  )
    P.load(model_file)
    temp = T.scalar('temp')
    char = T.iscalar('char')
    p_cell_1, p_hidden_1, p_cell_2, p_hidden_2 = T.vector("p_cell_1"), T.vector("p_hidden_2"), T.vector("p_cell_2"), T.vector("p_hidden_2")

    output, cell_1, hidden_1, cell_2, hidden_2 = sampler(temp, char, p_cell_1, p_hidden_1, p_cell_2, p_hidden_2)
    sample = theano.function(
        inputs=[temp, char, p_cell_1, p_hidden_1, p_cell_2, p_hidden_2],
        outputs=[output, cell_1, hidden_1, cell_2, hidden_2]
    )

    orig_c1 = P.init_recurrent_1_cell.get_value()
    orig_h1 = T.tanh(P.init_recurrent_1_hidden).eval()
    orig_c2 = P.init_recurrent_2_cell.get_value()
    orig_h2 = T.tanh(P.init_recurrent_2_hidden).eval()

    for _ in xrange(20):
        result = prime_str
        c_id = -1
        probs, c1, h1, c2, h2 = sample(temp_input, c_id, orig_c1, orig_h1, orig_c2, orig_h2)

        for char in prime_str:
            c = char2id[char]
            probs, c1, h1, c2, h2 = sample(temp_input, c, c1, h1, c2, h2)

        while len(result) < 200:
            probs = probs.astype(np.float64)
            probs = probs / probs.sum()
            c_id = np.argmax(np.random.multinomial(1, pvals=probs))
            char = id2char[c_id]
            if char == "\n":
                break
            result = result + char
            probs, c1, h1, c2, h2 = sample(temp_input, c_id, c1, h1, c2, h2)
        print result
