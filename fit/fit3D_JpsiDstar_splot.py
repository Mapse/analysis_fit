import ROOT
#import bot_config as bot
import argparse

from uncertainties import ufloat
from uncertainties.umath import *

import config_fit_3d_splot as config

# Enable multicore
ROOT.EnableImplicitMT()

## Argparse section
parser = argparse.ArgumentParser(description='JpsiDstar 3D fit')
parser.add_argument("-f", "--fit", help="Fit the data", action="store_true")
parser.add_argument("-s", "--splot", help="Splot and weights", action="store_true")
parser.add_argument("-c", "--coffea", help="Create coffea hists", action="store_true")
parser.add_argument("-y", "--yields", help="Calculate the yields", action="store_true")


args = parser.parse_args()

def fit3DJpsiDstar(opt):
    
    file = ROOT.TFile.Open(opt[1]['files'][8])
    #file = ROOT.TFile.Open("Charmonium_2017_RunF_HLT_Dimuon25_dl_fit.root")

    # Jpsi mass parameter
    jpsi_mass = ROOT.RooRealVar("jpsi_mass", "", 2.95, 3.25)

    # Decay lenght 
    jpsi_dl = ROOT.RooRealVar("jpsi_dl", "", -0.5, 1.4)

    jpsi_dlErr = ROOT.RooRealVar("jpsi_dlErr", "", *opt[0]['fit_parameters']['jpsi_dlErr'])
    jpsi_dlErr.setConstant(False)

    # Dstar mass parameter
    dstar_mass = ROOT.RooRealVar("dstar_mass", " ", 0.13957, 0.16)

    root_data = file.asso

    # Data
    data = ROOT.RooDataSet("data", "", ROOT.RooArgSet(jpsi_mass, jpsi_dl, dstar_mass),
                                    ROOT.RooFit.Import(root_data))
   
    ########## Jpsi Mass Signal: Crystal Ball and Gaussian with same mean

    # Mean
    mean_jpsi = ROOT.RooRealVar("mean_jpsi", "", *opt[0]['fit_parameters']['mean_jpsi'])
    
    # Sigmas
    sigma_gauss = ROOT.RooRealVar("sigma_gauss", "", *opt[0]['fit_parameters']['sigma_gauss'])
    sigma_cb = ROOT.RooRealVar("sigma_cb", "", *opt[0]['fit_parameters']['sigma_cb'])
    
    # PDFs fractions
    frac_gauss_jpsi = ROOT.RooRealVar("frac_gauss_jpsi","", *opt[0]['fit_parameters']['frac_gauss_jpsi'])
    frac_cb = ROOT.RooRealVar("frac_cb","", *opt[0]['fit_parameters']['frac_cb'])

    # Alpha and n for Crystal Ball
    alpha = ROOT.RooRealVar("alpha", "", opt[0]['fit_parameters']['alpha'])
    n = ROOT.RooRealVar("n", "", opt[0]['fit_parameters']['n'])

    # Mass Signal definition
    gauss = ROOT.RooGaussian("gauss", "", jpsi_mass, mean_jpsi, sigma_gauss)
    crystal_ball = ROOT.RooCBShape("crystal_ball", "", jpsi_mass, mean_jpsi, sigma_cb, alpha, n)

    if config.jpsi_mass_pdf['signal'] == 'CBG':
        jpsi_mass_signal = ROOT.RooAddPdf("jpsi_mass_signal", "", ROOT.RooArgList(gauss, crystal_ball), 
                                                                    ROOT.RooArgList(frac_gauss_jpsi, frac_cb),)
    elif config.jpsi_mass_pdf['signal'] == 'CB':
        jpsi_mass_signal = ROOT.RooCBShape("jpsi_mass_signal", "", jpsi_mass, mean_jpsi, sigma_cb, alpha, n)

    # jpsi mass frac
    #frac_gauss_jpsi = ROOT.RooRealVar("frac_jpsi_mass","", 3.13573e-01, 0.0001, 1.0)

    ## Jpsi Mass Background: Exponential

    # Exponential coefficient
    exp_coef = ROOT.RooRealVar("exp_coef", "", *opt[0]['fit_parameters']['exp_coef'])

    # Background fraction
    frac_exp_mass = ROOT.RooRealVar("frac_exp_mass", "", *opt[0]['fit_parameters']['frac_exp_mass'])

    # Background definition
    if config.jpsi_mass_pdf['background'] == 'exp':    	
        jpsi_mass_background = ROOT.RooExponential("back_exp", "", jpsi_mass, exp_coef)
    if config.jpsi_mass_pdf['background'] == 'linear':  
        p0 = ROOT.RooRealVar("p0","", *opt[0]['fit_parameters']['linear_coef0'])
        p1 = ROOT.RooRealVar('p1',"", *opt[0]['fit_parameters']['linear_coef1'])
        jpsi_mass_background = ROOT.RooPolynomial("back_linear", "", jpsi_mass, ROOT.RooArgList(p0,p1))
    ################## PDFs for prompt signal: Resolution function + Gaussian

    # Prompt Resolution 
    mean_prompt = ROOT.RooRealVar("mean_prompt", "", *opt[0]['fit_parameters']['mean_prompt'])
    sigma_prompt = ROOT.RooRealVar("sigma_prompt", "", *opt[0]['fit_parameters']['sigma_prompt'])
    frac_prompt = ROOT.RooRealVar("frac_prompt", "", *opt[0]['fit_parameters']['frac_prompt'])
    resolution_prompt = ROOT.RooGaussModel("resolution_prompt", "", jpsi_dl, mean_prompt, sigma_prompt, jpsi_dlErr)

    # Gaussian 
    mean_pv = ROOT.RooRealVar("mean_pv", "", *opt[0]['fit_parameters']['mean_pv'])
    sigma_pv = ROOT.RooRealVar("sigma_pv", "", *opt[0]['fit_parameters']['sigma_pv'])
    frac_pv = ROOT.RooRealVar("frac_np1", "", *opt[0]['fit_parameters']['frac_np1'])
    gauss_pv = ROOT.RooGaussian("gauss_pv", "", jpsi_dl, mean_pv, sigma_pv)
    exp_coef_pv = ROOT.RooRealVar("exp_coef_pv", "", *opt[0]['fit_parameters']['exp_coef_pv'])
    prompt_exp = ROOT.RooExponential("prompt_exp", "", jpsi_dl, exp_coef_pv)

    # Jpsi prompt model definition 
    if config.jpsi_pdf['prompt'] == 'resolG':    	
        jpsi_prompt = ROOT.RooAddPdf("jpsi_prompt", "", ROOT.RooArgList(resolution_prompt, gauss_pv),
                                                        ROOT.RooArgList(frac_prompt, frac_pv),)
    
    elif config.jpsi_pdf['prompt'] == 'GA':  
        mean_ge = ROOT.RooRealVar("mean_ge", "", *opt[0]['fit_parameters']['mean_ge']) #ge: Gauss extra
        sigma_ge = ROOT.RooRealVar("sigma_ge", "", *opt[0]['fit_parameters']['sigma_ge'])
        gauss_ge = ROOT.RooGaussian("gauss_ge", "", jpsi_dl, mean_ge, sigma_ge)
        jpsi_prompt = ROOT.RooAddPdf("jpsi_prompt", "", ROOT.RooArgList(gauss_ge, gauss_pv),
                                                        ROOT.RooArgList(frac_pv), ROOT.kTRUE)
        	
    ## Non-prompt: Exponential function convoluted with the another resolution function 

    # Non Prompt Resolution 
    mean_non_prompt = ROOT.RooRealVar("mean_non_prompt", "", *opt[0]['fit_parameters']['mean_non_prompt'])
    sigma_non_prompt = ROOT.RooRealVar("sigma_non_prompt", "", *opt[0]['fit_parameters']['sigma_non_prompt'])
    frac_non_prompt = ROOT.RooRealVar("frac_non_prompt", "", 0.5, 0, 1.0)
    frac_gauss_dl = ROOT.RooRealVar("frac_gauss_dl", "", *opt[0]['fit_parameters']['frac_gauss_dl'])
    resolution_non_prompt = ROOT.RooGaussModel("resolution_non_prompt", "", jpsi_dl, mean_non_prompt, sigma_non_prompt, jpsi_dlErr)

    # Exponential decay
    tau = ROOT.RooRealVar("tau", "", *opt[0]['fit_parameters']['tau'])
    
    # PDF for nompromt signal
    frac_exp_dl = ROOT.RooRealVar("frac_exp_dl", "", *opt[0]['fit_parameters']['frac_exp_dl'])
    #jpsi_non_prompt = ROOT.RooDecay("exp_decay", "", jpsi_dl, tau, resolution_non_prompt, ROOT.RooDecay.SingleSided)
    if config.jpsi_pdf['non_prompt'] == 'resol':    	    
        jpsi_non_prompt = ROOT.RooDecay("exp_decay", "", jpsi_dl, tau, resolution_non_prompt, ROOT.RooDecay.SingleSided)
    elif config.jpsi_pdf['non_prompt'] == 'GA':    
        
        gauss_gnp = ROOT.RooGaussian("gauss_gnp", "", jpsi_dl, mean_non_prompt, sigma_non_prompt)
        exp_coef_pv = ROOT.RooRealVar("exp_coef_pv", "", *opt[0]['fit_parameters']['exp_coef_pv'])
        prompt_exp = ROOT.RooExponential("prompt_exp", "", jpsi_dl, exp_coef_pv)
        jpsi_non_prompt = ROOT.RooFFTConvPdf("lxg","exp (X) gauss",jpsi_dl, prompt_exp, gauss_gnp) 	    
        #jpsi_non_prompt = ROOT.RooDecay("exp_decay", "", jpsi_dl, tau, gauss_gnp, ROOT.RooDecay.SingleSided)
        
    ## Dstar Signal: Jhonson's PDF

    # Dstar mean deltamr
    dstar_mean = ROOT.RooRealVar("dstar_mean", "Dstar mean", *opt[0]['fit_parameters']['dstar_mean'])    
    # Signal fraction
    dstar_frac = ROOT.RooRealVar("dstar_frac", "Dstar Johnson's frac", *opt[0]['fit_parameters']['dstar_frac'])

    # Jhonson PDF definition
    if config.dstar_pdf['signal'] == 'johnson':
        # Jhonson's lambda
        dstar_lambda = ROOT.RooRealVar("dstar_lambda", "Dstar Johnson's lambda", *opt[0]['fit_parameters']['dstar_lambda'])
        # Jhonson's gamma
        dstar_gamma = ROOT.RooRealVar("dstar_gamma", "Dstar Johnson's gamma", *opt[0]['fit_parameters']['dstar_gamma'])
        # Jhonson's delta
        dstar_delta = ROOT.RooRealVar("dstar_delta", "Dstar Johnson's delta", *opt[0]['fit_parameters']['dstar_delta'])
        dstar_signal = ROOT.RooJohnson("dstar_signal", "Dstar Jhonson", dstar_mass, dstar_mean, dstar_lambda, dstar_gamma, dstar_delta)
    if config.dstar_pdf['signal'] == 'doubleG':
        
        # Gaussians sigma
        dstar_sigma_g1 = ROOT.RooRealVar("dstar_sigma_g1", "Gauss sigma 1", *opt[0]['fit_parameters']['dstar_sigma_g1'])
        dstar_sigma_g2 = ROOT.RooRealVar("dstar_sigma_g2", "Gauss sigma 2", *opt[0]['fit_parameters']['dstar_sigma_g2'])
        # Gaussians definition
        gauss1_dstar = ROOT.RooGaussian("gauss1_dstar", "", dstar_mass, dstar_mean, dstar_sigma_g1)
        gauss2_dstar = ROOT.RooGaussian("gauss2_dstar", "", dstar_mass, dstar_mean, dstar_sigma_g2)
        dstar_signal = ROOT.RooAddPdf("dstar_signal", "", ROOT.RooArgList(gauss1_dstar, gauss2_dstar),
        	                                              ROOT.RooArgList(dstar_frac), ROOT.kTRUE)


    #  Phenomenological Threshold Function 
    if config.dstar_pdf['background'] == 'ptf':
        # Coefficients
        p0 = ROOT.RooRealVar("p0","", *opt[0]['fit_parameters']['p0'])
        p1 = ROOT.RooRealVar('p1',"", *opt[0]['fit_parameters']['p1'])
        p2 = ROOT.RooRealVar('p2',"", *opt[0]['fit_parameters']['p2'])
        # Background definition
        dstar_bkg = ROOT.RooGenericPdf("dstar_bkg","Dstar Background PDF","(1 - exp(-(@0 -0.13957)/@1)) * (@0/0.13957)**@2 + @3 * (@0/0.13957 - 1)",
                            ROOT.RooArgList(dstar_mass, p0, p1, p2))

    elif config.dstar_pdf['background'] == 'ntf':
        A = ROOT.RooRealVar("A","", *opt[0]['fit_parameters']['A'])
        B = ROOT.RooRealVar("B","", *opt[0]['fit_parameters']['B'])
        C = ROOT.RooRealVar("C","", *opt[0]['fit_parameters']['C'])
        # Background definition
        dstar_bkg = ROOT.RooGenericPdf("dstar_bkg","Dstar Background PDF"," @1 * (@0 - 0.13957)**@2 * exp(@3*(@0-0.13957))",
                            ROOT.RooArgList(dstar_mass, A, B, C))

    # Pdfs from fit
    signal = ROOT.RooProdPdf("signal", "Signal of 3D model", ROOT.RooArgList(jpsi_mass_signal, jpsi_prompt, dstar_signal))
    bkg1 = ROOT.RooProdPdf("bkg1", "Bkg1 of 3D model", ROOT.RooArgList(jpsi_mass_signal, jpsi_prompt, dstar_bkg))
    bkg2 = ROOT.RooProdPdf("bkg2", "Bkg2 of 3D model", ROOT.RooArgList(jpsi_mass_signal, jpsi_non_prompt, dstar_signal))
    bkg3 = ROOT.RooProdPdf("bkg3", "Bkg3 of 3D model", ROOT.RooArgList(jpsi_mass_signal, jpsi_non_prompt, dstar_bkg))
    bkg4 = ROOT.RooProdPdf("bkg4", "Bkg4 of 3D model", ROOT.RooArgList(jpsi_mass_background, jpsi_prompt, dstar_signal))
    bkg5 = ROOT.RooProdPdf("bkg5", "Bkg5 of 3D model", ROOT.RooArgList(jpsi_mass_background, jpsi_prompt, dstar_bkg))
    bkg6 = ROOT.RooProdPdf("bkg6", "Bkg6 of 3D model", ROOT.RooArgList(jpsi_mass_background, jpsi_non_prompt, dstar_signal))
    bkg7 = ROOT.RooProdPdf("bkg7", "Bkg7 of 3D model", ROOT.RooArgList(jpsi_mass_background, jpsi_non_prompt, dstar_bkg))

    signal_frac = ROOT.RooRealVar("signal_frac", "signal fraction", *opt[0]['fit_parameters']['signal_frac'])
    
    bkg1_frac = ROOT.RooRealVar("bkg1_frac", "bkg1 fraction", *opt[0]['fit_parameters']['bkg1_frac']) # Signal, prompt, Background (reduce)    
    bkg2_frac = ROOT.RooRealVar("bkg2_frac", "bkg2 fraction", *opt[0]['fit_parameters']['bkg2_frac']) # Signal, non prompt, signal
    bkg3_frac = ROOT.RooRealVar("bkg3_frac", "bkg3 fraction", *opt[0]['fit_parameters']['bkg3_frac'])
    bkg4_frac = ROOT.RooRealVar("bkg4_frac", "bkg4 fraction", *opt[0]['fit_parameters']['bkg4_frac']) # Background, prompt, signaL
    bkg5_frac = ROOT.RooRealVar("bkg5_frac", "bkg5 fraction", *opt[0]['fit_parameters']['bkg5_frac'])
    bkg6_frac = ROOT.RooRealVar("bkg6_frac", "bkg6 fraction", *opt[0]['fit_parameters']['bkg6_frac'])
    bkg7_frac = ROOT.RooRealVar("bkg7_frac", "bkg7 fraction", *opt[0]['fit_parameters']['bkg7_frac'])

    e_signal = ROOT.RooExtendPdf("e_signal", "Extended PDF - Signal of 3D model", signal, signal_frac)
    e_bkg1 = ROOT.RooExtendPdf("e_bkg1", "Extended PDF - bkg1 of 3D model", bkg1, bkg1_frac)
    e_bkg2 = ROOT.RooExtendPdf("e_bkg2", "Extended PDF - bkg2 of 3D model", bkg2, bkg2_frac)
    e_bkg3 = ROOT.RooExtendPdf("e_bkg3", "Extended PDF - bkg3 of 3D model", bkg3, bkg3_frac)
    e_bkg4 = ROOT.RooExtendPdf("e_bkg4", "Extended PDF - bkg4 of 3D model", bkg4, bkg4_frac)
    e_bkg5 = ROOT.RooExtendPdf("e_bkg5", "Extended PDF - bkg5 of 3D model", bkg5, bkg5_frac)
    e_bkg6 = ROOT.RooExtendPdf("e_bkg6", "Extended PDF - bkg6 of 3D model", bkg6, bkg6_frac)
    e_bkg7 = ROOT.RooExtendPdf("e_bkg7", "Extended PDF - bkg7 of 3D model", bkg7, bkg7_frac)

    model3D = ROOT.RooAddPdf("model3D",
                            "3D Model Jpsi mass + Jpsi cecay length", 
                            ROOT.RooArgList(e_signal, e_bkg1, e_bkg2, e_bkg3, e_bkg4, e_bkg5, e_bkg6, e_bkg7),
                            )

    result = model3D.fitTo(data, ROOT.RooFit.Save())
    # Print the results on screen
    result.floatParsFinal().Print("S")

    ####### Plotting

    # Remove all histograms titles.
    ROOT.gStyle.SetOptTitle(0)

    ### Jpsi mass

    #colors = [TColor.GetColor(color) for color in colors_hex]
    colors = [2, 3, 4, 5, 6, 7, 8, 9, 21]
    styles = [1, 1, 2, 2, 2, 2, 2, 2, 2]

    # Canvas for Jpsi mass
    cjm = ROOT.TCanvas("canvas_jpsi_mass", '', 1400, 900)
    
    # Frame for Jpsi mass
    frame_jpsi_mass = jpsi_mass.frame(ROOT.RooFit.Title("Dimuon Invariant mass"))
    frame_jpsi_mass.GetXaxis().SetTitle("#M_{\mu^+\mu^-} \ [GeV/c^2]")
    
    # Plot the Jpsi data
    data.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))

    # Plot the Model components
    model3D.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Signal"), ROOT.RooFit.Components("signal"),
                ROOT.RooFit.LineStyle(styles[1]), ROOT.RooFit.LineColor(colors[1]))
    model3D.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Background 1"), ROOT.RooFit.Components("bkg1"),
                ROOT.RooFit.LineStyle(styles[2]), ROOT.RooFit.LineColor(colors[2]))
    model3D.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Background 2"), ROOT.RooFit.Components("bkg2"),
                ROOT.RooFit.LineStyle(styles[3]), ROOT.RooFit.LineColor(colors[3]))
    model3D.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Background 3"), ROOT.RooFit.Components("bkg3"),
                ROOT.RooFit.LineStyle(styles[4]), ROOT.RooFit.LineColor(colors[4]))
    model3D.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Background 4"), ROOT.RooFit.Components("bkg4"),
                ROOT.RooFit.LineStyle(styles[5]), ROOT.RooFit.LineColor(colors[5]))
    model3D.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Background 5"), ROOT.RooFit.Components("bkg5"),
                ROOT.RooFit.LineStyle(styles[6]), ROOT.RooFit.LineColor(colors[6]))
    model3D.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Background 6"), ROOT.RooFit.Components("bkg6"),
                ROOT.RooFit.LineStyle(styles[7]), ROOT.RooFit.LineColor(colors[7]))
    model3D.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Background 7"), ROOT.RooFit.Components("bkg7"),
                ROOT.RooFit.LineStyle(styles[8]), ROOT.RooFit.LineColor(colors[8]))
    model3D.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("model3D"), ROOT.RooFit.LineStyle(styles[0]), ROOT.RooFit.LineColor(colors[0]))

    leg_jpsi_mass = ROOT.TLegend(0.55, 0.55, 0.9, 0.90) #(xsize, ysize, xcoord, ycoord)
    leg_jpsi_mass.SetTextSize(0.0159)
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Data"), "Data", "LEP")
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("model3D"), "Model Fit", "L")
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Signal"), "Signal Fit", "L") #"#Signal \ M_{\mu^+\mu^-}, \ Prompt, J/\psi \ Signal \ D^*"
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Background 1"), "#Signal \ M_{\mu^+\mu^-}, \ Prompt \ J/\psi, \ Background \ D^*", "L")
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Background 2"), "#Signal \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Signal \ D^*", "L")
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Background 3"), "#Signal \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Background \ D^*", "L")
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Background 4"), "#Background \ M_{\mu^+\mu^-}, \ Prompt \ J/\psi, \ Signal \ D^*", "L")
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Background 5"), "#Background \ M_{\mu^+\mu^-}, \ Prompt \ J/\psi, \ Background \ D^*", "L")
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Background 6"), "#Background \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Signal \ D^*", "L")
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Background 7"), "#Background \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Background \ D^*", "L")

    frame_jpsi_mass.Draw()
    leg_jpsi_mass.Draw("same")
    cjm.Draw()

    # Legend: jpsi mass
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(50)
    right.SetTextAlign(13)
    right.DrawLatex(0.10,.95,"#bf{CMS} #scale[0.7]{#it{Preliminary}}")
    right.SetTextSize(34)
    right.DrawLatex(.80,.94 , config.lumi)

    cjm.SaveAs(opt[1]['files'][0])

    ## Jpsi mass pull distribution
    cpjm = ROOT.TCanvas("Jpsi mass pull canvas", '', 1400, 900)

    # Creates the pull histogram
    histpull_jpsi_mass = frame_jpsi_mass.pullHist()
    #histpull_jpsi_mass.GetYaxis().SetRangeUser(-50.0, 50.0)

    # New frame to draw pull distribution
    frame_pull_jpsi_mass = jpsi_mass.frame(ROOT.RooFit.Title("Pull Distribution"))
    frame_pull_jpsi_mass.GetXaxis().SetTitle("#M_{\mu^+\mu^-} \ [GeV/c^2]")

    # Add the distribution to the frame
    frame_pull_jpsi_mass.addPlotable(histpull_jpsi_mass, "P")

    frame_pull_jpsi_mass.GetYaxis().SetRangeUser(-15.0, 15.0)
    frame_pull_jpsi_mass.Draw()

    # Legend: jpsi mass pull
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(50)
    right.SetTextAlign(13)
    right.DrawLatex(0.15,.95,"#bf{CMS} #scale[0.7]{#it{Preliminary}}")
    right.SetTextSize(34)
    right.DrawLatex(.80,.94 , config.lumi)

    cpjm.SaveAs(opt[1]['files'][1])

    ### Jpsi dl

    frame_jpsi_dl = jpsi_dl.frame(ROOT.RooFit.Title(""))
    frame_jpsi_dl.GetXaxis().SetTitle("#l_{J/\psi}\ [mm]")

    data.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("jpsi_dl"), ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))

    # Plot the Model components
    model3D.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("Signal"), ROOT.RooFit.Components("signal"),
                ROOT.RooFit.LineStyle(styles[1]), ROOT.RooFit.LineColor(colors[1]))
    model3D.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("Background 1"), ROOT.RooFit.Components("bkg1"),
                ROOT.RooFit.LineStyle(styles[2]), ROOT.RooFit.LineColor(colors[2]))
    model3D.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("Background 2"), ROOT.RooFit.Components("bkg2"),
                ROOT.RooFit.LineStyle(styles[3]), ROOT.RooFit.LineColor(colors[3]))
    model3D.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("Background 3"), ROOT.RooFit.Components("bkg3"),
                ROOT.RooFit.LineStyle(styles[4]), ROOT.RooFit.LineColor(colors[4]))
    model3D.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("Background 4"), ROOT.RooFit.Components("bkg4"),
                ROOT.RooFit.LineStyle(styles[5]), ROOT.RooFit.LineColor(colors[5]))
    model3D.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("Background 5"), ROOT.RooFit.Components("bkg5"),
                ROOT.RooFit.LineStyle(styles[6]), ROOT.RooFit.LineColor(colors[6]))
    model3D.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("Background 6"), ROOT.RooFit.Components("bkg6"),
                ROOT.RooFit.LineStyle(styles[7]), ROOT.RooFit.LineColor(colors[7]))
    model3D.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("Background 7"), ROOT.RooFit.Components("bkg7"),
                ROOT.RooFit.LineStyle(styles[8]), ROOT.RooFit.LineColor(colors[8]))
    model3D.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("model3D"), ROOT.RooFit.LineStyle(styles[0]), ROOT.RooFit.LineColor(colors[0]))

    can = ROOT.TCanvas("canvas_jpsi_dl", '', 1400, 900)
    can.Draw()

    leg_dl = ROOT.TLegend(0.45, 0.55, 0.9, 0.90) #(xsize, ysize, xcoord, ycoord)
    leg_dl.SetTextSize(0.018)
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Data"), "Data", "LEP")
    leg_dl.AddEntry(frame_jpsi_dl.findObject("model3D"), "Model Fit", "L")
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Signal"), "Signal Fit", "L")
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Background 1"), "#Signal \ M_{\mu^+\mu^-}, \ Prompt \ J/\psi, \ Background \ D^*", "L")
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Background 2"), "#Signal \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Signal \ D^*", "L")
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Background 3"), "#Signal \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Background \ D^*", "L")
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Background 4"), "#Background \ M_{\mu^+\mu^-}, \ Prompt \ J/\psi, \ Signal \ D^*", "L")
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Background 5"), "#Background \ M_{\mu^+\mu^-}, \ Prompt \ J/\psi, \ Background \ D^*", "L")
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Background 6"), "#Background \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Signal \ D^*", "L")
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Background 7"), "#Background \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Background \ D^*", "L")

    frame_jpsi_dl.Draw()
    leg_dl.Draw("same")

    can.SetLogy()

    # Legend: jpsi dl
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(50)
    right.SetTextAlign(13)
    right.DrawLatex(0.10,.95,"#bf{CMS} #scale[0.7]{#it{Preliminary}}")
    right.SetTextSize(34)
    right.DrawLatex(.80,.94 , config.lumi)
    
    can.SaveAs(opt[1]['files'][2])

    ## Jpsi dl pull distribution
    cpjdl = ROOT.TCanvas("Jpsi decy length pull canvas", '', 1400, 900)

    # Creates the pull histogram
    histpull_jpsi_dl = frame_jpsi_dl.pullHist()

    # New frame to draw pull distribution
    frame_pull_jpsi_dl = jpsi_dl.frame(ROOT.RooFit.Title("Pull Distribution"))
    frame_pull_jpsi_dl.GetXaxis().SetTitle("#l_{J/\psi}\ [mm]")

    # Add the distribution to the frame
    frame_pull_jpsi_dl.addPlotable(histpull_jpsi_dl, "P")

    frame_pull_jpsi_dl.GetYaxis().SetRangeUser(-15.0, 15.0)
    frame_pull_jpsi_dl.Draw()

    # Legend: jpsi dl pull
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(50)
    right.SetTextAlign(13)
    right.DrawLatex(0.15,.95,"#bf{CMS} #scale[0.7]{#it{Preliminary}}")
    right.SetTextSize(34)
    right.DrawLatex(.80,.94 , config.lumi)

    cpjdl.SaveAs(opt[1]['files'][3])

    ### Dstar

    frame_dstar = dstar_mass.frame(ROOT.RooFit.Title(""))
    frame_dstar.GetXaxis().SetTitle("#M_{K\pi\pi}-M_{K\pi} \ [GeV/c^2]")

    data.plotOn(frame_dstar, ROOT.RooFit.Name("dstar_mass"), ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))

    # Plot the Model components
    model3D.plotOn(frame_dstar, ROOT.RooFit.Name("Signal"), ROOT.RooFit.Components("signal"),
                ROOT.RooFit.LineStyle(styles[1]), ROOT.RooFit.LineColor(colors[1]))
    model3D.plotOn(frame_dstar, ROOT.RooFit.Name("Background 1"), ROOT.RooFit.Components("bkg1"),
                ROOT.RooFit.LineStyle(styles[2]), ROOT.RooFit.LineColor(colors[2]))
    model3D.plotOn(frame_dstar, ROOT.RooFit.Name("Background 2"), ROOT.RooFit.Components("bkg2"),
                ROOT.RooFit.LineStyle(styles[3]), ROOT.RooFit.LineColor(colors[3]))
    model3D.plotOn(frame_dstar, ROOT.RooFit.Name("Background 3"), ROOT.RooFit.Components("bkg3"),
                ROOT.RooFit.LineStyle(styles[4]), ROOT.RooFit.LineColor(colors[4]))
    model3D.plotOn(frame_dstar, ROOT.RooFit.Name("Background 4"), ROOT.RooFit.Components("bkg4"),
                ROOT.RooFit.LineStyle(styles[5]), ROOT.RooFit.LineColor(colors[5]))
    model3D.plotOn(frame_dstar, ROOT.RooFit.Name("Background 5"), ROOT.RooFit.Components("bkg5"),
                ROOT.RooFit.LineStyle(styles[6]), ROOT.RooFit.LineColor(colors[6]))
    model3D.plotOn(frame_dstar, ROOT.RooFit.Name("Background 6"), ROOT.RooFit.Components("bkg6"),
                ROOT.RooFit.LineStyle(styles[7]), ROOT.RooFit.LineColor(colors[7]))
    model3D.plotOn(frame_dstar, ROOT.RooFit.Name("Background 7"), ROOT.RooFit.Components("bkg7"),
                ROOT.RooFit.LineStyle(styles[8]), ROOT.RooFit.LineColor(colors[8]))
    model3D.plotOn(frame_dstar, ROOT.RooFit.Name("model3D"), ROOT.RooFit.LineStyle(styles[0]), ROOT.RooFit.LineColor(colors[0]))

    can_dstar = ROOT.TCanvas("canvas_dstar", '', 1400, 900)
    can_dstar.Draw()

    leg_dstar = ROOT.TLegend(0.45, 0.55, 0.9, 0.90) #(xsize, ysize, xcoord, ycoord)
    leg_dstar.SetTextSize(0.018)
    leg_dstar.AddEntry(frame_dstar.findObject("Data"), "Data", "LEP")
    leg_dstar.AddEntry(frame_dstar.findObject("model3D"), "Model Fit", "L")
    leg_dstar.AddEntry(frame_dstar.findObject("Signal"), "Signal Fit", "L")
    leg_dstar.AddEntry(frame_dstar.findObject("Background 1"), "#Signal \ M_{\mu^+\mu^-}, \ Prompt \ J/\psi, \ Background \ D^*", "L")
    leg_dstar.AddEntry(frame_dstar.findObject("Background 2"), "#Signal \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Signal \ D^*", "L")
    leg_dstar.AddEntry(frame_dstar.findObject("Background 3"), "#Signal \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Background \ D^*", "L")
    leg_dstar.AddEntry(frame_dstar.findObject("Background 4"), "#Background \ M_{\mu^+\mu^-}, \ Prompt \ J/\psi, \ Signal \ D^*", "L")
    leg_dstar.AddEntry(frame_dstar.findObject("Background 5"), "#Background \ M_{\mu^+\mu^-}, \ Prompt \ J/\psi, \ Background \ D^*", "L")
    leg_dstar.AddEntry(frame_dstar.findObject("Background 6"), "#Background \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Signal \ D^*", "L")
    leg_dstar.AddEntry(frame_dstar.findObject("Background 7"), "#Background \ M_{\mu^+\mu^-}, \ No-Prompt \ J/\psi, \ Background \ D^*", "L")

    frame_dstar.Draw()
    leg_dstar.Draw("same")

    # Legend: dstar mass
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(50)
    right.SetTextAlign(13)
    right.DrawLatex(0.10,.95,"#bf{CMS} #scale[0.7]{#it{Preliminary}}")
    right.SetTextSize(34)
    right.DrawLatex(.80,.94 , config.lumi)

    can_dstar.SaveAs(opt[1]['files'][4])

    ## Dstar pull distribution

    # Canvas for Dstar pull 
    cpd = ROOT.TCanvas("Dstar Canvas", '', 1400, 900)

    # Creates pull histogram
    histpull_dstar = frame_dstar.pullHist()

    # New frame to draw pull distribution
    frame_pull_dstar = dstar_mass.frame(ROOT.RooFit.Title("Pull Distribution"))
    frame_pull_dstar.GetXaxis().SetTitle("#M_{K\pi\pi}-M_{K\pi} \ [GeV/c^2]")

    # Add the distribution to the frame
    frame_pull_dstar.addPlotable(histpull_dstar, "P")

    frame_pull_dstar.GetYaxis().SetRangeUser(-15.0, 15.0)
    frame_pull_dstar.Draw()

    # Legend: dstar mass pull
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(50)
    right.SetTextAlign(13)
    right.DrawLatex(0.15,.95,"#bf{CMS} #scale[0.7]{#it{Preliminary}}")
    right.SetTextSize(34)
    right.DrawLatex(.80,.94 , config.lumi)

    cpd.SaveAs(opt[1]['files'][5])

    ###########################################################
    # To save workspace
    wspace = ROOT.RooWorkspace(opt[1]['files'][6])
    
    getattr(wspace, "import")(data)
    getattr(wspace, "import")(model3D)
    
    wspace.writeToFile(opt[1]['files'][7])

    # Jpsi mass chi square  
    chi_square_jpsi_mass = frame_jpsi_mass.chiSquare(config.nparm_jpsi_mass)
    print(f"Xi square for J/psi mass is: {chi_square_jpsi_mass}")
    # Jpsi dl chi square  
    chi_square_jpsi_dl = frame_jpsi_mass.chiSquare(config.nparm_jpsi_dl)
    print(f"Xi square for J/psi decay length is: {chi_square_jpsi_dl}")
    # Dstar chi square
    chi_square_dstar = frame_dstar.chiSquare(config.nparm_dstar)
    print(f"Xi square for Dstar is: {chi_square_dstar}")
    
    with open(opt[1]['files'][7].replace('.root', '') + '.txt', 'w') as f:
        f.write(str(chi_square_jpsi_mass))
        f.write('\n')
        f.write(str(chi_square_jpsi_dl))
        f.write('\n')
        f.write(str(chi_square_dstar))

def splot_jpsidstar(opt, wfile=config.yield_files[0]):

    """

    This function does splot and create plots for signal quantities (jpsi mass, jpsi decay length,
    and dstar delta mass) with the s-weights calculated with splot. It takes the workspace created
    with fit3DJpsiDstar function with the fitted pdfs.

    """

    # Takes the root file with the workspace
    file_root = ROOT.TFile(wfile.replace('_wspace', '') + '_3Dfit.root')
    # Takes the workspace object
    wspace = file_root.Get(wfile.replace('fit_root_files/', ''))

    ## Splot part

    # Takes the 3D pdf
    sPlotmodel3D = wspace.pdf("model3D")
    # Takes the paremeters (yields, pdf variables, etc)
    params = sPlotmodel3D.getVariables()
    # Takes the original data
    data = wspace.data("data")
    """ data_weighted_coffea = data
    data_weighted = data """

    # Takes all yields (signal, background 1, ... , background 7)
    sPlot_signal_frac = params.find("signal_frac")
    sPlot_bkg1_frac = params.find("bkg1_frac")   
    sPlot_bkg2_frac = params.find("bkg2_frac")  
    sPlot_bkg3_frac = params.find("bkg3_frac")
    sPlot_bkg4_frac = params.find("bkg4_frac")  
    sPlot_bkg5_frac = params.find("bkg5_frac") 
    sPlot_bkg6_frac = params.find("bkg6_frac") 
    sPlot_bkg7_frac = params.find("bkg7_frac") 
   
    # Do splot
    sData = ROOT.RooStats.SPlot(
    'sData', 'sData', data, sPlotmodel3D,
    ROOT.RooArgList(sPlot_signal_frac, sPlot_bkg1_frac, sPlot_bkg2_frac, sPlot_bkg3_frac, 
                    sPlot_bkg4_frac, sPlot_bkg5_frac, sPlot_bkg6_frac, sPlot_bkg7_frac,))  
    
    # Make the new weight datasets for all signal
    data_weighted = ROOT.RooDataSet(data.GetName(), data.GetTitle(), data, data.get(), "", "signal_frac_sw")     
    ## Plots part

    # Remove all histograms titles.
    ROOT.gStyle.SetOptTitle(0)

    # Jpsi mass
    jpsi_mass = params.find("jpsi_mass")
    frame_jpsi_mass = jpsi_mass.frame(ROOT.RooFit.Title("Dimuon Invariant mass"))
    frame_jpsi_mass.GetXaxis().SetTitle("#M_{\mu^+\mu^-} \ [GeV/c^2]")
    data_weighted.plotOn(frame_jpsi_mass, ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
    
    # Legend
    leg_jpsi_mass = ROOT.TLegend(0.1,0.7,0.27,0.9) #(xsize, ysize, xcoord, ycoord)
    leg_jpsi_mass.SetTextSize(0.025)
    leg_jpsi_mass.AddEntry(frame_jpsi_mass.findObject("Data"), "Data with sweights", "LEP")

    # Canvas
    cjm = ROOT.TCanvas("canvas_jpsi_mass", '', 1400, 900)
    frame_jpsi_mass.SetAxisRange(0.0, 400, axis="Y")
    frame_jpsi_mass.Draw()
    leg_jpsi_mass.Draw("same")
    cjm.Draw()

    # Legend: jpsi mass
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(50)
    right.SetTextAlign(13)
    right.DrawLatex(0.10,.95,"#bf{CMS} #scale[0.7]{#it{Preliminary}}")
    right.SetTextSize(34)
    right.DrawLatex(.80,.94 , config.lumi)
    cjm.SaveAs(opt[1]['files'][9])

    # Jpsi decay length
    jpsi_dl = params.find("jpsi_dl")
    frame_jpsi_dl = jpsi_dl.frame(ROOT.RooFit.Title(""), ROOT.RooFit.Title("") )
    frame_jpsi_dl.GetXaxis().SetTitle("#l_{J/\psi}\ [mm]")
    data_weighted.plotOn(frame_jpsi_dl, ROOT.RooFit.Name("jpsi_dl"), ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))

    # Legend
    leg_dl = ROOT.TLegend(0.1,0.7,0.27,0.9) #(xsize, ysize, xcoord, ycoord)
    leg_dl.SetTextSize(0.025)
    leg_dl.AddEntry(frame_jpsi_dl.findObject("Data"), "Data with sweights", "LEP")

    # Canvas
    can = ROOT.TCanvas("canvas_jpsi_dl", '', 1400, 900)
    frame_jpsi_dl.SetAxisRange(0.1, 5000, axis="Y")
    frame_jpsi_dl.SetAxisRange(-0.4, 0.4, axis="X")
    frame_jpsi_dl.Draw()
    leg_dl.Draw("same")
    can.Draw()

    # Legend: jpsi dl
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(50)
    right.SetTextAlign(13)
    right.DrawLatex(0.10,.95,"#bf{CMS} #scale[0.7]{#it{Preliminary}}")
    right.SetTextSize(34)
    right.DrawLatex(.80,.94 , config.lumi)
    can.SetLogy()
    can.SaveAs(opt[1]['files'][10])

    # Dstar mass
    dstar_mass = params.find("dstar_mass")
    frame_dstar = dstar_mass.frame(ROOT.RooFit.Title(""))
    frame_dstar.GetXaxis().SetTitle("#M_{K\pi\pi}-M_{K\pi} \ [GeV/c^2]")
    data_weighted.plotOn(frame_dstar, ROOT.RooFit.Name("dstar_mass"), ROOT.RooFit.Name("Data"), ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
    
    # Legend
    leg_dstar = ROOT.TLegend(0.1,0.7,0.27,0.9) #(xsize, ysize, xcoord, ycoord)
    leg_dstar.SetTextSize(0.025)
    leg_dstar.AddEntry(frame_dstar.findObject("Data"), "Data with sweights", "LEP")

    # Canvas for Dstar  
    cpd = ROOT.TCanvas("Dstar Canvas", '', 1400, 900)
    frame_dstar.SetAxisRange(0.0, 850, axis="Y")
    frame_dstar.Draw()
    leg_dstar.Draw("same")
    cpd.Draw()

    # Legend: dstar mass
    right = ROOT.TLatex()
    right.SetNDC()
    right.SetTextFont(43)
    right.SetTextSize(50)
    right.SetTextAlign(13)
    right.DrawLatex(0.10,.95,"#bf{CMS} #scale[0.7]{#it{Preliminary}}")
    right.SetTextSize(34)
    right.DrawLatex(.80,.94 , config.lumi)
    
    # Save canvas
    cpd.SaveAs(opt[1]['files'][11])

    ## Coffea - hist part
    from coffea import processor, hist
    from coffea.util import save
    import numpy as np
    # Takes the root file with the workspace
    file_root = ROOT.TFile(wfile.replace('_wspace', '') + '_3Dfit.root')
    # Takes the workspace object
    wspace = file_root.Get(wfile.replace('fit_root_files/', ''))

    weight = np.ones(len(data_weighted.to_numpy()['jpsi_mass']))
    for i in range(len(data_weighted.to_numpy()['jpsi_mass'])):
        weight[i] = weight[i] * sData.GetSWeight(i, "signal_frac_sw")
        #print(f'weight: {weight[i]}')

    data_weighted = sData.GetSDataSet()

    # Coffea histograms
    histo = processor.dict_accumulator({'JpsiDstar': processor.dict_accumulator({
                'Jpsi_mass': hist.Hist("Events", hist.Bin("mass", "$M_{\mu^+\mu^-}$ [GeV/$c^2$]", 100, 2.95, 3.25)), 
                'Jpsi_dl': hist.Hist("Events", hist.Bin("dl", "decay length", 100, -0.5, 1.4)),
                'Dstar_deltamr': hist.Hist("Events", 
                                        hist.Cat("chg", "charge"), 
                                        hist.Bin("deltamr", "$\Delta m_{refit}$ [$GeV/c^2$]", 100, 0.13957, 0.16)),})})
    
    histo['JpsiDstar']['Jpsi_mass'].fill(mass=data_weighted.to_numpy()['jpsi_mass'], weight = weight)
    histo['JpsiDstar']['Dstar_deltamr'].fill(chg='right charge', deltamr=data_weighted.to_numpy()['dstar_mass'], weight = weight)
    histo['JpsiDstar']['Jpsi_dl'].fill(dl=data_weighted.to_numpy()['jpsi_dl'], weight = weight)

    save(histo, 'Charmonium_' + config.set[10:14] + '_sweight.coffea')

    return data_weighted, sData
  
def yields_jpsidstar(yield_list=config.yield_files):

    import csv
    import numpy as np
    
    with open(config.csv_name, 'w') as c:
        # Creates the csv writer
        writer = csv.writer(c)
        # write a row to the csv file
        header = ['Case', 'N_evts_total', 'N_signal', 'N_signal_err', 
                  'N_background', 'N_background_err', 'N_non_prompt',
                  'N_non_prompt_err', 'chi_square_jpsi_mass','chi_square_jpsi_dl',
                  'chi_square_dstar' , 'Zsb', 'Zsb_err',
                  'Zssb', 'Zssb_err', 'Z12', 'Z12_err',]
        writer.writerow(header)

        for f in yield_list:

            with open(f.replace('_wspace', '') + '_3Dfit.txt', 'r') as tx:
                list_chi = tx.readlines()
                chi_square_jpsi_mass = float(list_chi[0])
                chi_square_jpsi_dl = float(list_chi[1])
                chi_square_dstar = float(list_chi[2])
               
            file_root = ROOT.TFile(f.replace('_wspace', '') + '_3Dfit.root')
            print()
            wspace = file_root.Get(f.replace('fit_root_files/', ''))

            print(wspace.var(""))

            model3D = wspace.pdf("model3D")

            print("Params")
            params = model3D.getVariables()
            data = wspace.data("data")

            # N events
            Nevts = data.sumEntries()

            # Frac signal (Jpsi mass signal, prompt, dstar delta m signal)
            frac_signal = params.find("signal_frac")

            # Frac background 1 (Jpsi mass signal, prompt, dstar delta m background)
            frac_back1 = params.find("bkg1_frac")

            # Frac background 2 (Non-Prompt signal)
            frac_back2 = params.find("bkg2_frac")

            nevts_signal_val = Nevts * frac_signal.getVal()
            #nevts_signal_error = Nevts * frac_signal.getError()
            nevts_signal_error = nevts_signal_val**0.5

            #x_frac_back = ufloat(frac_signal.getVal(), frac_signal.getError())
            #y_back = ufloat(nevts_background_val, nevts_background_error)

            # N background events
            nevts_background_val = Nevts - nevts_signal_val
            nevts_background_error = nevts_background_val**0.5

            # N non-prompt signal events
            nevts_non_prompt_val = Nevts * (1-frac_signal.getVal()) * (1-frac_back1.getVal()) * frac_back2.getVal()
            nevts_non_prompt_err = nevts_non_prompt_val**0.5

            ## Using uncertaities to compute fom and error

            # Zsb
            x_zsb = ufloat(nevts_signal_val, nevts_signal_error)
            y_zsb = ufloat(nevts_background_val, nevts_background_error)
            fom_zsb = x_zsb/(y_zsb)**0.5
            fom_zsb_val = fom_zsb.nominal_value
            fom_zsb_error = fom_zsb.std_dev

            # Zssb
            x_zssb = ufloat(nevts_signal_val, nevts_signal_error)
            y_zssb = ufloat(nevts_background_val, nevts_background_error)
            fom_zssb = x_zssb/(x_zssb + y_zssb)**0.5
            fom_zssb_val = fom_zssb.nominal_value
            fom_zssb_error = fom_zssb.std_dev

            # Z12
            x_z12 = ufloat(nevts_signal_val, nevts_signal_error)
            y_z12 = ufloat(nevts_background_val, nevts_background_error)
            fom_z12 = 2*((x_z12 + y_z12)**0.5 - (y_z12)**0.5 )
            fom_z12_val = fom_z12.nominal_value
            fom_z12_error = fom_z12.std_dev

            row = [f, Nevts, nevts_signal_val, nevts_signal_error, nevts_background_val, nevts_background_error,
                   nevts_non_prompt_val, nevts_non_prompt_err, chi_square_jpsi_mass, chi_square_jpsi_dl,
                   chi_square_dstar, fom_zsb_val, fom_zsb_error,
                   fom_zssb_val, fom_zssb_error, fom_z12_val, fom_z12_error]
            writer.writerow(row)
            
            msg = f"""Summary:
        Nevt total = {Nevts:.2f} 
        Nevt signal = {(nevts_signal_val):.2f} +- {(nevts_signal_error):.2f}
        Nevt bg  = {(nevts_background_val):.2f} +- {(nevts_background_error):.2f} 
        Nevt non-prompt  = {(nevts_non_prompt_val):.2f} +- {(nevts_non_prompt_err):.2f} 
        """

            print(msg)
             # Creates a csv file to save the number of quantities
            with open(f.replace('_wspace', '') + '_3Dfit_yields.csv', 'w') as yi:
                # Creates the csv writer
                writer = csv.writer(yi)
                # write a row to the csv file
                header = ['Component', 'Value', 'Error', 'Comment']
                writer.writerow(header)

                levt = ['Num. Total Events', f'{Nevts:.2f}' , 0, '-']
                writer.writerow(levt)

                lsig = ['Num. Signal Events', f'{nevts_signal_val:.2f}' , f'{nevts_signal_error:.2f}', f'~ {(nevts_signal_val/Nevts*100):.2f} % of total']
                writer.writerow(lsig)

                lback = ['Num. Background Events', f'{nevts_background_val:.2f}' , f'{nevts_background_error:.2f}', f'~ {(nevts_background_val/Nevts*100):.2f} % of total']
                writer.writerow(lback)

                lnonprompt = ['Num. "Signal" Events With non-prompt J/ψ', f'{nevts_non_prompt_val:.2f}' , f'{nevts_non_prompt_err:.2f}', f'~ {(nevts_non_prompt_val/Nevts*100):.2f} % of total']
                writer.writerow(lnonprompt)
            
            ## Jpsi fit parameters

            # Mass
            mass_jpsi = params.find("mean_jpsi")
            mass_jpsi_val = mass_jpsi.getVal()
            mass_jpsi_error = mass_jpsi.getError()

            if config.jpsi_mass_pdf['signal'] == 'CBG':
                #Sigma gauss
                sigma_gauss_jpsi = params.find("sigma_gauss")
                sigma_gauss_jpsi_val = sigma_gauss_jpsi.getVal()
                sigma_gauss_jpsi_error = sigma_gauss_jpsi.getError()
            # Sigma CB
            sigma_cb_jpsi = params.find("sigma_cb")
            sigma_cb_jpsi_val = sigma_cb_jpsi.getVal()
            sigma_cb_jpsi_error = sigma_cb_jpsi.getError()

            ## Dstar fit parameters

            # Delta mass
            dmass_dstar = params.find("dstar_mean")
            dmass_dstar_val = dmass_dstar.getVal()
            dmass_dstar_error = dmass_dstar.getError()

            # Sigma dstar
            if config.dstar_pdf['signal'] == 'johnson':
                sigma_dstar = params.find("dstar_lambda")
                sigma_dstar_val = sigma_dstar.getVal()
                sigma_dstar_error = sigma_dstar.getError()
            elif  config.dstar_pdf['signal'] == 'doubleG':
                sigma_dstar_g1 = params.find("dstar_sigma_g1")   ## I'm not sure!
                sigma_dstar_g2 = params.find("dstar_sigma_g2")

                sigma_dstar_g1_val = sigma_dstar_g1.getVal()
                sigma_dstar_g1_error = sigma_dstar_g1.getError()

                sigma_dstar_g2_val = sigma_dstar_g2.getVal()
                sigma_dstar_g2_error = sigma_dstar_g2.getError()

                sigma_dstar_val = (sigma_dstar_g1_val + sigma_dstar_g2_val)/2
                sigma_dstar_error = (sigma_dstar_g1_error + sigma_dstar_g2_error)/2
            
            

            # Sigma CB
            sigma_cb_jpsi = params.find("sigma_cb")
            sigma_cb_jpsi_val = sigma_cb_jpsi.getVal()
            sigma_cb_jpsi_error = sigma_cb_jpsi.getError()

            
            with open(f.replace('_wspace', '') + '_3Dfit_pdf_params.csv', 'w') as yi:
                # Creates the csv writer
                writer = csv.writer(yi)
                # write a row to the csv file
                header = ['Parameter', 'Value', 'Error', ]
                writer.writerow(header)

                # Jpsi parameters

                lxisq_jpsi_mass = ['𝜒²/d.o.f - J/ψ mass ', f'{chi_square_jpsi_mass:.2f}' , 0,]
                writer.writerow(lxisq_jpsi_mass)

                lxisq_jpsi_dl = ['𝜒²/d.o.f - J/ψ decay length', f'{chi_square_jpsi_dl:.2f}' , 0,]
                writer.writerow(lxisq_jpsi_dl)

                lmass_jpsi = ['Mass - J/ψ [GeV/c²]', f'{mass_jpsi_val:.5f}' , f'{mass_jpsi_error:.5f}']
                writer.writerow(lmass_jpsi)

                if config.jpsi_mass_pdf['signal'] == 'CBG':
                	lgauss_jpsi_sigma = ['Gaussian Sigma - J/ψ [GeV/c²]', f'{sigma_gauss_jpsi_val:.5f}' , f'{sigma_gauss_jpsi_error:.5f}']
                	writer.writerow(lgauss_jpsi_sigma)

                lcb_sigma = ['Crystal Ball Sigma - J/ψ [GeV/c²]', f'{sigma_cb_jpsi_val:.5f}' , f'{sigma_cb_jpsi_error:.5f}',]
                writer.writerow(lcb_sigma)

                # D* parameters

                lxisq_dstar = ['𝜒²/d.o.f - D* ', f'{chi_square_dstar:.2f}' , 0,]
                writer.writerow(lxisq_dstar)

                ldmass_dstar = ['Delta Mass - D* [GeV/c²]', f'{dmass_dstar_val:.7f}' , f'{dmass_dstar_error:.7f}']
                writer.writerow(ldmass_dstar)

                llambda_dstar = ['Johnson Sigma - D* [GeV/c²]', f'{sigma_dstar_val:.7f}' , f'{sigma_dstar_error:.7f}']
                writer.writerow(llambda_dstar)

    return params
    
#bot.bot_message(f"3D Fit Started")

if (args.fit):
    import time

    tstart = time.time()
    for opt in config.cases.values():
        fit3DJpsiDstar(opt)
    print(f'Finished in: {( time.time() - tstart)} s')

if (args.yields):
    p = yields_jpsidstar()

if (args.splot):
    import time

    tstart = time.time()
    for opt in config.cases.values():
        splot_jpsidstar(opt)
    print(f'Finished in: {( time.time() - tstart)} s')
    
if (args.coffea):
    import time

    tstart = time.time()
    for opt in config.cases.values():
        make_coffea_hist(opt)
    print(f'Finished in: {( time.time() - tstart)} s')

#bot.bot_message(f"3D Fit Finished")
#bot.bot_image("dstar_mass_projection.png")
#bot.bot_image("jpsi_dl_projection.png")


