import csv
import hashlib
import time
import statistics


def mine_block(block_data, difficulty):
    prefix = "0" * difficulty
    nonce = 0
    start = time.perf_counter()

    while True:
        text = f"{block_data}{nonce}"
        hash_result = hashlib.sha256(text.encode()).hexdigest()
        if hash_result.startswith(prefix):
            elapsed = time.perf_counter() - start
            return {
                "hash": hash_result,
                "nonce": nonce,
                "attempts": nonce + 1,
                "time": elapsed
            }
        nonce += 1


def run_experiment(difficulty, num_blocks=30):
    results = []
    for i in range(num_blocks):
        block_data = f"Block-{i}-{difficulty}"
        result = mine_block(block_data, difficulty)
        results.append(result)
    return results


def summarize(results):
    times = [r["time"] for r in results]
    attempts = [r["attempts"] for r in results]
    total_time = sum(times)
    total_attempts = sum(attempts)
    return {
        "avg_time": statistics.mean(times),
        "min_time": min(times),
        "max_time": max(times),
        "std_time": statistics.stdev(times) if len(times) > 1 else 0.0,
        "avg_attempts": statistics.mean(attempts),
        "throughput": total_attempts / total_time if total_time > 0 else 0.0,
    }


if __name__ == "__main__":
    difficulties = [2, 3, 4, 5]
    summary_table = []
    all_rows = []

    for diff in difficulties:
        print(f"\n=== Mining 30 blocks at difficulty {diff} ===")
        results = run_experiment(diff, num_blocks=30)

        # record every block (valid hash, attempts, time) in a CSV file
        for i, r in enumerate(results):
            all_rows.append([diff, i, r["hash"], r["nonce"], r["attempts"], f"{r['time']:.6f}"])

        # show the first 3 blocks as examples
        for i, r in enumerate(results[:3]):
            print(f"Block {i}: hash={r['hash']} | attempts={r['attempts']} | time={r['time']:.6f}s")
        print("... (all 30 blocks are saved in mining_results.csv)")

        stats = summarize(results)
        stats["difficulty"] = diff
        summary_table.append(stats)

        print(f"Average time: {stats['avg_time']:.6f}s | "
              f"Min: {stats['min_time']:.6f}s | Max: {stats['max_time']:.6f}s | "
              f"StdDev: {stats['std_time']:.6f}s | "
              f"Throughput: {stats['throughput']:.0f} H/s")

    with open("mining_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["difficulty", "block", "hash", "nonce", "attempts", "time_s"])
        writer.writerows(all_rows)

    print("\n\n=== Summary Table ===")
    header = (f"{'Difficulty':<12}{'Avg(s)':<12}{'Min(s)':<12}{'Max(s)':<12}{'StdDev(s)':<12}"
              f"{'Avg Attempts':<14}{'Expected 16^d':<15}{'Throughput(H/s)':<16}")
    print(header)
    for s in summary_table:
        print(f"{s['difficulty']:<12}{s['avg_time']:<12.6f}{s['min_time']:<12.6f}"
              f"{s['max_time']:<12.6f}{s['std_time']:<12.6f}{s['avg_attempts']:<14.1f}"
              f"{16 ** s['difficulty']:<15}{s['throughput']:<16.0f}")

    print("\n=== Growth between difficulty levels ===")
    for prev, cur in zip(summary_table, summary_table[1:]):
        print(f"Difficulty {prev['difficulty']} -> {cur['difficulty']}: "
              f"time x{cur['avg_time'] / prev['avg_time']:.1f}, "
              f"attempts x{cur['avg_attempts'] / prev['avg_attempts']:.1f}")