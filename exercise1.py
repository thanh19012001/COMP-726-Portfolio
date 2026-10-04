import hashlib
import json
import time


class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __repr__(self):
        return (f"Block #{self.index} | Hash: {self.hash[:12]}... | "
                f"Prev: {self.previous_hash[:12]}... | Tx: {self.transactions}")


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        new_block = Block(
            index=len(self.chain),
            transactions=transactions,
            previous_hash=self.get_latest_block().hash
        )
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            recalculated_hash = current.calculate_hash()

            # Check 1: has this block's data been tampered with?
            if current.hash != recalculated_hash:
                print(f"\n>>> TAMPERING DETECTED at Block #{i} <<<")
                print(f"Transaction data: {current.transactions}")
                print(f"Stored hash:       {current.hash}")
                print(f"Recalculated hash: {recalculated_hash}")
                print(f"(Mismatch means the transaction data was changed "
                      f"without updating the hash.)")
                return False, i

            # Check 2: does it still correctly link to the previous block?
            if current.previous_hash != previous.hash:
                print(f"\n>>> BROKEN LINK DETECTED at Block #{i} <<<")
                print(f"Block #{i}'s stored previous_hash: {current.previous_hash}")
                print(f"Actual hash of Block #{i - 1}:       {previous.hash}")
                print(f"(Mismatch means the chain link itself is broken.)")
                return False, i

        return True, None

    def print_chain(self):
        for block in self.chain:
            print(block)


if __name__ == "__main__":
    # 1. Build a chain of 10 blocks (including genesis)
    bc = Blockchain()
    for i in range(1, 10):
        bc.add_block(f"Transaction data {i}: Alice pays Bob {i * 10} coins")

    print("=== Blockchain BEFORE tampering ===")
    bc.print_chain()
    valid, bad_index = bc.is_chain_valid()
    print(f"\nValidation result: {valid}")

    # 2. Tamper with block 5's data WITHOUT recalculating its hash
    print("\n=== Tampering with Block 5 ===")
    bc.chain[5].transactions = "Alice pays Bob 9999 coins"  # hash NOT recalculated

    print("\n=== Blockchain AFTER tampering ===")
    bc.print_chain()
    valid, bad_index = bc.is_chain_valid()
    print(f"\nValidation result: {valid}")
    if not valid:
        print(f"First invalid block detected at index: {bad_index}")
    # 3. Second test: the attacker also recalculates Block 5's hash to hide the change
    print("\n=== Attacker recalculates Block 5's hash ===")
    bc.chain[5].hash = bc.chain[5].calculate_hash()
    bc.print_chain()
    valid, bad_index = bc.is_chain_valid()
    print(f"\nValidation result: {valid}")
    if not valid:
        print(f"First invalid block detected at index: {bad_index}")