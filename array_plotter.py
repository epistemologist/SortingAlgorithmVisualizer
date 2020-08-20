from functools import total_ordering
from copy import copy, deepcopy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import time

import matplotlib
matplotlib.use('TkAgg')


SWAP_COLOR = "yellow"
ACCESS_COLOR = "green"
COMPARE_COLOR = "red"
INSERT_COLOR = "purple"
DEFAULT_COLOR = "blue"

class Array:
    "Class that stores an array as well as implementing special methods and keeping track of various statistics"

    def __init__(self, array, labels = None, verbose = False):
        self.array = [ArrayElement(array[i], self, i)
                      for i in range(len(array))]
        self.permutation = list(range(len(array)))
        self.accesses = 0
        self.comparisons = 0
        self.swaps = 0
        self.labels = labels
        self.verbose = verbose
        self.start_time = time()
        self.history = []
        self.history.append(self.summary())

    def __repr__(self):
        return str(self.array)

    def __len__(self):
        return len(self.array)

    def __iter__(self):
        return iter(self.array)
        
    def __getitem__(self, key):
        try:
            out = self.array[key]
            self.accesses += 1
            if self.verbose: self.history.append(self.summary(action={
                "type":"access",
                "args": key
            }))
            return out
        except Exception as e:
            raise ValueError("invalid index!")

    def __setitem__(self, key, value):
        if key < 0 or key >= len(self.array):
            raise ValueError("invalid index!")
        self.array[key] = value
        self.update_permutation()
        self.history.append(self.summary(action = {
            "type": "insert",
            "args": (key,value)
        }))

    def swap(self, index1, index2):
        try:
            self[index1], self[index2] = self[index2], self[index1]
            self.swaps += 1
            self.history.append(self.summary(action = {
                "type": "swap",
                "args": (index1, index2)
            }))
        except:
            raise ValueError("invalid index!")

    def compare(self, elem1, elem2):
        self.comparisons += 1
        index1, index2 = None, None
        try:
            for i in range(len(self.array)):
                if self.array[i].index == elem1.index:
                    index1 = i
                    break
        except:
            pass
        try:
            for i in range(len(self.array)):
                if self.array[i].index == elem2.index:
                    index2 = i
                    break
        except:
            pass
        self.history.append(self.summary(action = {
            "type": "compare",
            "args": (index1, index2)
        }))

    def summary(self, action={"type": "none"}):
        out = dict()
        out["array"] = copy(self.array)
        out["accesses"] = self.accesses
        out["comparisons"] = self.comparisons
        out["swaps"] = self.swaps
        out["labels"] = copy(self.labels)
        out["action"] = action
        out["permutation"] = copy(self.permutation)
        out["time"] = time() - self.start_time
        return out

    def update_permutation(self):
        self.permutation = [i.index for i in self.array]

@total_ordering
class ArrayElement:
    """
    Class that stores an element of an array which also keeps track of comparisons
    """

    def __init__(self, element, array, index):
        self.element = element
        self.array = array
        self.index = index

    def __repr__(self):
        return str(self.element)

    def __int__(self):
        return self.element

    def __eq__(self, other):
        self.array.compare(self, other)
        return self.element == other.element

    def __lt__(self, other):
        self.array.compare(self, other)
        return self.element < other.element



def plot_frame(frame, filename):
    fig, ax = plt.subplots(figsize=(20,6))
    bars = [int(i) for i in frame["array"]]
    summary_string = "array acceses: " + str(frame["accesses"]) + "\n" + \
        "comparisons: " + str(frame["comparisons"]) + "\n" + \
        "swaps: " + str(frame["swaps"]) + "\n" + \
        "elapsed time (s): " + str(frame["time"])
    bars_colors = [DEFAULT_COLOR for i in range(len(bars))]
    if frame["action"]["type"] == "access":
        key = frame["action"]["args"]
        bars_colors[key] = ACCESS_COLOR
    if frame["action"]["type"] == "insert":
        key, _ = frame["action"]["args"]
        bars_colors[key] = INSERT_COLOR
    if frame["action"]["type"] == "swap":
        index1, index2 = frame["action"]["args"]
        bars_colors[index1] = SWAP_COLOR
        bars_colors[index2] = SWAP_COLOR
    if frame["action"]["type"] == "compare":
        index1, index2 = frame["action"]["args"]
        if index1: bars_colors[index1] = COMPARE_COLOR
        if index2: bars_colors[index2] = COMPARE_COLOR
    ax.text(0.5,1.01, summary_string, size=10, color="black", transform = ax.transAxes)
    ax.bar(range(len(bars)), bars, color = bars_colors, edgecolor = "black", linewidth=1)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.savefig(filename)
    plt.close("all")

def plot_history_bar(frames):
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10,4))
    def animate(i):
        print(i)
        frame = frames[i]
        bars = [int(j) for j in frame["array"]]
        summary_string = "array acceses: " + str(frame["accesses"]) + "\n" + \
            "comparisons: " + str(frame["comparisons"]) + "\n" + \
            "swaps: " + str(frame["swaps"]) + "\n" + \
            "elapsed time (s): " + str(frame["time"])
        bars_colors = [DEFAULT_COLOR for i in range(len(bars))]
        if frame["action"]["type"] == "access":
            key = frame["action"]["args"]
            bars_colors[key] = ACCESS_COLOR
        if frame["action"]["type"] == "insert":
            key, _ = frame["action"]["args"]
            bars_colors[key] = INSERT_COLOR
        if frame["action"]["type"] == "swap":
            index1, index2 = frame["action"]["args"]
            bars_colors[index1] = SWAP_COLOR
            bars_colors[index2] = SWAP_COLOR
        if frame["action"]["type"] == "compare":
            index1, index2 = frame["action"]["args"]
            if index1: bars_colors[index1] = COMPARE_COLOR
            if index2: bars_colors[index2] = COMPARE_COLOR
        ax.clear()
        ax.text(0.5,1.01, summary_string, size=8, color="white", transform = ax.transAxes)
        ax.bar(range(len(bars)), bars, color = bars_colors, edgecolor = "black", linewidth=1)
        ax.set_xticks([])
        ax.set_yticks([])
    anim = FuncAnimation(fig, animate, interval = 100, frames = len(frames))
    return anim

def plot_history_line(frames):
    arr = [int(j) for j in frames[0]["array"]]
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize = (10,4))
    line = ax.plot(arr)[0]
    text = ax.text(0.5,1.01,"",size=8,color="white", transform=ax.transAxes)
    ax.set_xlim(0, 1.1*len(arr))
    ax.set_ylim(0, 1.1*max(arr))
    ax.set_xticks([])
    ax.set_yticks([])
    def animate(i):
        print(i)
        frame = frames[i]
        pts = [int(j) for j in frame["array"]]
        summary_string = "array acceses: " + str(frame["accesses"]) + "\n" + \
            "comparisons: " + str(frame["comparisons"]) + "\n" + \
            "swaps: " + str(frame["swaps"]) + "\n" + \
            "elapsed time (s): " + str(frame["time"])
        text.set_text(summary_string)
        line.set_ydata(pts)
    anim = FuncAnimation(fig, animate, interval = 10, frames = len(frames))
    return anim

# Various sorting algorithms


def selection_sort(arr):
    for i in range(len(arr)):
        min_id = i
        for j in range(i+1, len(arr)):
            if arr[min_id] > arr[j]:
                min_id = j
        arr.swap(i, min_id)

def insertion_sort_efficient(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key < arr[j]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key


arr = Array([i+1 for i in reversed(range(20))],verbose=False)
print(arr)
selection_sort(arr)
print(len(arr.history))
test = plot_history_bar(arr.history)
test.save("selection.avi")