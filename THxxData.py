import ROOT as rt
import numpy as np
import math
import THxxData
import copy

from helper import *

class THxxData: # class RootHistData

    '''
    TUnfoldxxData
    input: histogram using TUnfoldBinning 
    
    '''
    def __init__(self, input_root_files, hist_name, hist_label_name, color, set_mean_value = False):
        
        self.hist_name=hist_name # histogram name to read 
        self.hist_label_name=hist_label_name # histogram label to write in output plot
        
        self.sample_names=[]
        
        self.input_thists=[]
        self.color = color

        self.stat_unc_hists=[]
        
        # open root file
        first_file=True
        for sample_name, root_file in input_root_files: 
            temp_file=rt.TFile.Open(root_file, "READ")
            self.sample_names.append(sample_name)
            
            # read central histogram 
            temp_thist=temp_file.Get(self.hist_name)
            if type(temp_thist) == rt.TH1D : # check if histogram exist
                temp_thist.Sumw2()
                temp_thist.SetDirectory(0)
                if first_file:
                    self.central_thist=temp_thist 
                else:
                    self.central_thist.Add(temp_thist,1)
                    
                temp_thist_raw=temp_thist.Clone(sample_name)
                temp_thist_raw.SetDirectory(0)
                self.input_thists.append(temp_thist_raw)
            
            first_file=False
            temp_file.Close()

        self.set_stat_unc_hists()

    def get_mean(self, x_start=0, x_end=0, reset_stat=False) :
        if reset_stat :
            temp_hist = self.central_thist.Clone("cloned_hist")
            temp_hist.ResetStats()
            if x_start == x_end :
                return temp_hist.GetMean(), temp_hist.GetMeanError()
        else :
            if x_start == x_end :
                return self.central_thist.GetMean(), self.central_thist.GetMeanError()

    def divide_bin_width(self) :
    
        self.central_thist.Scale(1., "width");
        self.set_stat_unc_hists()

    def normalize(self) :
        
        self.central_thist.Scale(1./self.central_thist.Integral())
        self.set_stat_unc_hists()

    def get_color(self) :
        return self.color
        
    def set_label_name(self, name):
        self.hist_label_name = name

    def get_label_name(self):
        return self.hist_label_name
            
    def print_input_sample_names(self):
        for sample_name in self.sample_names:
            print(sample_name)

    def get_bin_edges(self):

        bin_edges = []
        nbinsx=self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            bin_edges.append(self.central_thist.GetXaxis().GetBinLowEdge(ibin+1))

        # last bin upper edge
        bin_edges.append(bin_edges[-1] + self.central_thist.GetBinWidth(nbinsx))

        return np.array(bin_edges)

    def get_bin_centers(self):

        bin_centers = []
        nbinsx=self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            bin_centers.append(self.central_thist.GetXaxis().GetBinCenter(ibin+1))

        return np.array(bin_centers)

    def get_bin_contents(self):
   
        bin_contents = []
        nbinsx=self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            bin_contents.append(self.central_thist.GetBinContent(ibin+1))
    
        return np.array(bin_contents)
    
    def get_bin_widths(self):
   
        bin_widths = []
        nbinsx=self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            bin_widths.append(self.central_thist.GetXaxis().GetBinWidth(ibin+1))

        return np.array(bin_widths)

    def set_stat_unc_hists(self):

        if len(self.stat_unc_hists)!=0:
            self.stat_unc_hists.clear()

        self.stat_unc_hists.append(make_clean_hist(self.central_thist, "total_unc_up"))
        self.stat_unc_hists.append(make_clean_hist(self.central_thist, "total_unc_down"))

        nbinsx=self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):

            stat_up=self.central_thist.GetBinError(ibin+1)

            self.stat_unc_hists[up_down.up].SetBinContent(ibin+1, stat_up)
            self.stat_unc_hists[up_down.down].SetBinContent(ibin+1, stat_up)

    def get_stat_errors(self, variation_direction=up_down.up):

        bin_errors = []
        nbinsx = self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            bin_errors.append(self.stat_unc_hists[variation_direction].GetBinContent(ibin+1))

        return np.array(bin_errors)

    def __truediv__(self, other):
        # operator overloading for ratio histogram with systematic info
        # return new THxxDataWithSyst object
        ratio_=copy.deepcopy(self)
        ratio_.central_thist.Divide(other.central_thist)

        ratio_.set_stat_unc_hists()

        return ratio_

    def __add__(self, other):

        sum_=copy.deepcopy(self)
        sum_.central_thist.Add(other.central_thist,1.)

        sum_.set_stat_unc_hists()

        return sum_
            
    def make_plot(self, show_syst=False, output_name="test.pdf"):
        c1 = rt.TCanvas()
        
        self.central_thist.Draw()
        
        color=1
        for thist in self.input_thists:
            thist.Draw("HIST SAMEE")
            thist.SetLineColor(color)
            color+=1
        
        c1.Draw()
        c1.SaveAs(output_name)
        
    def get_central_data(self):
        pass 
    
if __name__=='__main__':
    
    dy_hist=THxxData([("DY50plus","/Users/jhkim/cms_snu/ISRAnalyzer_DYJets.root"),
                      ("DY10to50","/Users/jhkim/cms_snu/ISRAnalyzer_DYJets10to50_MG.root")],
                     "mm2016/dilep_pt_mm40to64","Drell-Yan")
    
    dy_hist.print_input_sample_names()
    dy_hist.make_plot()
