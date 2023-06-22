from flask import Flask
from flask import request
from inspect import getsourcefile
from os.path import abspath, dirname
from os import path
import multiprocessing
import time
import warnings
import shutil
import re
import pandas as pd
import json
import numpy as np
from PowerTouch.TouchMonitorFlutter.Server import app


# todo: swipes
# todo: battery
# todo: statistics
# todo: plotting touch data
# todo: connection with main program


class TouchMonitor:

    def setupPhoneCommunicationServer(self, file_save_path=None, file_name_index=0):
        if file_save_path is None:  # if no file_save_path is given, use the current directory
            self.file_save_path = dirname(abspath(getsourcefile(lambda: 0)))
        else:
            self.file_save_path = file_save_path

        self.file_name_index = file_name_index

        self.flutter_server = multiprocessing.Process(target=self._RunServer)

    @staticmethod
    def _RunServer():
        app.run(host="0.0.0.0", port="18888")

    def initiatePhoneCommunication(self):
        self.flutter_server.start()
        print('Server is running:')

    def terminatePhoneCommunication(self):
        print("Shutting server down now..")
        self.flutter_server.terminate()
        print("Server shut down.")

    def checkPhoneConnection(self):
        pass

    def readPhoneBattery(self, verbose=False):
        pass

    def copyEventFile(self, event_file_path='./touched.log', copy_to='./'):
        shutil.copy2(event_file_path, ''.join([copy_to, 'touched', '.log']))

    def parseEventFile(self, event_file_path='./touched.log', event_file_copy_to=None, verbose=True, save_raw_csv=None,
                       save_processed_csv=None):
        if event_file_copy_to is not None:
            shutil.copy2(event_file_path, event_file_copy_to)

        # if exist touched.log, parse it
        if path.exists(event_file_path):
            # read event files
            touches = []
            with open(event_file_path) as _f_read:
                for line in _f_read.readlines():
                    touches.append(json.loads(line))

            if len(touches) == 0:
                return 0  # no touches detected

            # convert to pandas dataframe
            df_processed = pd.DataFrame(touches)

            if save_processed_csv is not None:
                # compared with record, this file is used to debug the parser
                df_processed.to_csv(''.join([save_processed_csv, 'events', '.csv']), index=False)
        else:
            warnings.warn('No event file found.')
            return 0  # no file detected

    def writeMultiTouchRecord2CSV(self, save_path='./'):
        filename = 'events'
        self.records.to_csv(''.join([save_path, filename, '.csv']), index=False)

    def readCSV2MultiTouchRecord(self, read_path='./', filename='events'):
        self.records = pd.read_csv(''.join([read_path, filename, '.csv']))

        # reset parameters
        self.statistic_swipe = pd.DataFrame()
        self.statistic_click = pd.DataFrame()
        self.statistic_touch_count = pd.DataFrame()
        self.timestamps = []

        self.timestamps = list(set(self.records['Time']))
        self.timestamps.sort()
        pass

    def compileMultiTouchStatistics(self):
        dropped = 0
        total = 0
        processed = 0
        processed_new = 0

        # count the click number
        self.statistic_touch_count = pd.DataFrame(columns=['Type', 'Number'])
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'Click',
                                                                        'Number': len(self.statistic_click)
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'Swipe',
                                                                        'Number': len(self.statistic_swipe)
                                                                        }, ignore_index=True)
        total_touches = len(self.statistic_swipe) + len(self.statistic_click)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'TotalTouches',
                                                                        'Number': total_touches
                                                                        }, ignore_index=True)
        if total_touches == 0:
            click_proportion = 0
            swipe_proportion = 0
        else:
            click_proportion = len(self.statistic_click) / total_touches
            swipe_proportion = len(self.statistic_swipe) / total_touches
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'ClickProportion',
                                                                        'Number': click_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeProportion',
                                                                        'Number': swipe_proportion
                                                                        }, ignore_index=True)

        swipe_x_left = len(self.statistic_swipe[self.statistic_swipe.XDirection == 'left'])
        swipe_x_right = len(self.statistic_swipe[self.statistic_swipe.XDirection == 'right'])
        swipe_x_center = len(self.statistic_swipe[self.statistic_swipe.XDirection == 'center'])
        swipe_y_up = len(self.statistic_swipe[self.statistic_swipe.YDirection == 'up'])
        swipe_y_down = len(self.statistic_swipe[self.statistic_swipe.YDirection == 'down'])
        swipe_y_center = len(self.statistic_swipe[self.statistic_swipe.YDirection == 'center'])
        if len(self.statistic_swipe) == 0:
            swipe_x_left_proportion = 0
            swipe_x_right_proportion = 0
            swipe_x_center_proportion = 0
            swipe_y_up_proportion = 0
            swipe_y_down_proportion = 0
            swipe_y_center_proportion = 0
        else:
            swipe_x_left_proportion = swipe_x_left / len(self.statistic_swipe)
            swipe_x_right_proportion = swipe_x_right / len(self.statistic_swipe)
            swipe_x_center_proportion = swipe_x_center / len(self.statistic_swipe)
            swipe_y_up_proportion = swipe_y_up / len(self.statistic_swipe)
            swipe_y_down_proportion = swipe_y_down / len(self.statistic_swipe)
            swipe_y_center_proportion = swipe_y_center / len(self.statistic_swipe)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXLeft',
                                                                        'Number': swipe_x_left
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXRight',
                                                                        'Number': swipe_x_right
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXCenter',
                                                                        'Number': swipe_x_center
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXLeftProportion',
                                                                        'Number': swipe_x_left_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXRightProportion',
                                                                        'Number': swipe_x_right_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeXCenterProportion',
                                                                        'Number': swipe_x_center_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYUp',
                                                                        'Number': swipe_y_up
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYDown',
                                                                        'Number': swipe_y_down
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYCenter',
                                                                        'Number': swipe_y_center
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYUpProportion',
                                                                        'Number': swipe_y_up_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYDownProportion',
                                                                        'Number': swipe_y_down_proportion
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'SwipeYCenterProportion',
                                                                        'Number': swipe_y_center_proportion
                                                                        }, ignore_index=True)

        # count the events number
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'DroppedEvents',
                                                                        'Number': dropped
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'TotalEvents',
                                                                        'Number': total
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'ProcessedEvents',
                                                                        'Number': processed
                                                                        }, ignore_index=True)
        self.statistic_touch_count = self.statistic_touch_count.append({'Type': 'ProcessedEventsOnlyNew',
                                                                        'Number': processed_new
                                                                        }, ignore_index=True)

    def writeMultiTouchStatistics2CSV(self, save_path='./'):
        self.statistic_click.to_csv(''.join([save_path, 'click', '.csv']), index=False)
        self.statistic_swipe.to_csv(''.join([save_path, 'nonclick', '.csv']), index=False)
        self.statistic_touch_count.to_csv(''.join([save_path, 'eventNumber', '.csv']), index=False)

    def plotMultiTouch(self, time_delay=1, persistence=False, plot_circle=True, show_cross_mark=True):

        plt.ion()
        fig, axes = plt.subplots()
        # fig.set_figheight(10)
        # fig.set_figwidth(6.5)
        axes.set_xlim([0, 1080])
        axes.set_ylim([1920, 0])
        axes.set_aspect('equal')
        plt.tight_layout()
        touches = {}
        death_note = []
        axes.grid(color='darkgray', linestyle='--', linewidth=0.5)
        rows = np.linspace(0, 1920, 27)
        for i in range(len(rows)):
            axes.axhline(y=rows[i], color='tab:red', linewidth=0.5, linestyle='--')
            axes.text(1080, rows[i], str(i + 1), color='tab:red', va='center')
        plt.tight_layout()

        for time in self.timestamps:
            axes.set_title(time)

            # clear lifted touches
            if persistence is False:
                if len(death_note) != 0:
                    for deceased in death_note:
                        touches[deceased].clearTouch()
                        del touches[deceased]
                        death_note.remove(deceased)

            # plot slot touches
            for i in range(len(self.slots)):
                dataframe = self.slots[i].record.query('Time == @time')
                if dataframe.empty is True:
                    continue
                elif len(dataframe) == 1:
                    event = dataframe['Event'].values[0]
                    tracking_id = dataframe['Tracking'].values[0]
                    x = dataframe['X'].values[0]
                    y = dataframe['Y'].values[0]
                    diameter = dataframe['Diameter'].values[0]

                    if event == 'New':
                        touches[str(tracking_id)] = TouchEventPlotHandler(axes, slot_index=i,
                                                                          color_list=self._color_list)
                        touches[str(tracking_id)].plotNewTouch(timestamp=time, tracking_id=tracking_id, x=x, y=y,
                                                               diameter=diameter, plot_circle=plot_circle)
                    elif event == 'Move':
                        touches[str(tracking_id)].plotMoveTouch(timestamp=time, x=x, y=y, diameter=diameter,
                                                                plot_circle=plot_circle)
                    elif event == 'Lift':
                        if show_cross_mark is True:
                            touches[str(tracking_id)].plotLiftTouch(timestamp=time)
                        death_note.append(str(tracking_id))
                else:
                    raise ValueError("More than one row.")

            plt.draw()
            plt.pause(time_delay)


if __name__ == '__main__':
    monitor = TouchMonitor()
    # monitor.setupPhoneCommunicationServer(file_name_index=6)
    # monitor.initiatePhoneCommunication()
    # time.sleep(20)
    # monitor.terminatePhoneCommunication()
    monitor.parseEventFile(event_file_path='./touched.log', save_processed_csv='./')
    monitor.readCSV2MultiTouchRecord()
