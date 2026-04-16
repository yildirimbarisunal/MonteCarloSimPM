# Project Simulation: PERT + Monte Carlo Scheduling Engine

##  Overview

This project is a simulation-based project scheduling tool that estimates total project duration under uncertainty. It combines **PERT estimation**, **Monte Carlo simulation**, and **dependency-aware scheduling (topological sorting)** to model real-world project variability.

Instead of producing a single fixed project duration, the system generates a distribution of possible outcomes and performs statistical analysis on them (mean, min, max, P50, P90).

---

##  Key Features

-  PERT-based task duration modeling
-  Monte Carlo simulation for uncertainty analysis
-  Dependency-aware task scheduling (Topological Sort / DAG processing)
-  Statistical analysis of simulation results (mean, percentiles, min/max)
-  Modular task-based architecture

---

##  Methodology

### 1. Task Modeling (PERT)

Each task is defined with three time estimates:
- Optimistic (best case)
- Most likely (expected case)
- Pessimistic (worst case)

These values are used to model uncertainty in task duration.

---

### 2. Stochastic Simulation (Monte Carlo)

Instead of using a single fixed duration, each task duration is sampled using a **triangular distribution**, simulating realistic variability across multiple iterations.

The project is simulated thousands of times to generate a distribution of total completion times.

---

### 3. Dependency Handling

Tasks may depend on other tasks. A **topological sorting algorithm (DFS-based)** is used to ensure that all dependencies are resolved before execution order is determined.

---

### 4. Statistical Analysis

After simulation, results are analyzed using:

- Mean (average project duration)
- Minimum / Maximum values
- P50 (median scenario)
- P90 (high-confidence planning estimate)

These metrics help evaluate both expected performance and risk.

---

##  Output Example

```text
Mean: 42.3 days
Min: 35 days
Max: 55 days
P50: 41 days
P90: 48 days
