import ROOT as rt
import numpy as np
import math
import THxxData
import THxxDataWithSyst
import copy
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator, LogLocator, NullFormatter, LogFormatter)
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

from helper import *

import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 0.5

class MatplotlibDrawer:

    def __init__(self, n_row=2, n_col=1, fig_size=(8,7), height_ratios=[1,0.3]):
        
        self.n_row = n_row
        self.n_col = n_col
        if self.n_row > 1 :
            self.fig, axes = plt.subplots(self.n_row, self.n_col, sharex=False, figsize=fig_size, gridspec_kw = {'height_ratios':height_ratios})
        else :
            self.fig, axes = plt.subplots(self.n_row, self.n_col, sharex=False, figsize=fig_size)
        plt.tight_layout()
        plt.subplots_adjust(left=0.15, right=0.9, bottom=0.1, top=0.9, hspace=0.0)
        
        self.axes = []
        self.labels_in_axes = []
        self.hists_in_axes = []
        
        self.color_map = {}
        
        if n_row > 1:
            for axe in axes:
                self.axes.append(axe)
                axe.tick_params(bottom=True, top=True, left=True, right=True, which='both', direction='in')
                self.labels_in_axes.append([])
                self.hists_in_axes.append([])

                axe.tick_params(length=10, which='major')
                axe.tick_params(length=5, which='minor')
        else:
            axes.tick_params(bottom=True, top=True, left=True, right=True, which='both', direction='in')
            self.axes.append(axes)
            self.labels_in_axes.append([])
            self.hists_in_axes.append([])

    def get_axes(self, i_row):
        return self.axes[i_row]
        
    def clear_axes(self, i_row):
        self.axes[i_row].clear()
        self.labels_in_axes[i_row].clear()
        self.hists_in_axes[i_row].clear()

    def set_log_xscale(self, i_row):
        self.axes[i_row].set_xscale("log")

    def set_log_yscale(self, i_row):
        self.axes[i_row].set_yscale("log")
        self.axes[i_row].yaxis.set_major_locator(LogLocator(10, numticks=14))
        self.axes[i_row].yaxis.set_minor_locator(LogLocator(10, subs=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9), numticks=14))
        
    def remove_xais_labels(self, i_row):
        self.axes[i_row].set_xticklabels([])

    def remove_first_tick_yaxis(self, i_row, prune='lower'):
        self.axes[i_row].yaxis.set_major_locator(MaxNLocator(prune=prune))

    def save_plot(self, out_name = "test"):
        self.fig.savefig(out_name, format="pdf", dpi=300)
        
    def set_y_range(self, i_row, y_min, y_max):
        self.axes[i_row].set_ylim(y_min, y_max)
        
    def set_x_range(self, i_row, x_min, x_max):
        self.axes[i_row].set_xlim(x_min, x_max)

    def write_yaxis_title(self, i_row, title):
        self.axes[i_row].set_ylabel(title, fontsize='xx-large', ha='right', y=1.0, labelpad=15)

    def write_xaxis_title(self, i_row, title):
        self.axes[i_row].set_xlabel(title, fontsize='xx-large', ha='right', x=1.0, labelpad=5)

    def write_text(self, i_row, x, y, text, ha = "left") :
        self.axes[i_row].text(x, y, text, fontsize='xx-large', transform=self.axes[i_row].transAxes, ha = ha)
        
    # https://matplotlib.org/3.5.0/gallery/statistics/errorbars_and_boxes.html
    def draw_hatch_error(self, thxxdata, i_row, edgecolor='none', hatch_style='\\\\\\', alpha=0.5):
        
        x_bin_centers = thxxdata.get_bin_centers()
        x_bin_width = thxxdata.get_bin_widths()
        bin_contents = thxxdata.get_bin_contents()
        # TODO add option to select specific systematic source
        total_error = thxxdata.get_stat_errors()
        
        xerror = np.array([x_bin_width/2., x_bin_width/2.])
        yerror = np.array([total_error, total_error])
                     
        # Loop over data points; create box from errors at each point
        errorboxes = [Rectangle((x - xe[0], y - ye[0]), xe.sum(), ye.sum(), fill=False, facecolor=None,
                        edgecolor=edgecolor, hatch=hatch_style)
                        for x, y, xe, ye in zip(x_bin_centers, bin_contents, xerror.T, yerror.T)]

        # Create patch collection with specified colour/alpha
        pc = PatchCollection(errorboxes, match_original=True, hatch=hatch_style, linewidth=0)

        # Add collection to axes
        self.axes[i_row].add_collection(pc)
        
    def draw_box_error(self, thxxdata, i_row, face_color='red', edge_color='none', alpha=0.1, error_name="stat", label=""):
        
        x_bin_centers = thxxdata.get_bin_centers()
        x_bin_width = thxxdata.get_bin_widths()
        bin_contents = thxxdata.get_bin_contents()
        if error_name=="stat" :
            total_error = thxxdata.get_stat_errors()
        else :
            total_error = thxxdata.get_total_errors()
        
        xerror = np.array([x_bin_width/2., x_bin_width/2.])
        yerror = np.array([total_error, total_error])
                     
        # Loop over data points; create box from errors at each point
        errorboxes = [Rectangle((x - xe[0], y - ye[0]), xe.sum(), ye.sum())
                        for x, y, xe, ye in zip(x_bin_centers, bin_contents, xerror.T, yerror.T)]

        # Create patch collection with specified colour/alpha
        pc = PatchCollection(errorboxes, facecolor=face_color, alpha=alpha,
                             edgecolor=edge_color, linewidth=0.05)

        # Add collection to axes
        self.axes[i_row].add_collection(pc)

        if label != "" :
            patch=mpatches.Patch(facecolor=face_color, alpha=alpha, edgecolor=edge_color, linewidth=0.05, label=label)
            self.hists_in_axes[i_row].append(patch)
            self.labels_in_axes[i_row].append(label)
    
    def draw_hist(self, thxxdata, i_row, color, label = "", normalisation = 1., set_labels=True):

        if i_row >= self.n_row:
            print("Check number of row.")
            return
        
        x_bin_centers = thxxdata.get_bin_centers()
        x_bin_edges = thxxdata.get_bin_edges()
        bin_contents = thxxdata.get_bin_contents()
        stat_unc = thxxdata.get_stat_errors()
        
        self.axes[i_row].hist(x_bin_centers, bins = x_bin_edges, weights=bin_contents, color=color, histtype = "step")
        if set_labels:
            legend_handle = mlines.Line2D([], [], color=color, label=label)
            self.hists_in_axes[i_row].append(legend_handle)
            self.labels_in_axes[i_row].append(label)

    def draw_errorbar(self, thxxdata, i_row, fmt = 'o', normalisation = 1., set_labels=True, ms = 4., **kwargs):
        
        if i_row >= self.n_row:
            print("Check number of row.")
            return
        
        x_bin_centers = thxxdata.get_bin_centers()
        x_bin_width = thxxdata.get_bin_widths()
        bin_contents = thxxdata.get_bin_contents()
        stat_unc = thxxdata.get_stat_errors()
        
        handle = self.axes[i_row].errorbar(x_bin_centers, bin_contents, xerr=x_bin_width/2., yerr=stat_unc, fmt=fmt, ms = ms, linewidth=0.5, **kwargs)
        if set_labels:
            self.hists_in_axes[i_row].append(handle)
            self.labels_in_axes[i_row].append(thxxdata.get_label_name())
            
    #
    def draw_stack(self, *thxxdatas, i_row, set_labels = True, normalisation = 1.):
    
        stacks = 0
        info_for_labels = []
        for index, thxxdata in enumerate(thxxdatas) :
            
            x_bin_centers = thxxdata.get_bin_centers()
            x_bin_width = thxxdata.get_bin_widths()
            bin_contents = thxxdata.get_bin_contents()
            
            label_name = thxxdata.get_label_name()
            color = thxxdata.get_color()
            
            handle = self.axes[i_row].bar(x_bin_centers, bin_contents, width = x_bin_width, bottom=stacks, color = color, alpha=0.7)
            stacks = stacks + bin_contents
            info_for_labels.append((handle, label_name))
        
        if set_labels:
            for handle, label in reversed(info_for_labels):
                self.hists_in_axes[i_row].append(handle)
                self.labels_in_axes[i_row].append(label)
            
    def draw_labels(self, i_row, **kwargs) :
        self.axes[i_row].legend(tuple(self.hists_in_axes[i_row]), tuple(self.labels_in_axes[i_row]), **kwargs)

    def draw_bar(self, thxxdata, i_row, normalisation = 1.):
        pass
