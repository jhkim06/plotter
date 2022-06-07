import ROOT as rt
import numpy as np
import math
import THxxData
import THxxDataWithSyst
import copy
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

class MatplotlibDrawer:

    def __init__(self, n_row=2, n_col=1, fig_size=(8,7), height_ratios=[1,0.3], output_name="test.pdf"):
        
        self.output_name = output_name
        self.n_row = n_row
        self.n_col = n_col
        self.fig, axes = plt.subplots(self.n_row, self.n_col, sharex=False, figsize=fig_size, gridspec_kw = {'height_ratios':height_ratios})
        plt.tight_layout()
        plt.subplots_adjust(left=0.15, right=0.97, bottom=0.05, top=0.95, hspace=0.0)
        
        self.axes = []
        if n_row > 1:
            for axe in axes:
                self.axes.append(axe)
        else:
            self.axes.append(axes)
        
        '''
        note, axes can be matrix
        list of (histogram handle, label)  per axes
        
        '''
        
    def clear_axes(self, i_row):
        self.axes[i_row].clear()
        
    def remove_xais_labels(self, i_row):
        self.axes[i_row].set_xticklabels([])

    def save_plot(self):
        self.fig.savefig(self.output_name, format="pdf", dpi=300)
        
    # https://matplotlib.org/3.5.0/gallery/statistics/errorbars_and_boxes.html
    def draw_hatch_error(self, thxxdata, i_row, edgecolor='none', hatch_style='\\\\\\', alpha=0.5):
        
        x_bin_centers = thxxdata.get_bin_centers()
        x_bin_width = thxxdata.get_bin_widths()
        bin_contents = thxxdata.get_bin_contents()
        # TODO add option to select specific systematic source
        total_error = thxxdata.get_total_errors()
        
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
        
    def draw_box_error(self, thxxdata, i_row, face_color='red', edge_color='none', alpha=0.1):
        
        x_bin_centers = thxxdata.get_bin_centers()
        x_bin_width = thxxdata.get_bin_widths()
        bin_contents = thxxdata.get_bin_contents()
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
    
    def draw_hist(self, thxxdata, i_row, normalisation = 1.):

        '''
        make error box
        how to extract bin contents from THxx to numpy
        '''
        pass

    def draw_errorbar(self, thxxdata, i_row, fmt = 'o', normalisation = 1., show_label=True,
                     y_range = None):
        
        if y_range is not None:
            self.axes[i_row].set_ylim(y_range[0], y_range[1])
        
        if i_row >= self.n_row:
            print("Check number of row.")
            return
        
        x_bin_centers = thxxdata.get_bin_centers()
        x_bin_width = thxxdata.get_bin_widths()
        bin_contents = thxxdata.get_bin_contents()
        
        artists = self.axes[i_row].errorbar(x_bin_centers, bin_contents, xerr=x_bin_width/2., fmt=fmt)
            
    #
    def draw_stack(self, *thxxdatas, i_row, normalisation = 1.):
    
        stacks = 0
        for index, thxxdata in enumerate(thxxdatas) :
            
            x_bin_centers = thxxdata.get_bin_centers()
            x_bin_width = thxxdata.get_bin_widths()
            bin_contents = thxxdata.get_bin_contents()
            
            handle = self.axes[i_row].bar(x_bin_centers, bin_contents, width = x_bin_width, bottom=stacks, alpha=0.7)
            stacks = stacks + bin_contents

    def draw_bar(self, thxxdata, i_row, normalisation = 1.):
        pass
