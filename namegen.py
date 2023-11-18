from Crypto.Hash import keccak


def genName(name:str)->str:
    return keccak.new(digest_bits=256).update(name.encode("utf-8")).hexdigest()

