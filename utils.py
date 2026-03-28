# PLOTTER / FITTER class

from ROOT import TCanvas, TGraphErrors, TLegend, gPad, gStyle, TF1, kBlue, kRed # type: ignore
from array import array
import numpy as np

class fitPlotter():
    """ utility class to plot graphs and do fits with ROOT """
    def __init__(self, name=""):
        self._canvas = TCanvas() 
        self._name   = name
        self._graphs  = []
        self._legends = []
        self._funcs = []

    def addGraph(self, x, y, x_err=np.array([]), y_err=np.array([]), title="graph", fit_formula="pol1", color=kRed, setparam = np.array([]), xrange = None):
        """ adds graph and eventually performs fit (else pass fit_formula=None) """
        # using c-style arrays breaks out of bound errors, so we have to implement some sanity checks
        if len(x) != len(y):
            raise IndexError("lenght of provided data are not the same")
        elif (x_err.any()) and len(x_err) != len(x):
            raise IndexError("err_x lenght does not match x")
        elif (y_err.any()) and len(y_err) != len(y):
            raise IndexError("err_x lenght does not match x")
            
        n = len(x)

        # init form empty errors
        if len(x_err) == 0:
            x_err = np.zeros(n)

        if len(y_err) == 0:
            y_err = np.zeros(n)

        x_arr, y_arr = array('d', x), array('d', y)
        ex_arr, ey_arr = array('d', x_err), array('d', y_err)

        graph = TGraphErrors(n, x_arr, y_arr, ex_arr, ey_arr)
        graph.SetTitle(title)
        graph.SetMarkerStyle(20)
        graph.SetMarkerColor(color)
        graph.SetLineColor(color)

        leg = TLegend(0.12, 0.75, 0.45, 0.88)
        leg.SetBorderSize(1)
        leg.SetFillColor(0)
        #leg.AddEntry(graph, "data points", "ple")

        if (fit_formula):
            if not isinstance(fit_formula, list):
                
                print(f"\n--- fit Results for: {title} ---")

                func_name = f"f_{len(self._graphs)}"
                
                if xrange is not None:
                    func = TF1(func_name, fit_formula, xrange[0],xrange[1])
                else:
                    func = TF1(func_name, fit_formula)

                if setparam.any():
                    setparam = array('d', setparam)
                    func.SetParameters(setparam)
                
                func.SetLineColor(kBlue)

                if xrange is not None:
                    graph.Fit(func, "SQR+")  #Salva, Quiet, Range,( ottimizzazione Migliorata), disporre + grafici
                else:
                    graph.Fit(func, "SQ+")
                
                # fit stats
                chi2 = func.GetChisquare()
                ndf = func.GetNDF()
                pvalue = func.GetProb()
                print(f"Function: {fit_formula}")
                print(f"Chi2/NDF: {chi2:.4f} / {ndf}")
                print(f"p-value:  {pvalue:.4f}\n")

                # fit parameters stuff
                params = np.zeros((func.GetNpar(),2))  # simo: ora viene ritornato un array numpy bidimensionale dei parametri e degli errori
                
                for i in range(func.GetNpar()):
                    name = func.GetParName(i)
                    val  = func.GetParameter(i)
                    err  = func.GetParError(i)
                    print(f"{name}: {val:.4f} +/- {err:.4f}")
                    params[i,0] = func.GetParameter(i)
                    params[i,1] = func.GetParError(i)

                print("-" * 32)

                leg.AddEntry(func, "fit function", "l")


            else:
                # now, fitting multiple functions on same graph 
                #  fit_formula = [pol1,pol3,...], xrange = [[100,200],[200,300],..],
                #  setparam = [np.array,np.array,...] 
                # if range is not specified, it shall be [None,None,...]
                # to be improved: now fits are done on all graphs of the canvas.
                n_fits = len(fit_formula)
                if xrange is not None:
                    if len(xrange) != len(fit_formula):
                        raise IndexError("number of formulas to fit and number of x-ranges must be equal")
                else:
                    xrange = [None] * n_fits

                if not isinstance(setparam, list):
                    setparam = [setparam] * n_fits

                print(f"\n--- fit Results for: {title} --- \n ! Multiple fits are being committed !")
                params = [] #now params will be [np.array([[a,err_a],[b,err_b]]) , np.array(...), ...]
                
                for i_fit_formula, i_xrange, i_setparam, I in zip(fit_formula, xrange, setparam, range(n_fits)):

                    print(f"fit {I}, f = {i_fit_formula}")
                    
                    func_name = f"f_{len(self._graphs)}{i_fit_formula}{I}"

                    if i_xrange is not None:
                        func = TF1(func_name, i_fit_formula, i_xrange[0], i_xrange[1])
                    else:
                        func = TF1(func_name, i_fit_formula)

                    self._funcs.append(func)

                    if i_setparam.any():
                        i_setparam = array('d', i_setparam)
                        func.SetParameters(i_setparam)
                    
                    func.SetLineColor(kBlue - I)

                    if i_xrange is not None:
                        graph.Fit(func, "SQR+")  #Salva, (Quiet), Range,( ottimizzazione Migliorata), disporre + grafici
                    else:
                        graph.Fit(func, "SQ+")
                    
                    # fit stats
                    chi2 = func.GetChisquare()
                    ndf = func.GetNDF()
                    pvalue = func.GetProb()
                    print(f"Function: {i_fit_formula}")
                    print(f"Chi2/NDF: {chi2:.4f} / {ndf}")
                    print(f"p-value:  {pvalue:.4f}\n")

                    # fit parameters stuff
                    i_param = np.zeros((func.GetNpar(),2)) 
                    
                    for i in range(func.GetNpar()):
                        name = func.GetParName(i)
                        val  = func.GetParameter(i)
                        err  = func.GetParError(i)
                        print(f"{name}: {val:.4f} +/- {err:.4f}")
                        i_param[i,0] = func.GetParameter(i)
                        i_param[i,1] = func.GetParError(i)
                    
                    params.append(i_param)

                    print("-" * 32)

                    leg.AddEntry(func, i_fit_formula, "l")

            # fuck the garbage collector
        self._graphs.append(graph)
        self._legends.append(leg)

        # returning (masked) fit results (if fit was performed)
        if fit_formula: 
            return params
        else:
            return None

    def drawCanvas(self, legend=True, dimX=1000, dimY=500):
        """ draws entire canvas """
        nGraphs = len(self._graphs)
        if nGraphs < 1: return
        
        cols = 2
        rows = (nGraphs + 1) // 2 
        
        self._canvas = TCanvas(self._name, self._name, dimX, dimY * rows)
        self._canvas.Divide(cols, rows)

        for i in range(nGraphs):
            pad = self._canvas.cd(i+1)

            pad.SetLeftMargin(0.15) # setting padding
            pad.SetBottomMargin(0.12)

            gStyle.SetOptFit(1100) # setting fit stats
            gPad.SetGrid() 
            
            self._graphs[i].Draw("AP")
            
            if legend: # sometimes we dont want it drawn!
                self._legends[i].Draw()

        self._canvas.Draw()

    def updateLegend(self,labels,index=-1):
        """ updates the legends entries (with labels = [string]), and returns the legend to give more control. CANVAS NEEDS TO BE DRAWN """
        if len(self._legends) < 1:
            raise IndexError("no legends present!")

        # retrieving legend and entries into it
        leg = self._legends[index]
        entries = leg.GetListOfPrimitives()

        if len(entries) != len(labels):
            raise IndexError("lenght of labels does not match number of entries in legend")

        # setting labels
        for i in range(0, len(entries)):
            entries.At(i).SetLabel(labels[i])

        # updating (drawn) canvas
        self._canvas.Modified()
        self._canvas.Update()
        
        return self._legends[index]
        

    def saveCanvas(self, fileName="canvas.png"):
        """ saves canvas: has logic to modify name (but its not that useful) """
        if fileName == "canvas.png" and self._name:
            fileName = self._name + ".png"
        self._canvas.SaveAs(fileName)

# example use of TEXTABLER
# x = np.array([1,2,3])
# y = np.array([2,3,4])
# err_x = np.array([0.1,0.2,0.3])
# err_y = np.array([0.1,0.2,0.3])
# texTabler([x,y], [err_x, err_y], ["x", "y"], digits = 4)

def texTabler(data, errors, names, digits=3):
    """ turns data = [np.array, np.array, ...] and errors = [np.array, np.array, ...] into table with names = [string, string, ...] """
    if len(data) != len(errors) or len(data) != len(names):
        raise IndexError("mistakes in lists lenghts! check them")

    title = ""
    for i in range(0,len(names)-1):
        title += f"${names[i]}$ & $\delta {names[i]}$ & "
    title+= f"${names[len(names)-1]}$ & $\delta {names[len(names)-1]}$ \\\\"

    print(title)
    
    for i in range(0, len(data[0])):
        row = ""

        for j in range(0, len(data)-1):
            row += f"{data[j][i]:.{digits}f} & {errors[j][i]:.{digits}f} & "

        row += f"{data[len(data)-1][i]:.{digits}f} & {errors[len(data)-1][i]:.{digits}f} \\\\"

        print(row)

# we have to remove the contribution for B=0
# (our measurements need to have the same currents, or else we need to interpolate between the points...)
# NOT NEEDED ANYMORE : DEPRECATED
def removeBackground(data, back, err_data, err_back):
    """ removes background data `back` from `data` (propagating errors as sums of squares) """
    newdata     = []
    err_newdata = []

    for i in range(0,len(data)):
        newdata.append(data[i] - back[i])
        err_newdata.append((err_data[i]**2 + err_back[i]**2)**0.5)

    return newdata, err_newdata
    
# MEAN CALCULATOR w/ ERROR PROPAGATION
# TODO: use numpy!

def meanCalc(values):
    """ returns mean of values (w/ error) weighted by errors of: values = List[[value1, err1], [value2, err2], ...] """
    mean = 0
    mean_err = 0

    for v in values:
        mean_err += 1 / (v[1])**2      # 1 / sigma^2
        mean     += v[0] / (v[1])**2   # value / sigma^2

    # right now mean_err = sum of weights
    mean /= mean_err

    # this is the true error
    mean_err = 1 / (mean_err)**0.5

    return mean, mean_err

# Mean error calculator

def MeanError(s1,s2):
    "used to calculate mean of two arrays of np.array([mean,error],[],...) type"
    if (np.shape(s1) != np.shape(s2)):
        raise("TypeError: shape of imput arrays must be equal")
    else:
        rel_error = np.sqrt((s1[:,1]/s1[:,0])**2 + (s2[:,1]/s2[:,0])**2)
        stima = (s1 + s2)/len(s1)
        stima[:,1] = rel_error * stima[:,0]
        return stima

# Z test calculator!

import scipy.stats as stats

def testZ(media_campione, media_popolazione, dev_std_popolazione, n, alfa=0.05, tipo_test='bilaterale'):
    """ returns p-value of z-test """
    
    # 1. Calcolo dell'errore standard
    errore_standard = dev_std_popolazione / np.sqrt(n)
    
    # 2. Calcolo della statistica Z
    Z = (media_campione - media_popolazione) / errore_standard
    print(f"Statistica Z calcolata: {Z:.4f}")
    
    # 3. Calcolo del P-value in base al tipo di test
    if tipo_test == 'bilaterale':
        # Moltiplico per 2 perché guardo entrambe le code
        p_value = 2 * (1 - stats.norm.cdf(abs(Z)))
    elif tipo_test == 'maggiore':
        # Coda di destra
        p_value = 1 - stats.norm.cdf(Z)
    elif tipo_test == 'minore':
        # Coda di sinistra
        p_value = stats.norm.cdf(Z)
    else:
        raise ValueError("tipo_test deve essere 'bilaterale', 'maggiore' o 'minore'")
        
    print(f"P-value calcolato: {p_value:.4f}")
    print(f"Livello di significatività (alfa): {alfa}")
    
    # 4. Conclusione del test
    print("-" * 30)
    if p_value < alfa:
        print("Conclusione: Rifiutiamo l'ipotesi nulla (H0).")
        print("Il risultato è statisticamente significativo al livello del 5%.")
    else:
        print("Conclusione: Non ci sono prove sufficienti per rifiutare l'ipotesi nulla (H0).")
        print("Il risultato NON è statisticamente significativo al livello del 5%.")

    return p_value

# Zscore function

def Zscore(s1, s2, Print = True):
    "used to compare array of np.array([mean,error] measures. returns z score "
    if (np.shape(s1) != np.shape(s2)):
        raise("TypeError: shape of imput arrays must be equal")
    else:
        errors = np.sqrt(s1[:,1]**2 + s2[:,1] **2)
        z = (s2[:,0]-s1[:,0])/errors
        if Print:
            for i in range(len(s1)):
                print(f"z value of param {i} :", round(z[i],3))
            print("\n")
    
        return z

# Amprobe 37-XRA for errors on current
# converting all in mA

import numpy as np

def Amprobe(current,unit = "mA"):
    """used to calculate the error on i""" 
    array = current
    error = []
    
    # converting in mA if measures are in A
    if (unit == "A") : 
        array = current*1000 
        
    # calculating errors based on range
    for data in array:
        if (abs(data) < 0.1):
            error.append (0.005*abs(data) + 0.001*0.001*10) 
        elif abs(data) < 400 : 
            error.append (0.005*abs(data) + 0.001*5) 
        else : 
            error.append (0.015*abs(data) + 10)

    if (unit == "A") : 
        error = np.array(error) / 1000

    return np.array(error)

# Keithley DMM6500 for errors on voltage
# all measures are in mV 

def Keithley (voltage) :
    """used to calculate the error on V"""
    error = []

# calculating errors based on range

    for data in voltage:
        if (abs(data) < 100) : 
            error.append((0.0035*abs(data) + 0.0035*100)/100) # in the booklet errors are specified as percentages
        else : 
            error.append ((0.0030*abs(data) + 0.0006*1000)/100)
    
    return np.array(error)

# magnetic meter for errors on B values
# all measures are in mT

def Teslameter (magneticfield) : 
    """ used to calculate the error on B """
    error = []

#calculate errors based on range

    for data in magneticfield:
        #error.append(0.005*abs(data) + 1)
        error.append(0.05*abs(data) + 1)
    return np.array(error)


# Amprobe 37_XRA for errors on voltage
# all measures are in mV

def Amprobe_V (voltage):
    """ used to calculate errors on V"""
    error = []

# calculate errors based on range
    for data in voltage:
        error.append(0.001*abs(data) + 0.1*5)

    return np.array(error)
        