import time
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


def run_benchmark(
    time_cost: int, memory_cost: int, parallelism: int, iterations: int = 5
):
    print("Benchmarking Argon2id with:")
    print(f" - Time cost: {time_cost}")
    print(f" - Memory cost: {memory_cost} KiB")
    print(f" - Parallelism: {parallelism}")

    password_hash = PasswordHash(
        (
            Argon2Hasher(
                time_cost=time_cost,
                memory_cost=memory_cost,
                parallelism=parallelism,
            ),
        )
    )

    total_time = 0.0
    for i in range(iterations):
        start = time.perf_counter()
        hashed = password_hash.hash(f"benchmark_password_{i}")  # noqa: F841
        end = time.perf_counter()

        duration = end - start
        total_time += duration
        print(f" Iteration {i + 1}: {duration:.4f} seconds")

    avg_time = total_time / iterations
    print(f"\nAverage time per hash: {avg_time:.4f} seconds ({avg_time * 1000:.1f} ms)")

    if 0.200 <= avg_time <= 0.500:
        print("RESULT: WITHIN TARGET (200-500ms)")
    elif avg_time < 0.200:
        print("RESULT: TOO FAST (Increase costs)")
    else:
        print("RESULT: TOO SLOW (Decrease costs)")


if __name__ == "__main__":
    run_benchmark(time_cost=3, memory_cost=65536, parallelism=1, iterations=5)
