import ROOT as rt
import numpy as np
import math
import THxxData
import copy

from collections import defaultdict


def make_clean_hist(original_hist, name):

    new_hist = original_hist.Clone(name)
    new_hist.Reset()
    return new_hist

class up_down:
    up=0
    down=1
    
class THxxDataWithSyst(THxxData.THxxData):
    #def __init__(self, *args, **kwargs):
    
    def __init__(self, input_root_files, hist_name, hist_label_name, syst_input_root_files, syst_names):
    
        super().__init__(input_root_files, hist_name, hist_label_name) # set central histogram
        
        self.syst_names = syst_names
        self.syst_raw_hists_map=defaultdict(list)
        
        self.syst_hists_map=defaultdict(list) # delta
        self.total_syst_hists=[] # total systematic uncertainty histograms
        self.total_error_hists=[] # stat+syst histograms
        
        # open root file
        first_file=True
        for root_file in syst_input_root_files:
            #print(root_file)
            temp_file=rt.TFile.Open(root_file, "READ")
            
            # read systematic histograms
            for syst_name in self.syst_names :
                for index, syst_postfix in enumerate(self.syst_names[syst_name]):
                    temp_thist=temp_file.Get(hist_name+syst_name+syst_postfix)
                    temp_thist.SetDirectory(0)
                    if first_file:
                        self.syst_raw_hists_map[syst_name].append(temp_thist)
                    else:
                        self.syst_raw_hists_map[syst_name][index].Add(temp_thist,1)
            
            first_file=False
            temp_file.Close()
        
        # set total systematic histograms
        self.set_total_syst_hists()
        # set total uncertatiny histograms
        self.set_total_error_hists()
        
    def get_total_errors(self, variation_direction=up_down.up):
        
        bin_errors = []
        nbinsx = self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            bin_errors.append(self.total_error_hists[variation_direction].GetBinContent(ibin+1))
        
        return np.array(bin_errors)
        
    def get_bin_contents(self):
    
        bin_contents = []
        nbinsx=self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            bin_contents.append(self.central_thist.GetBinContent(ibin+1))
        
        return np.array(bin_contents)
        
    def get_bin_centers(self):
        
        bin_centers = []
        nbinsx=self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            bin_centers.append(self.central_thist.GetXaxis().GetBinCenter(ibin+1))
        
        return np.array(bin_centers)
        
    def get_bin_widths(self):
    
        bin_widths = []
        nbinsx=self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            bin_widths.append(self.central_thist.GetXaxis().GetBinWidth(ibin+1))
        
        return np.array(bin_widths)

    def set_total_syst_hists(self):
        
        if len(self.total_syst_hists)!=0:
            self.total_syst_hists.clear()
    
        # set squared delta sum up/down histograms
        self.total_syst_hists.append(make_clean_hist(self.central_thist, "total_syst_up"))
        self.total_syst_hists.append(make_clean_hist(self.central_thist, "total_syst_down"))
        nbinsx=self.central_thist.GetNbinsX()
        
        # loop over systematic source
        for syst_name in self.syst_names:
            
            syst_array=np.zeros((nbinsx, len(self.syst_names[syst_name])))
            
            # loop over variations
            for index, syst_postfix in enumerate(self.syst_names[syst_name]):
                temp_delta=self.syst_raw_hists_map[syst_name][index].Clone(syst_name+syst_postfix)
                temp_delta.Add(self.central_thist,-1)
                
                self.syst_hists_map[syst_name].append(temp_delta)
                
                # set syst_array
                for ibin in range(nbinsx):
                    syst_array[ibin][index]=abs(temp_delta.GetBinContent(ibin+1))
                
            # set maximum variation for each bin
            for ibin in range(nbinsx):
                max_variation_ibin=np.amax(syst_array[ibin])
                previous_tot_syst_up=self.total_syst_hists[up_down.up].GetBinContent(ibin+1)
                previous_tot_syst_down=self.total_syst_hists[up_down.down].GetBinContent(ibin+1)
                
                update_tot_syst_up=previous_tot_syst_up*previous_tot_syst_up+max_variation_ibin*max_variation_ibin
                update_tot_syst_down=previous_tot_syst_up*previous_tot_syst_down+max_variation_ibin*max_variation_ibin
                
                self.total_syst_hists[up_down.up].SetBinContent(ibin+1,math.sqrt(update_tot_syst_up))
                self.total_syst_hists[up_down.down].SetBinContent(ibin+1,math.sqrt(update_tot_syst_down))
                
    def set_total_error_hists(self):
        # syst+stat
        
        if len(self.total_error_hists)!=0:
            self.total_error_hists.clear()
        
        self.total_error_hists.append(make_clean_hist(self.central_thist, "total_unc_up"))
        self.total_error_hists.append(make_clean_hist(self.central_thist, "total_unc_down"))
        
        nbinsx=self.central_thist.GetNbinsX()
        for ibin in range(nbinsx):
            
            tot_syst_up=self.total_syst_hists[up_down.up].GetBinContent(ibin+1)
            stat_up=self.central_thist.GetBinError(ibin+1)
           
            tot_unc=tot_syst_up*tot_syst_up+stat_up*stat_up
            #tot_unc=tot_syst_up*tot_syst_up
            self.total_error_hists[up_down.up].SetBinContent(ibin+1,math.sqrt(tot_unc))
            self.total_error_hists[up_down.down].SetBinContent(ibin+1,math.sqrt(tot_unc))
            
    def __add__(self, other):

        sum_=copy.deepcopy(self)        
        sum_.central_thist.Add(other.central_thist,1.)

        for syst_name in self.syst_names :
            for index, syst_postfix in enumerate(self.syst_names[syst_name]):
                sum_.syst_raw_hists_map[syst_name][index].Add(other.syst_raw_hists_map[syst_name][index],1.) # TODO check how to handle if different systematics considered 

        sum_.set_total_syst_hists()
        sum_.set_total_error_hists()

        return sum_
            
    def __truediv__(self, other):
        # operator overloading for ratio histogram with systematic info
        # return new THxxDataWithSyst object
        ratio_=copy.deepcopy(self)
        ratio_.central_thist.Divide(other.central_thist)
        
        for syst_name in self.syst_names :
            for index, syst_postfix in enumerate(self.syst_names[syst_name]):
                ratio_.syst_raw_hists_map[syst_name][index].Divide(other.central_thist)
                
        ratio_.set_total_syst_hists()
        ratio_.set_total_error_hists()
        
        return ratio_
        
    # test plot
    def make_plot(self,output_name="test_syst.pdf"):
        c1 = rt.TCanvas()
        c1.SetLogx()
        print("make_plot in THxxDataWithSyst")
        
        #self.central_thist.GetXaxis().SetRangeUser(0.1,100)
        self.central_thist.Draw("HIST P9e")
        self.central_thist.SetMarkerStyle(24)
        self.central_thist.SetMarkerSize(0);
        self.central_thist.SetLineColor(rt.kBlack)
        
        self.central_thist.SetMinimum(0.5)
        self.central_thist.SetMaximum(1.5)
        
        total_syst_hist=self.central_thist.Clone("total_syst_hist")
        for ibin in range(total_syst_hist.GetNbinsX()):
            total_syst_hist.SetBinError(ibin+1, self.total_syst_hists[up_down.up].GetBinContent(ibin+1))
        
        #total_syst_hist.Draw("p9E2 SAME")
        #total_syst_hist.SetMarkerStyle(20)
        #total_syst_hist.SetMarkerSize(0.5);
        #total_syst_hist.SetFillStyle(1001)
        #total_syst_hist.SetFillColorAlpha(rt.kBlack,0.5);
        
        self.central_thist.Draw("p9E2 SAME")
        self.central_thist.SetMarkerStyle(20)
        self.central_thist.SetMarkerSize(0.5);
        self.central_thist.SetFillStyle(1001)
        self.central_thist.SetFillColorAlpha(rt.kBlack,0.5);
        
        total_error_hist=self.central_thist.Clone("total_error_hist")
        for ibin in range(total_error_hist.GetNbinsX()):
            total_error_hist.SetBinError(ibin+1, self.total_error_hists[up_down.up].GetBinContent(ibin+1))
            
        total_error_hist.Draw("p9E2 SAME")
        total_error_hist.SetMarkerStyle(24)
        total_error_hist.SetMarkerSize(0.5);
        total_error_hist.SetFillStyle(3004)
        total_error_hist.SetFillColor(rt.kBlack);
        
        #color=1
        #for syst_name in self.syst_raw_hists_map:
        #    for syst_thist in self.syst_raw_hists_map[syst_name]:
        #        syst_thist.Draw("HIST SAME")
        #        syst_thist.SetLineColor(color)
        #    color+=1
        
        c1.Draw()
        c1.SaveAs(output_name)

if __name__=='__main__':

    dy_hist=THxxDataWithSyst([("DY50plus","./hists.root")],"mm2016/2D_dipt_dimass_smeared","Drell-Yan",
    ["./hists_syst.root"], {"_scale":["_up","_down"], "_IDSF":["_up","_down"]})
    
    dy_hist.print_input_sample_names()
    dy_hist.make_plot()
    
    dy_hist_copy=copy.deepcopy(dy_hist)
    ratio=dy_hist_copy/dy_hist
    ratio.make_plot(output_name="ratio.pdf")
    
