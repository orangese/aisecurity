"""AES encryption for the image database.

"""

import functools
import struct

import numpy as np
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from aisecurity.utils.paths import name_key_path, embed_key_path


################################ Setup ###############################

# CONSTANTS
_BIT_ENCRYPTION = 16


# DECORATORS
def require_permission(func):
    @functools.wraps(func)
    def _func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            raise OSError("permission denied (key file does not exist)")

    return _func


################################ Encryption helpers ###############################

# GENERATING ENCRYPTION INFO
@require_permission
def generate_key(key_file):
    open(key_file, "w").close()
    with open(key_file, "wb") as keys:
        key = get_random_bytes(_BIT_ENCRYPTION)
        keys.write(key)


@require_permission
def generate_cipher(key_file, alloc_mem):
    key = get_key(key_file)
    cipher = AES.new(key, AES.MODE_EAX)
    if alloc_mem:
        with open(key_file, "ab") as keys:
            keys.write(cipher.nonce)
    return cipher


# RETRIEVALS
@require_permission
def get_key(key_file):
    with open(key_file, "rb") as keys:
        key = b"".join(keys.readlines())[:_BIT_ENCRYPTION]
    return key


@require_permission
def get_nonce(key_file, position):
    with open(key_file, "rb") as keys:
        joined_nonces = b"".join(keys.readlines())[_BIT_ENCRYPTION:]
        nonce = joined_nonces[position*_BIT_ENCRYPTION:(position+1)*_BIT_ENCRYPTION]
    return nonce


# ENCRYPT AND DECRYPT
def encrypt(data, cipher):
    cipher_text, __ = cipher.encrypt_and_digest(data)
    return cipher_text


def decrypt(cipher_text, position, key_file):
    decrypt_cipher = AES.new(get_key(key_file), AES.MODE_EAX, nonce=get_nonce(key_file, position))
    return decrypt_cipher.decrypt(cipher_text)


################################ Used in aisecurity ###############################
def encrypt_data(data, ignore=None, decryptable=True, name_keys=name_key_path, embedding_keys=embed_key_path, **kwargs):
    if ignore is None:
        ignore = []

    if decryptable:
        generate_key(name_keys)
        generate_key(embedding_keys)

    encrypted = {}
    for person in data:
        assert data[person].ndim == 2, "embeds must have shape (number of embeds, dim(embed))"
        encrypted_name, encrypted_embeds = person, data[person].tolist()

        if "names" not in ignore:
            name_cipher = generate_cipher(name_keys, alloc_mem=decryptable)
            encrypted_name = "".join(chr(c) for c in list(encrypt(person.encode("utf-8"), name_cipher)))
            # bytes are not json-serializable

        if "embeddings" not in ignore:
            for idx, embed in enumerate(encrypted_embeds):
                embed_cipher = generate_cipher(embedding_keys, alloc_mem=decryptable)
                byte_embed = struct.pack("%sd" % len(embed), *embed)
                encrypted_embeds[idx] = list(encrypt(byte_embed, embed_cipher))

        encrypted[encrypted_name] = encrypted_embeds

    return encrypted


def decrypt_data(data, ignore=None, name_keys=name_key_path, embedding_keys=embed_key_path):
    if ignore is None:
        ignore = []

    adj_nonce_pos = 0
    decrypted = {}
    for nonce_pos, encrypted_name in enumerate(data):
        name, embeds = encrypted_name, data[encrypted_name]
        # assume embeds have shape (number of embeds, dim(embed) * 8) because double = 8 bytes

        """
        Obviously, if the embedding sets have differing lengths, the lengths of the nonce groups associated with
        those embeddings will be different.

        However, the position of the name nonce will not be affected by the length of the nonce group because it
        is stored in a different memory buffer than the embedding nonces. Therefore, the name nonce's position
        in its memory buffer is just the index of the name (nonce_pos).

        Embedding nonces are more complicated- we must take into account the lengths of the nonce groups.
        Therefore, the position of any specific embed (x) in a set of embeddings is given by the total length
        of all of the embeds in all of the embeddings prior to x (adj_nonce_pos).
        """

        if "names" not in ignore:
            name = decrypt(bytes(ord(c) for c in encrypted_name), nonce_pos, name_keys).decode("utf-8")

        if "embeddings" not in ignore:
            for idx, embed in enumerate(embeds):
                byte_embed = decrypt(bytes(embed), adj_nonce_pos + idx, embedding_keys)
                embeds[idx] = np.array(struct.unpack("%sd" % (len(byte_embed) // 8), byte_embed))
                # using double precision, hence int division by 8 (C double is 8 bits)

        adj_nonce_pos += len(embeds)
        decrypted[name] = embeds

    return decrypted
