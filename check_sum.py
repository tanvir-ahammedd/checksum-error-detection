"""
========================================================
  CHECKSUM GENERATOR AND VALIDATOR
  Data Communication — Error Detection System
========================================================

"""

import random


#  utility functions
def validate_binary(s):
    return all(c in '01' for c in s) and len(s) > 0


def binary_addition(a, b):
    max_len = max(len(a), len(b))
    a = a.zfill(max_len)
    b = b.zfill(max_len)

    result = ''
    carry = 0

    for i in range(max_len - 1, -1, -1):
        total = carry + int(a[i]) + int(b[i])
        result = str(total % 2) + result
        carry = total // 2

    # Wraparound carry (end-around carry)
    if carry:
        result = binary_addition(result, '1'.zfill(len(result)))

    return result


def ones_complement(binary):
    return ''.join('1' if bit == '0' else '0' for bit in binary)


def inject_errors(data_blocks, num_errors=1):
    blocks = [list(b) for b in data_blocks]
    flips = []

    all_positions = [
        (bi, bpos)
        for bi, block in enumerate(blocks)
        for bpos in range(len(block))
    ]

    chosen = random.sample(all_positions, min(num_errors, len(all_positions)))

    for bi, bpos in chosen:
        blocks[bi][bpos] = '1' if blocks[bi][bpos] == '0' else '0'
        flips.append((bi, bpos))

    return [''.join(b) for b in blocks], flips



#  sender side

def sender(data_blocks, block_size, verbose=True):
    if verbose:
        divider()
        print("  SENDER SIDE")
        divider()
        print(f"  Block size : {block_size} bits")
        print(f"  Blocks     : {len(data_blocks)}\n")
        for i, block in enumerate(data_blocks):
            print(f"  Block {i+1:>2}   :  {block}")

    # Step 1: Sum all blocks
    running_sum = data_blocks[0]
    if verbose:
        print(f"\n  [Step 1] Binary Addition (end-around carry)\n")
        print(f"  Start      :  {running_sum}")

    for i in range(1, len(data_blocks)):
        prev_sum = running_sum
        running_sum = binary_addition(running_sum, data_blocks[i])
        if verbose:
            print(f"  + Block {i+1:<2}  :  {data_blocks[i]}")
            print(f"  = Sum      :  {running_sum}")
            if i < len(data_blocks) - 1:
                print()

    if verbose:
        print(f"\n  Final Sum  :  {running_sum}")

    # Step 2: One's complement → checksum
    checksum = ones_complement(running_sum)

    if verbose:
        print(f"\n  [Step 2] One's Complement of Sum")
        print(f"  Sum        :  {running_sum}")
        print(f"  Checksum   :  {checksum}  ← sent along with data\n")

    return checksum, running_sum


#  receiver side

def receiver(received_blocks, checksum, block_size, verbose=True):
    if verbose:
        divider()
        print("  RECEIVER SIDE")
        divider()
        print(f"  Received {len(received_blocks)} block(s) + checksum\n")
        for i, block in enumerate(received_blocks):
            print(f"  Block {i+1:>2}   :  {block}")
        print(f"  Checksum   :  {checksum}\n")

    # Step 1: Sum all received blocks
    running_sum = received_blocks[0]
    if verbose:
        print(f"  [Step 1] Add all received blocks\n")
        print(f"  Start      :  {running_sum}")

    for i in range(1, len(received_blocks)):
        running_sum = binary_addition(running_sum, received_blocks[i])
        if verbose:
            print(f"  + Block {i+1:<2}  :  {received_blocks[i]}")
            print(f"  = Sum      :  {running_sum}")

    # Step 2: Add checksum
    final_sum = binary_addition(running_sum, checksum)
    if verbose:
        print(f"\n  [Step 2] Add checksum to total\n")
        print(f"  Sum        :  {running_sum}")
        print(f"  + Checksum :  {checksum}")
        print(f"  = Final    :  {final_sum}\n")

    # Step 3: Check
    no_error = all(bit == '1' for bit in final_sum)
    if verbose:
        print(f"  [Step 3] Verification")
        if no_error:
            print(f"  Result     :  {final_sum}  ← all 1s")
            print(f"  ✓  NO ERROR — Data received correctly.\n")
        else:
            print(f"  Result     :  {final_sum}  ← not all 1s")
            print(f"  ✗  ERROR DETECTED — Data was corrupted!\n")

    return no_error


#  display

def divider(char='─', width=52):
    print(f"  {''.join([char] * width)}")


def banner():
    print()
    divider('═')
    print("  CHECKSUM GENERATOR AND VALIDATOR")
    print("  Error Detection in Data Communication")
    divider('═')
    print()


def show_transmission(data_blocks, checksum):
    divider()
    print("  TRANSMISSION PACKET")
    divider()
    print(f"  Payload  :  {' | '.join(data_blocks)}")
    print(f"  Checksum :  {checksum}")
    print()


def show_channel(original, received, flips):
    divider()
    print("  CHANNEL (Noise Simulation)")
    divider()
    if not flips:
        print("  Channel is clean — no bits flipped.\n")
    else:
        print(f"  {len(flips)} bit(s) flipped by noise:\n")
        for bi, bpos in flips:
            orig_bit = original[bi][bpos]
            recv_bit = received[bi][bpos]
            print(f"  Block {bi+1}, bit {bpos}: {orig_bit} → {recv_bit}")
        print(f"\n  Original : {' | '.join(original)}")
        print(f"  Received : {' | '.join(received)}\n")


def show_summary(runs):
    divider('═')
    print("  TEST SUMMARY")
    divider('═')
    for i, (label, result) in enumerate(runs, 1):
        status = "✓ PASS (no error detected)" if result else "✗ FAIL (error detected)"
        print(f"  Test {i}: {label:<30} {status}")
    print()



#  input handler

def get_block_size():
    while True:
        try:
            size = int(input("  Enter block size in bits (e.g., 8): ").strip())
            if size < 1:
                print("  Block size must be at least 1.")
                continue
            return size
        except ValueError:
            print("  Please enter a valid integer.")


def get_num_blocks():
    while True:
        try:
            n = int(input("  Enter number of data blocks (min 2): ").strip())
            if n < 2:
                print("  At least 2 blocks are required.")
                continue
            return n
        except ValueError:
            print("  Please enter a valid integer.")


def get_data_blocks(n, block_size):
    print(f"\n  Enter {n} binary blocks, each exactly {block_size} bits:\n")
    blocks = []
    for i in range(n):
        while True:
            val = input(f"  Block {i+1}: ").strip()
            if not validate_binary(val):
                print(f"  Error: only 0s and 1s allowed.")
            elif len(val) != block_size:
                print(f"  Error: must be exactly {block_size} bits (got {len(val)}).")
            else:
                blocks.append(val)
                break
    return blocks


def get_noise_preference():
    print("\n  Simulate a noisy channel?")
    choice = input("  Enter 'y' for yes, any other key for no: ").strip().lower()
    if choice == 'y':
        while True:
            try:
                n = int(input("  How many bits to flip? ").strip())
                if n < 1:
                    print("  At least 1.")
                    continue
                return n
            except ValueError:
                print("  Please enter a valid number.")
    return 0



def run_interactive():
    banner()

    block_size = get_block_size()
    num_blocks = get_num_blocks()
    data_blocks = get_data_blocks(num_blocks, block_size)
    num_flips = get_noise_preference()

    print()
    results = []

    # Sender
    checksum, _ = sender(data_blocks, block_size, verbose=True)
    show_transmission(data_blocks, checksum)

    # Channel
    if num_flips > 0:
        corrupted, flips = inject_errors(data_blocks, num_errors=num_flips)
        show_channel(data_blocks, corrupted, flips)
        label = f"Noisy channel ({num_flips} flip(s))"
        ok = receiver(corrupted, checksum, block_size, verbose=True)
    else:
        print("  [Channel] Clean — no bits flipped.\n")
        label = "Clean channel"
        ok = receiver(data_blocks, checksum, block_size, verbose=True)

    results.append((label, ok))
    show_summary(results)



def main():
    run_interactive()


if __name__ == "__main__":
    main()