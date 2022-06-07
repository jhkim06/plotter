import ROOT as rt

class THxxData: # class RootHistData
    def __init__(self, input_root_files, hist_name, hist_label_name):
        
        self.hist_name=hist_name # histogram name to read 
        self.hist_label_name=hist_label_name # histogram label to write in output plot
        
        self.sample_names=[]
        
        self.input_thists=[]
        
        # open root file
        first_file=True
        for sample_name, root_file in input_root_files: 
            temp_file=rt.TFile.Open(root_file, "READ")
            self.sample_names.append(sample_name)
            
            # read central histogram 
            temp_thist=temp_file.Get(self.hist_name)
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

    def set_label_name(self, name):
        self.hist_label_name = name

    def get_label_name(self):
        return self.hist_label_name
            
    def print_input_sample_names(self):
        for sample_name in self.sample_names:
            print(sample_name)
            
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
