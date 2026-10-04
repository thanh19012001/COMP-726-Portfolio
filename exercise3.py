from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
from ecdsa.util import sigencode_string, sigdecode_string
import hashlib

# secp256k1 curve parameters (used by Bitcoin/Ethereum)
P = SECP256k1.curve.p()
A = SECP256k1.curve.a()
B = SECP256k1.curve.b()


def compress_pubkey(vk: VerifyingKey) -> bytes:
    """Compress a public key point (x, y) -> prefix(02/03) + x"""
    point = vk.pubkey.point
    x = point.x()
    y = point.y()
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    x_bytes = x.to_bytes(32, byteorder='big')
    return prefix + x_bytes


def decompress_pubkey(compressed: bytes) -> VerifyingKey:
    """Decompress prefix(02/03) + x -> full (x, y) point, then rebuild VerifyingKey"""
    prefix = compressed[0]
    x = int.from_bytes(compressed[1:], byteorder='big')

    # y^2 = x^3 + a*x + b (mod p)   [secp256k1: a=0]
    y_squared = (pow(x, 3, P) + A * x + B) % P

    # secp256k1's p is congruent to 3 mod 4, so sqrt is simply this modular exponent
    y = pow(y_squared, (P + 1) // 4, P)

    # pick the y with the correct parity to match the prefix
    if (y % 2 == 0 and prefix == 0x03) or (y % 2 == 1 and prefix == 0x02):
        y = P - y

    uncompressed = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
    return VerifyingKey.from_string(uncompressed, curve=SECP256k1)


if __name__ == "__main__":
    # 1. Generate ECDSA key pair (secp256k1 - same curve used by Bitcoin/Ethereum)
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()

    private_hex = sk.to_string().hex()
    public_uncompressed_hex = vk.to_string("uncompressed").hex()  # includes 0x04 prefix

    print("=== Key Pair (hex) ===")
    print(f"Private key (hex): {private_hex}")
    print(f"Public key uncompressed (hex): {public_uncompressed_hex}")

    print("\n=== PEM format ===")
    print(sk.to_pem().decode())
    print(vk.to_pem().decode())

    # save both keys to files (hex and PEM) so they can be opened in a text editor
    with open("private_ks.txt", "w") as f:
        f.write(private_hex)
    with open("public_ks.txt", "w") as f:
        f.write(public_uncompressed_hex)
    with open("private_ks.pem", "wb") as f:
        f.write(sk.to_pem())
    with open("public_ks.pem", "wb") as f:
        f.write(vk.to_pem())
    print("Keys saved to private_ks.txt, public_ks.txt, private_ks.pem, public_ks.pem\n")

    # 2. Compare sizes
    priv_bytes = len(sk.to_string())
    pub_uncompressed_bytes = len(vk.to_string("uncompressed"))

    print("=== Size comparison (uncompressed) ===")
    print(f"Private key: {priv_bytes} bytes | {len(private_hex)} hex chars")
    print(f"Public key (uncompressed): {pub_uncompressed_bytes} bytes | {len(public_uncompressed_hex)} hex chars")

    # 3. Compress the public key
    compressed = compress_pubkey(vk)
    compressed_hex = compressed.hex()
    print(f"\nPublic key (compressed): {len(compressed)} bytes | {len(compressed_hex)} hex chars")
    print(f"Compressed public key (hex): {compressed_hex}")

    reduction_pct = (1 - len(compressed) / pub_uncompressed_bytes) * 100
    print(f"\nStorage reduction from compression: {reduction_pct:.2f}%")

    # 4. Verify a signature using the DEcompressed public key
    message = b"COMP726 blockchain assignment - test message"
    signature = sk.sign(message, sigencode=sigencode_string)

    recovered_vk = decompress_pubkey(compressed)
    is_valid = recovered_vk.verify(signature, message, sigdecode=sigdecode_string)

    print("\n=== Signature verification using decompressed key ===")
    print(f"Original public key matches recovered: "
          f"{vk.to_string('uncompressed') == recovered_vk.to_string('uncompressed')}")
    print(f"Signature valid using decompressed key: {is_valid}")

    # 5. Negative test: the same signature must NOT verify for a modified message
    tampered_message = b"COMP726 blockchain assignment - tampered message"
    try:
        recovered_vk.verify(signature, tampered_message, sigdecode=sigdecode_string)
        print("Signature valid for tampered message: True")
    except BadSignatureError:
        print("Signature valid for tampered message: False (rejected as expected)")