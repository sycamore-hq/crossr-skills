# Tokio runtime

SOLE OWNER of worker fairness, schedule latency, and locks that can park a Tokio worker. RS owns off-runtime alloc/unsafe/secrets and does not restate these. RS-05 does not apply on a worker thread.

## Rules

RY-01  Work backward from a user-facing metric. A long poll is not a defect by itself.

RY-02  Yield between immediately-ready units when the goal is multi-tenant latency.
       Batch the same work when the goal is throughput.

RY-03  Batch filesystem and other blocking work into the largest sensible `spawn_blocking` segment.
       Do not sprinkle `tokio::fs` calls.
       check: rg 'tokio::fs::' --glob '*.rs' → review each hit

RY-04  Do not spawn a task whose useful work is measured in microseconds.

RY-05  Treat the blocking pool and the global queue as contended globals.
       Do not flood them from outside a worker.

RY-06  Never hold a blocking mutex, `parking_lot` lock, or `RwLock` across I/O, flush, or `.await` on a Tokio worker.
       `tokio::sync::Mutex` only when the critical section lasts milliseconds.

RY-07  Bound task fan-out with a `Semaphore`. Unbounded spawn against a downstream is a defect.

RY-08  Pin Tokio workers off cores that run other processes or long non-yielding Rust threads.

RY-09  Do not block inside `join!` or `select!`. There is no work-stealing inside a task.

## How

Tokio performance is fairness versus batching. Diagnose from the metric you ship and from `RuntimeMetrics::schedule_latency_histogram`. Most incidents blamed on Tokio are application code, often across a distributed boundary. Folded from Russell / dial9, *Principles for fast Tokio applications* (2026-09-13), and Alice Ryhl, *What is Blocking?*.

A poll is the work between `.await` points. Alice's 10–100 µs budget is a starting point. Under light load, work stealing hides a long poll. It stops hiding when the runtime is saturated or the kernel is slow to unpark a worker. `join!` and `select!` have no steal: blocking that task blocks every sibling.

Pipelined reads that stay `Poll::Ready` starve other connections. Yield after the unit of work. A ready-run of about four immediately-ready frames is the usual fairness/throughput trim. A real park resets the run.

```rust
async fn handle_conn(conn: &mut Conn) -> Result<(), ConnError> {
    loop {
        let frame = conn.read_frame().await?;
        exec(&frame).await?;
        tokio::task::yield_now().await;
    }
}
```

`tokio::fs` without io_uring is `spawn_blocking` per call. Group the syscalls. A 10 µs task of its own is anti-helpful: more polls, more schedule delay, more global-queue chances. The blocking pool has been a single queue (Tokio 1.52.0's shard landed and was reverted in 1.52.1). About 50k blocking tasks/s on a 32-core host is a published saturation point, not a budget.

A metrics registry behind a mutex that flushes while holding the lock will park every worker that records a point. Keep the critical section to one map update. `RwLock` still contends on the atomic and is the wrong primitive on a worker. RS-05 is off-runtime guidance. `tokio::sync::Mutex` is heavier and has FutureLock-shaped hazards; use it only when the section itself is milliseconds.

Fan-out is a Semaphore, not hope. Pin Tokio workers off Java leftovers, `tracing_appender` threads that run 100 ms without yield, and any other tenant of the box. You rarely need every core for Tokio.

Two further moves are exceptions, not defaults. Split latency-sensitive work onto its own runtime (and niceness) when background work shares the host. Spin a reserved core for tens of microseconds only when the SLO is measured in microseconds.

Mental model: futures progress only while polled; idle futures wait; N workers each own a local queue and overflow to the global queue; a worker steals only if it is running and the runtime notices the imbalance.
