import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from .filters import Filtering


class plotSettings:
    def __init__(self, mpl, style="dark_background"):

        self.mpl = mpl
        self.style = style
        # self.updateSettings()

    def updateSettings(self):

        fs = 16

        # mpl.style.use('seaborn')
        self.mpl.style.use(self.style)
        self.mpl.rcParams["figure.figsize"] = [6, 6]
        self.mpl.rcParams["figure.dpi"] = 80
        self.mpl.rcParams["savefig.dpi"] = 100

        self.mpl.rcParams["font.size"] = fs
        self.mpl.rcParams["legend.fontsize"] = fs
        self.mpl.rcParams["figure.titlesize"] = fs

        self.mpl.rcParams["ytick.labelsize"] = fs
        self.mpl.rcParams["xtick.labelsize"] = fs
        self.mpl.rcParams["axes.titlesize"] = fs
        self.mpl.rcParams["axes.labelsize"] = fs

        self.mpl.rcParams["legend.fancybox"] = True
        self.mpl.rcParams["legend.framealpha"] = 0.7
        self.mpl.rcParams["legend.facecolor"] = "silver"
        self.mpl.rcParams["legend.frameon"] = True

        self.mpl.rcParams["lines.linewidth"] = 5

        return self

    def plotSetup(plot):

        plt.setp(plot.axes.xaxis.get_majorticklabels(), rotation=0)
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        plot.axes.xaxis.set_major_formatter(formatter)

        plt.grid(b=True)

        return plot


class visualizer:
    def __init__(self, data):

        self.data = data

    def viewOrigVar(
        self,
        varName,
        cmap="Spectral",
        vmin=-1,
        vmax=1,
        elv="90",
        azm="-",
        save=False,
        plotID=None,
        figPath=None,
        namePrefix=None,
        show=False,
        minTime=None,
        maxTime=None,
    ):

        if plotID == "rad_wind_speed_panel":

            tmpData = self.data
            self.plotDataAZM(
                dataNon90=tmpData,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                plotID=plotID,
                figPath=figPath,
                save=save,
                show=show,
                minTime=minTime,
                maxTime=maxTime,
            )

        else:
            tmpData = Filtering(self.data).get_vertical_obs_comp(varName)

            if namePrefix:
                strName = "{}_{}".format(
                    namePrefix, tmpData.attrs["standard_name"]
                )

            else:
                strName = tmpData.attrs["standard_name"]

            self.plotData(
                tmpData=tmpData,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                elv=elv,
                azm=azm,
                save=save,
                plotID=plotID,
                strName=strName,
                figPath=figPath,
                show=show,
                minTime=minTime,
                maxTime=maxTime,
            )

    def viewRetVar(
        self,
        varName,
        cmap="Spectral",
        vmin=-1,
        vmax=1,
        elv="90",
        azm="-",
        save=False,
        plotID=None,
        figPath=None,
        namePrefix=None,
        show=False,
        minTime=None,
        maxTime=None,
    ):

        tmpData = self.data[varName]

        strName = tmpData.attrs["standard_name"]

        self.plotData(
            tmpData=tmpData,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            elv=elv,
            azm=azm,
            save=save,
            plotID=plotID,
            strName=strName,
            figPath=figPath,
            show=show,
            minTime=minTime,
            maxTime=maxTime,
        )

    def plotData(
        self,
        tmpData,
        cmap="Spectral",
        vmin=-1,
        vmax=1,
        elv="90",
        azm="-",
        save=False,
        plotID=None,
        figPath=None,
        strName=None,
        show=False,
        minTime=None,
        maxTime=None,
    ):

        selDay = pd.to_datetime(tmpData.time[0].values)

        if maxTime is not None:
            maxTime = pd.to_datetime(maxTime)

        else:
            maxTime = pd.to_datetime(selDay.strftime("%Y%m%d 23:59:59"))

        if minTime is not None:
            minTime = pd.to_datetime(minTime)

        else:
            minTime = pd.to_datetime(selDay.strftime("%Y%m%d 00:00:00"))

        tmpData = tmpData.sel(time=slice(minTime, maxTime))

        if strName:
            tmpData.attrs["standard_name"] = strName

        plt.figure(figsize=(18, 8))
        plot = tmpData.plot(x="time", cmap=cmap, vmin=vmin, vmax=vmax)
        plot = plotSettings.plotSetup(plot)

        plt.grid(b=True)
        plt.ylim(0, 12e3)
        plt.xlim(minTime, maxTime)
        plt.title(f"elv: {elv}, azm: {azm}")

        if plotID == "hor_wind_dir":
            plot.colorbar.set_ticks(np.linspace(0, 360, 9))

        if save:
            fileName = "{}_{}.png".format(selDay.strftime("%Y%m%d"), plotID)
            outputFileName = os.path.join(figPath, fileName)
            print(outputFileName)
            plt.savefig(outputFileName, bbox_inches="tight")

        if show:
            plt.show()

        plt.close()

    def plotDataAZM(
        self,
        dataNon90,
        cmap="Spectral",
        vmin=-1,
        vmax=1,
        figPath=None,
        save=False,
        plotID=None,
        show=False,
        minTime=None,
        maxTime=None,
    ):

        elv = dataNon90.elv.values[0]
        fig, axes = plt.subplots(5, 1, sharex=True, figsize=(18, 25))

        selDay = pd.to_datetime(dataNon90.time[0].values)

        if maxTime is not None:
            maxTime = pd.to_datetime(maxTime)

        else:
            maxTime = pd.to_datetime(selDay.strftime("%Y%m%d 23:59:59"))

        if minTime is not None:
            minTime = pd.to_datetime(minTime)

        else:
            minTime = pd.to_datetime(selDay.strftime("%Y%m%d 00:00:00"))

        for axN, i in enumerate(dataNon90.azm.values):

            tmpData = dataNon90.sel(azm=i)

            tmpData = tmpData.sel(time=slice(minTime, maxTime))

            plot = tmpData.plot(
                x="time", cmap=cmap, vmin=vmin, vmax=vmax, ax=axes[axN]
            )

            plot = plotSettings.plotSetup(plot)

            axes[axN].grid(b=True)
            axes[axN].set_ylim(0, 12e3)
            axes[axN].set_xlim(minTime, maxTime)
            axes[axN].set_title(f"elv: {elv}, azm: {i}")

        if save:
            fileName = "{}_{}.png".format(selDay.strftime("%Y%m%d"), plotID)
            outputFileName = os.path.join(figPath, fileName)
            print(outputFileName)
            plt.savefig(outputFileName, bbox_inches="tight")

        if show:
            plt.show()

        plt.close()
