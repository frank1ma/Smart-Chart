# import necessary modules in PySide6
from PySide6.QtWidgets import QApplication,QMainWindow
from smart_chart import SmartChart
import control
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # example of bode plot
        custom_frame = SmartChart(plot_type="bode_mag",sub_plot_type="bode_phase")
        
        # example of nichols plot
        #custom_frame = SmartChart(plot_type="nichols")

        self.setCentralWidget(custom_frame)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.setGeometry(800, 400, 800, 600)
    window.show()
    widget:SmartChart = window.centralWidget()
    #widget.chart_view.sub_chart=None
    #widget.chart_view2.hide()

    # sys 1 
    sys1 = control.tf([10], [1,2,1,1])
    #sys1 = control.zpk([-1,-2,4],[-30,-1,-2,-3],100)
    mag,phase,omega = control.bode_plot(sys1,dB=True,deg=True,omega_limits=(0.1,2500),omega_num=500,plot=False)

    # sys 2
    sys2 = control.tf([10], [1,5,5,1])
    mag1,phase1,omega1 = control.bode_plot(sys2,dB=True,deg=True,omega_limits=(0.1,2500),omega_num=500,plot=False)

    
    # plot nichols chart
    #wrapped_phase_degree = widget.chart_view.wrapPhase(phase)
    # widget.chart_view.plotXY(phase/np.pi*180,20*np.log10(mag))
    # widget.chart_view.setNicholsFrequencyData(omega)
    # widget.chart_view.showNicholsGrid()

    # widget.chart_view.plotXY(phase1/np.pi*180,20*np.log10(mag1),hold_on=True)
    # widget.chart_view.setNicholsFrequencyData(omega1)



    # plot the bode chart / uncomment line #custom_frame = SmartChart(plot_type="bode_mag",sub_plot_type="bode_phase")

    widget.chart_view.plotXY(omega,20*np.log10(mag))

    widget.chart_view.x_axis.setTitleText("Frequency (Hz)")
    widget.chart_view.y_axis.setTitleText("Magnitude (dB)")
    widget.chart_view2.plotXY(omega,phase/np.pi*180)

    widget.chart_view2.x_axis.setTitleText("Frequency (Hz)")
    widget.chart_view2.y_axis.setTitleText("Phase (deg)")
    #widget.chart_view.calculateGainMargin(omega,20*np.log10(mag),phase/np.pi*180)
    #widget.chart_view.showGainMarginMarker(omega,20*np.log10(mag),phase/np.pi*180,True)
    #widget.chart_view.calculatePhaseMargin(omega,20*np.log10(mag),phase/np.pi*180,True)
    app.exec()