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

from helper import *

import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 0.5

class MatplotlibDrawer:

    def __init__(self, n_row=2, n_col=1, fig_size=(8,7), height_ratios=[1,0.3], output_name="test.pdf"):
        
        self.output_name = output_name
        self.n_row = n_row
        self.n_col = n_col
        self.fig, axes = plt.subplots(self.n_row, self.n_col, sharex=False, figsize=fig_size, gridspec_kw = {'height_ratios':height_ratios})
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
        else:
            axes.tick_params(bottom=True, top=True, left=True, right=True, which='both', direction='in')
            self.axes.append(axes)
        
    def clear_axes(self, i_row):
        self.axes[i_row].clear()
        self.labels_in_axes[i_row].clear()
        self.hists_in_axes[i_row].clear()
        
    def remove_xais_labels(self, i_row):
        self.axes[i_row].set_xticklabels([])

    def remove_first_tick_yaxis(self, i_row):
        self.axes[i_row].yaxis.set_major_locator(MaxNLocator(prune='lower'))

    def save_plot(self):
        self.fig.savefig(self.output_name, format="pdf", dpi=300)
        
    def set_y_range(self, i_row, y_min, y_max):
        self.axes[i_row].set_ylim(y_min, y_max)
        
    def set_x_range(self, i_row, x_min, x_max):
        self.axes[i_row].set_xlim(x_min, x_max)

    def write_yaxis_title(self, i_row, title):
        self.axes[i_row].set_ylabel(title, fontsize='xx-large', ha='right', y=1.0, labelpad=15)

    def write_xaxis_title(self, i_row, title):
        self.axes[i_row].set_xlabel(title, fontsize='xx-large', ha='right', x=1.0, labelpad=15)

    def write_text(self, i_row, x, y, text, ha = "left") :
        self.axes[i_row].text(x, y, text, fontsize='xx-large', transform=self.axes[i_row].transAxes, ha = ha)
        
    # https://matplotlib.org/3.5.0/gallery/statistics/errorbars_and_boxes.html
    def draw_hatch_error(self, thxxdata, i_row, show_stat = True, edgecolor='none', hatch_style='\\\\\\', alpha=0.5):
        
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
        
    def draw_box_error(self, thxxdata, i_row, show_stat = True, face_color='red', edge_color='none', alpha=0.1):
        
        x_bin_centers = thxxdata.get_bin_centers()
        x_bin_width = thxxdata.get_bin_widths()
        bin_contents = thxxdata.get_bin_contents()
        total_error = thxxdata.get_stat_errors()
        
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
    
    def draw_hist(self, thxxdata, i_row, normalisation = 1.):

        '''
        make error box
        how to extract bin contents from THxx to numpy
        '''
        pass

    def draw_errorbar(self, thxxdata, i_row, fmt = 'o', normalisation = 1., set_labels=True, ms = 4.):
        
        if i_row >= self.n_row:
            print("Check number of row.")
            return
        
        x_bin_centers = thxxdata.get_bin_centers()
        x_bin_width = thxxdata.get_bin_widths()
        bin_contents = thxxdata.get_bin_contents()
        stat_unc = thxxdata.get_stat_errors()
        
        handle = self.axes[i_row].errorbar(x_bin_centers, bin_contents, xerr=x_bin_width/2., yerr=stat_unc, fmt=fmt, ms = ms)
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
            
    def draw_labels(self, i_row) :
        self.axes[i_row].legend(tuple(self.hists_in_axes[i_row]), tuple(self.labels_in_axes[i_row]))

    def draw_bar(self, thxxdata, i_row, normalisation = 1.):
        pass
