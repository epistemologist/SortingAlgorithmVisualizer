from functools import total_ordering
from copy import copy, deepcopy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import time
from math import log2, log
import colorsys

import matplotlib
matplotlib.use('TkAgg')


SWAP_COLOR = "yellow"
ACCESS_COLOR = "green"
COMPARE_COLOR = "red"
INSERT_COLOR = "blue"
DEFAULT_COLOR = "white"
FINISH_COLOR = "lime"

class Array:
    "Class that stores an array as well as implementing special methods and keeping track of various statistics"

    def __init__(self, array, labels = None, verbose = False):
        self.array = [ArrayElement(array[i], self, i)
                      for i in range(len(array))]
        self.permutation = list(range(len(array)))
        self.accesses = 0
        self.comparisons = 0
        self.swaps = 0
        self.labels = labels # labels will be an array with same length as given array where labels[i] is the color of array[i], else None
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

    def swap(self, index1, index2, silent=False):
        try:
            if not silent: self[index1], self[index2] = self[index2], self[index1]
            if silent: self.array[index1], self.array[index2] = self.array[index2], self.array[index1]
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

    def finish(self):
        labels = [None for i in range(len(self.array))]
        for i in range(len(labels)):
            labels[i] = FINISH_COLOR
            self.labels = labels
            self.history.append(self.summary())

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
    ax.text(0.5,1.01, summary_string, size=14, color="black", transform = ax.transAxes)
    ax.bar(range(len(bars)), bars, color = bars_colors, edgecolor = "black", linewidth=1)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.savefig(filename)
    plt.close("all")

def plot_history_bar(frames, name = ""):
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10,10))
    def animate(i):
        print(i)
        frame = frames[i]
        bars = [int(j) for j in frame["array"]]
        summary_string = "array acceses: " + str(frame["accesses"]) + "\n" + \
            "comparisons: " + str(frame["comparisons"]) + "\n" + \
            "swaps: " + str(frame["swaps"]) + "\n" + \
            "elapsed time (s): " + str(frame["time"])
        bars_colors = [DEFAULT_COLOR for i in range(len(bars))]
        if frame["labels"]:
            for i in range(len(frame["labels"])):
                if frame["labels"][i]:
                    bars_colors[i] = frame["labels"][i]
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
        ax.text(0.5,-0.1, name, size=28, color="white", transform = ax.transAxes)
        ax.bar(range(len(bars)), bars, color = bars_colors, edgecolor = "black", linewidth=1)
        ax.set_xticks([])
        ax.set_yticks([])
    anim = FuncAnimation(fig, animate, interval = 100, frames = len(frames))
    return anim

def plot_history_line(frames):
    arr = [int(j) for j in frames[0]["array"]]
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize = (10,10))
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

def plot_history_scatter(frames):
    y = [int(j) for j in frames[0]["array"]]
    x = range(len(y))
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize = (10,4))
    scatter = ax.scatter(x,y)
    text = ax.text(0.5,1.01,"",size=8,color="white", transform=ax.transAxes)
    ax.set_xlim(0, 1.1*len(y))
    ax.set_ylim(0, 1.1*max(y))
    ax.set_xticks([])
    ax.set_yticks([])
    def animate(i):
        print(i)
        frame = frames[i]
        pts = [[i,int(frame["array"][i])] for i in range(len(frame["array"]))]
        summary_string = "array acceses: " + str(frame["accesses"]) + "\n" + \
            "comparisons: " + str(frame["comparisons"]) + "\n" + \
            "swaps: " + str(frame["swaps"]) + "\n" + \
            "elapsed time (s): " + str(frame["time"])
        text.set_text(summary_string)
        scatter.set_offsets(pts)
    anim = FuncAnimation(fig, animate, interval = 10, frames = len(frames))
    return anim

# Various sorting algorithms


def selection_sort(arr, finish=False):
    for i in range(len(arr)):
        min_id = i
        for j in range(i+1, len(arr)):
            if arr[min_id] > arr[j]:
                min_id = j
        arr.swap(i, min_id)
    if finish: arr.finish()

def insertion_sort(arr, finish=False):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key < arr[j]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    if finish: arr.finish()

def bubble_sort(arr, finish=False):
    for i in range(len(arr)):
        for j in range(len(arr)-i-1):
            if arr[j] > arr[j+1]:
                arr.swap(j,j+1)
    if finish: arr.finish()

def slow_sort(arr, finish=False):
    def slow_sort_(arr, i, j):
        if i >= j: return
        m = int(0.5 * (i+j))
        slow_sort_(arr, i, m)
        slow_sort_(arr, m+1, j)
        if arr[j] < arr[m]:
            arr.swap(j,m)
        slow_sort_(arr,i,j-1)
    slow_sort_(arr, 0, len(arr)-1)
    if finish: arr.finish()

def stooge_sort(arr, finish=False):
    def stooge_sort_(arr, i, j):
        if arr[i] > arr[j]:
            arr.swap(i,j)
        if (j-i+1) > 2:
            t = (j-i+1)/3
            stooge_sort_(arr,i,j-t)
            stooge_sort_(arr,i+t,j)
            stooge_sort_(arr,i,j-t)
        return arr
    stooge_sort_(arr, 0, len(arr)-1)
    if finish: arr.finish()

def quick_sort(arr, finish=False, label=True):
    LO_COLOR = "#ff00aa"
    HI_COLOR = "#00ffa0"
    PART_COLOR = "#00ffff"
    labels = None
    if label: 
        arr.labels = [None for i in range(len(arr))]
    def quick_sort_(arr,lo,hi):
        if label and lo < hi: 
            arr.labels = [None for i in range(len(arr))]
            arr.labels[lo] = LO_COLOR
            arr.labels[hi] = HI_COLOR
        if lo < hi:
            p = partition_(arr,lo,hi)
            if arr.labels: arr.labels[p] = PART_COLOR
            quick_sort_(arr,lo,p-1)
            quick_sort_(arr,p+1,hi)
    def partition_(arr,lo,hi):
        pivot = arr[hi]
        i = lo
        for j in range(lo,hi+1):
            if arr[j] < pivot:
                arr.swap(i,j)
                i += 1
        arr.swap(i,hi)
        return i
    quick_sort_(arr,0,len(arr)-1)
    if finish: arr.finish()

def shell_sort(arr, finish=False):
    gaps = [701, 301, 132, 57, 23, 10, 4, 1]
    for gap in gaps:
        for i in range(gap,len(arr)):
            temp = arr[i]
            j = i
            while j >= gap and arr[j-gap] > temp:
                arr[j] = arr[j-gap]
                j -= gap
            arr[j] = temp
    if finish: arr.finish()

def cocktail_sort(arr, finish=False):
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(arr)-1):
            if arr[i] > arr[i+1]:
                arr.swap(i,i+1)
                swapped = True
        if not swapped:
            break
        swapped = False
        for i in reversed(range(len(arr)-1)):
            if arr[i] > arr[i+1]:
                arr.swap(i,i+1)
                swapped = True
    if finish: arr.finish()

def odd_even_sort(arr, finish=False):
    sorted = False
    while not sorted:
        sorted = True
        for i in range(1,len(arr)-1,2):
            if arr[i] > arr[i+1]:
                arr.swap(i,i+1)
                sorted = False
        for i in range(0,len(arr)-1,2):
            if arr[i] > arr[i+1]:
                arr.swap(i,i+1)
                sorted = False
    if finish: arr.finish()

def comb_sort(arr, finish=False):
    gap = len(arr)
    shrink = 1.3
    sorted = False
    while not sorted:
        gap = int(gap/shrink)
        if gap <= 1:
            gap = 1
            sorted = True
        i = 0
        while i+gap < len(arr):
            if arr[i] > arr[i+gap]:
                arr.swap(i,i+gap)
                sorted=False
            i += 1
    if finish: arr.finish()

def gnome_sort(arr, finish=False):
    pos = 0
    while pos < len(arr):
        if pos == 0 or arr[pos] >= arr[pos-1]:
            pos += 1
        else:
            arr.swap(pos,pos-1)
            pos -= 1
    if finish: arr.finish()

def heap_sort(arr, finish=False, show_heap=False):
    def heapify(arr):
        start = parent(len(arr)-1)
        while start >= 0:
            sift_down(start, len(arr)-1)
            start -= 1
    def sift_down(start, end):
        root = start
        while left_child(root) <= end:
            child = left_child(root)
            swap = root
            if arr[swap] < arr[child]:
                swap = child
            if child+1 <= end and arr[swap] < arr[child+1]:
                swap = child+1
            if swap == root:
                return
            else:
                arr.swap(root,swap)
                root = swap
    parent = lambda i: int(0.5*(i-1))
    left_child = lambda i: 2*i+1
    right_child = lambda i: 2*i+2
    heapify(arr)
    if show_heap:
        indicies = [i for i in range(len(arr))]
        arr.labels = [None for i in range(len(arr))]
        print(list(enumerate([indicies[2**i:2**(i+1)] for i in range(0,int(log2(len(arr)))+2)])))
        for n, level in enumerate([indicies[2**i:2**(i+1)] for i in range(0,int(log2(len(arr)))+2)]):
            for i in level:
                arr.labels[i] = (0,1./(n+1),1./(n+1))
                arr.history.append(arr.summary())
    arr.labels = []
    end = len(arr)-1
    while end > 0:
        arr.swap(end, 0)
        end -= 1
        sift_down(0,end)
    if finish: arr.finish()

def merge_sort(arr,finish=False,labels=False):
    # Python translation of https://stackoverflow.com/a/15657134/9653799
    def wmerge(xs, i, m, j, n, w):
        if labels:
            xs.labels = [None for _ in range(len(xs))]
            for pos in range(i,m):
                xs.labels[pos] = "purple"
            for pos in range(j,n):
                xs.labels[pos] = "pink"
        # Merge two sorted subarrays xs[i, m) and xs[j, n) to working area xs[w...]
        while i < m and j < n:
            if xs[i] < xs[j]:
                xs.swap(w,i)
                i += 1
            else:
                xs.swap(w,j)
                j += 1
            w += 1
        while i < m:
            xs.swap(w,i)
            w += 1
            i += 1
        while j < n:
            xs.swap(w,j)
            w += 1
            j += 1
        xs.labels = None
    def wsort(xs, l, u, w):
        # sort xs[l,u) and put result to working area w
        # constraint, len(w) == u - 1
        if u-l > 1:
            m = l + (u-l)//2
            imsort(xs, l, m)
            imsort(xs, m, u)
            wmerge(xs, l, m, m, u, w)
        else:
            while l < u:
                xs.swap(l,w)
                l += 1
                w += 1

    def imsort(xs, l, u):
        if u-l > 1:
            m = l + (u-l)//2
            w = l + u - m
            wsort(xs, l, m, w)
            while (w - l > 2):
                n = w
                w = l + (n-l+1)//2
                wsort(xs, w, n, l)
                wmerge(xs, l, l+n-w, n, u, w)
            n = w
            while n > l:
                m = n
                while m < u and xs[m] < xs[m-1]:
                    xs.swap(m,m-1)
                    m += 1
                n -= 1
    imsort(arr, 0, len(arr))
    if finish: arr.finish()

def radix_sort(arr, base=10, labels=False, finish=False):
    if labels: arr.labels = [None for i in range(len(arr))]
    def pass_(arr, digit):
        buckets = [[0,0] for i in range(base)]
        buckets_ = [[] for i in range(base)]
        def add_to_bucket(index, bucket):
            buckets_[bucket].append(int(arr[index]))
            temp = buckets[bucket][1]
            while index > temp:
                arr.swap(index, temp)
                temp += 1
            buckets[bucket][1] += 1
            for i in range(bucket+1, len(buckets)):
                buckets[i][0] += 1
                buckets[i][1] += 1
        for i in range(len(arr)):
            #print(i, max(sum(buckets, [])))
            #print(arr[i], digit, int(int(arr[i])//(base**digit)) % base)
            add_to_bucket(i, int(int(arr[i])//(base**digit)) % base)
            if labels:
                for j,bucket in enumerate(buckets):
                    for index in range(bucket[0], bucket[1]):
                        arr.labels[index] = colorsys.hsv_to_rgb(j*1./len(buckets),0.5,1)
        arr.labels = [None for i in range(len(arr))]
    arr_copy = [int(i) for i in arr.array]
    for pos in range(1+int(1+log(max(arr_copy))/log(base))):
        pass_(arr, pos)
    if finish: arr.finish()
        


arr = Array(list(reversed(range(1,21))),verbose=False)
print(arr)
heap_sort(arr, finish=True, show_heap=True)
print(len(arr.history))
test = plot_history_bar(arr.history)
test.save("out4.mp4")
