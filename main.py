import random
import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
import matplotlib.pyplot as plt



class Task:
    def __init__(self, name, optimistic_time, most_likely, pessimistic_time, dependencies=None):
        self.name = name
        self.optimistic = float(optimistic_time)
        self.most_likely = float(most_likely)
        self.pessimistic = float(pessimistic_time)
        self.dependencies = dependencies if dependencies else []

        # runtime
        self.duration = 0
        self.start_time = 0
        self.finish_time = 0

    def generate_duration(self):
        self.duration = random.triangular(
            self.optimistic,
            self.pessimistic,
            self.most_likely
        )
        return self.duration



def topological_sort(tasks):
    task_map = {t.name: t for t in tasks}
    visited = set()
    order = []

    def visit(task):
        if task.name in visited:
            return
        visited.add(task.name)

        for d in task.dependencies:
            visit(task_map[d])

        order.append(task)

    for t in tasks:
        visit(t)

    return order


def single_simulation(tasks, critical_counter=None):
    order = topological_sort(tasks)
    task_map = {t.name: t for t in tasks}

    for t in tasks:
        t.start_time = 0
        t.finish_time = 0
        t.generate_duration()

    for task in order:
        if not task.dependencies:
            task.start_time = 0
        else:
            task.start_time = max(
                task_map[d].finish_time for d in task.dependencies
            )

        task.finish_time = task.start_time + task.duration

    project_duration = max(t.finish_time for t in tasks)

    # critical path detection
    critical_tasks = [
        t.name for t in tasks
        if abs(t.finish_time - project_duration) < 1e-6
    ]

    if critical_counter is not None:
        for name in critical_tasks:
            critical_counter[name] += 1

    return tasks, project_duration



def run_simulation(tasks, iterations):
    results = []
    critical_counter = defaultdict(int)
    last_run = None

    for _ in range(iterations):
        cloned = [
            Task(t.name, t.optimistic, t.most_likely, t.pessimistic, list(t.dependencies))
            for t in tasks
        ]

        sim_tasks, duration = single_simulation(cloned, critical_counter)
        results.append(duration)
        last_run = sim_tasks

    return results, critical_counter, last_run



def analyze(results):
    results.sort()
    n = len(results)

    return {
        "mean": sum(results) / n,
        "min": results[0],
        "max": results[-1],
        "p50( likely scenario)": results[int(0.5 * n)],
        "p90( guarantee scenario)": results[int(0.9 * n)]
    }


def analyze_criticality(counter, iteration):
    return {
        k: v / iteration
        for k, v in counter.items()
    }


def show_gantt(tasks):
    fig, ax = plt.subplots()

    colors = plt.cm.tab10.colors
    color_map = {}

    # assign color per task
    for i, t in enumerate(tasks):
        color_map[t.name] = colors[i % len(colors)]

    for t in tasks:
        ax.barh(
            t.name,
            t.duration,
            left=t.start_time,
            color=color_map[t.name]
        )


    handles = [
        plt.Rectangle((0, 0), 1, 1, color=color_map[name])
        for name in color_map
    ]

    ax.legend(handles, color_map.keys(), title="Tasks")

    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart")
    plt.show()



class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Monte Carlo Project Planner")

        self.tasks = []

        # INPUT
        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Label(frame, text="Task").grid(row=0, column=0)
        tk.Label(frame, text="O").grid(row=0, column=1)
        tk.Label(frame, text="M").grid(row=0, column=2)
        tk.Label(frame, text="P").grid(row=0, column=3)
        tk.Label(frame, text="Deps").grid(row=0, column=4)

        self.name = tk.Entry(frame)
        self.o = tk.Entry(frame)
        self.m = tk.Entry(frame)
        self.p = tk.Entry(frame)
        self.dep = tk.Entry(frame)

        self.name.grid(row=1, column=0)
        self.o.grid(row=1, column=1)
        self.m.grid(row=1, column=2)
        self.p.grid(row=1, column=3)
        self.dep.grid(row=1, column=4)

        tk.Button(frame, text="Add Task", command=self.add_task).grid(row=1, column=5)

        # TABLE
        self.tree = ttk.Treeview(root, columns=("O", "M", "P", "Deps"), show="headings")
        self.tree.heading("O", text="O")
        self.tree.heading("M", text="M")
        self.tree.heading("P", text="P")
        self.tree.heading("Deps", text="Deps")
        self.tree.pack()

        # SIMULATION
        sim_frame = tk.Frame(root)
        sim_frame.pack(pady=10)

        self.iter_entry = tk.Entry(sim_frame)
        self.iter_entry.insert(0, "1000")

        self.iter_entry.pack(side=tk.LEFT)

        tk.Button(sim_frame, text="Run", command=self.run).pack(side=tk.LEFT)
        tk.Button(sim_frame, text="Gantt", command=self.gantt).pack(side=tk.LEFT)

    def add_task(self):
        task = Task(
            self.name.get(),
            self.o.get(),
            self.m.get(),
            self.p.get(),
            self.dep.get().split(",") if self.dep.get() else []
        )

        self.tasks.append(task)

        self.tree.insert("", "end", values=(
            task.optimistic,
            task.most_likely,
            task.pessimistic,
            ",".join(task.dependencies)
        ))

    def run(self):
        iterations = int(self.iter_entry.get())

        results, critical_counter, last_run = run_simulation(self.tasks, iterations)
        stats = analyze(results)
        criticality = analyze_criticality(critical_counter, iterations)

        # RESULT TEXT
        msg = "PROJECT STATS\n\n"
        for k, v in stats.items():
            msg += f"{k}: {v:.2f}\n"

        msg += "\nCRITICAL PATH ANALYSIS\n"
        for k, v in sorted(criticality.items(), key=lambda x: -x[1]):
            msg += f"{k}: {v*100:.1f}%\n"

        messagebox.showinfo("Results", msg)

        self.last_run = last_run

    def gantt(self):
        if hasattr(self, "last_run"):
            show_gantt(self.last_run)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()