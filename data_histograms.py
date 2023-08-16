from coffea.util import load
from coffea import hist
import numpy as np
import matplotlib.pyplot as plt
import mplhep

def create_plot1d(hist1d, lumi, log=False, ax=None, typ=None):
    
    from matplotlib.offsetbox import AnchoredOffsetbox, TextArea
    plt.style.use(mplhep.style.CMS)
    plt.rcParams.update({
        'font.size': 16,
        'axes.titlesize': 18,
        'axes.labelsize': 18,
        'xtick.labelsize': 14,
        'ytick.labelsize': 14
    })
    
    if typ == 'data':
        
        data_err_opts = {
        'linestyle': 'none',
        'marker': '.',
        'markersize': 10.,
        'color': 'k',
        'elinewidth': 1,
        }
        ax = hist.plot1d(hist1d, error_opts=data_err_opts)
        
        # CMS style
    
        CMS = plt.text(0.03, 0.93, "CMS",
                      fontsize=22,
                      fontweight='bold',
                      horizontalalignment='left',
                      verticalalignment='bottom',
                      transform=ax.transAxes
                     )
        pre = plt.text(0.03, 0.88, "Preliminary",
                      fontsize=19,
                      fontstyle='italic',
                      horizontalalignment='left',
                      verticalalignment='bottom',
                      transform=ax.transAxes
                     )
        lumi = plt.text(1., 1., r"" + lumi +  " fb$^{-1}$ (13 TeV)",
                    fontsize=18,
                    fontstyle='normal',
                    horizontalalignment='right',
                    verticalalignment='bottom',
                    transform=ax.transAxes
                   )
        
        
    elif typ == 'mc':
        
        fill_opts = {
        'alpha': 0.8,
        'edgecolor':(0,0,0,.5)
        }
        
        ax = hist.plot1d(hist1d, fill_opts=fill_opts)
        
        # CMS format
        hfont = {'fontname':'Helvetica'}    
        plt.text(0.13, 0.89, "CMS", fontdict=hfont,  fontweight='bold', transform=plt.gcf().transFigure)
        plt.text(0.19, 0.89, "Simulation", fontdict=hfont, style='italic', transform=plt.gcf().transFigure)
        
    else:
        
        data_err_opts = {
        'linestyle': 'none',
        'marker': '.',
        'markersize': 10.,
        'color': 'k',
        'elinewidth': 1,}
        
            
        ax = hist.plot1d(hist1d, ax=ax)#, error_opts=data_err_opts)

   
    ax.legend().remove()
    
    return ax


if __name__ == '__main__':

    data_file = '/afs/cern.ch/work/m/mabarros/public/CMSSW_10_6_12/src/analysis_data/analysis_fit/2017/Charmonium_2017_vtx0p05.coffea'
    lumi='41.48'
    data = load(data_file)
    year = '2017'

    ax = create_plot1d(data['JpsiDstar']['Dstar_D0pt'], lumi, typ='data')
    plt.savefig(year + '/hists/Dstar_D0pt.png')

    ax = create_plot1d(data['JpsiDstar']['Dstar_D0cosphi'], lumi, typ='data')
    plt.savefig(year + '/hists/Dstar_D0cosphi.png')

    ax = create_plot1d(data['JpsiDstar']['Dstar_D0dlSig'], lumi, typ='data')
    plt.savefig(year + '/hists/Dstar_D0dlSig.png')
    
    ax = create_plot1d(data['JpsiDstar']['Dstar_Kpt'], lumi, typ='data')
    plt.savefig(year + '/hists/Dstar_Kpt.png')

    ax = hist.plot1d(data['JpsiDstar']['Dstar_Kchindof'])
    plt.savefig(year + '/hists/Dstar_Kchindof.png')

    ax = hist.plot1d(data['JpsiDstar']['Dstar_KnValid'])
    plt.savefig(year + '/hists/Dstar_KnValid.png')

    ax = hist.plot1d(data['JpsiDstar']['Dstar_Kdxy'])
    plt.savefig(year + '/hists/Dstar_Kdxy.png')

    ax = hist.plot1d(data['JpsiDstar']['Dstar_Kdz'])
    plt.savefig(year + '/hists/Dstar_Kdz.png')

    ax = hist.plot1d(data['JpsiDstar']['Dstar_pispt'])
    plt.savefig(year + '/hists/Dstar_pispt.png')

    ax = hist.plot1d(data['JpsiDstar']['Dstar_pischindof'])
    plt.savefig(year + '/hists/Dstar_pischindof.png')

    ax = hist.plot1d(data['JpsiDstar']['Dstar_pisnValid'])
    plt.savefig(year + '/hists/Dstar_pisnValid.png')