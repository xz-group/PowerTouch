import numpy as np
import pandas as pd


class BasicTouchEvent(object):
    def __init__(self, record):
        self.record = record.reset_index()

    @property
    def x_list(self):
        values = self.record['X'].to_numpy(dtype='float', na_value=np.nan)
        values = values[0:-1]
        return values

    @property
    def y_list(self):
        values = self.record['Y'].to_numpy(dtype='float', na_value=np.nan)
        values = values[0:-1]
        return values

    @property
    def diameter_list(self):
        values = self.record['Diameter'].to_numpy(dtype='float', na_value=np.nan)
        values = values[0:-1]
        return values

    @property
    def pressure_list(self):
        values = self.record['Pressure'].to_numpy(dtype='float', na_value=np.nan)
        values = values[0:-1]
        return values

    @property
    def duration(self):
        return self.time_list[-1] - self.time_list[0]

    @property
    def interval_list(self):
        return np.diff(self.time_list)

    @property
    def time_list(self):
        return self.record['Time'].to_numpy(dtype='float', na_value=np.nan)

    @property
    def start_time(self):
        return self.time_list[0]

    @property
    def end_time(self):
        return self.time_list[-1]

    @property
    def num_points(self):
        return len(self.record) - 1

    @property
    def if_missing_data(self):
        return self.record.isnull().values.any()

    @property
    def tracking_id(self):
        return self.record['Tracking'].tolist()[0]

    @property
    def slot_index(self):
        return self.record['Slot'].tolist()[0]

    @staticmethod
    def nanmean(array):
        nan_location = np.argwhere(np.isnan(array))
        if len(nan_location) == len(array):
            return np.nan
        else:
            return np.nanmean(array)

    @staticmethod
    def nanmax(array):
        nan_location = np.argwhere(np.isnan(array))
        if len(nan_location) == len(array):
            return np.nan
        else:
            return np.nanmax(array)

    @staticmethod
    def nanmin(array):
        nan_location = np.argwhere(np.isnan(array))
        if len(nan_location) == len(array):
            return np.nan
        else:
            return np.nanmin(array)

    @staticmethod
    def nanstd(array):
        nan_location = np.argwhere(np.isnan(array))
        if len(nan_location) == len(array):
            return np.nan
        else:
            return np.nanstd(array)


class Click(BasicTouchEvent):
    @property
    def x(self):
        value = self.record['X'].tolist()[0]
        return value

    @property
    def y(self):
        value = self.record['Y'].tolist()[0]
        return value

    @property
    def type(self):
        return 'Click'

    @property
    def information_dict(self):
        info = {}
        info['StartTime'] = self.start_time
        info['EndTime'] = self.end_time
        info['Slot'] = self.slot_index
        info['Tracking'] = self.tracking_id
        info['Type'] = self.type
        info['X'] = self.x
        info['Y'] = self.y
        info['Duration'] = self.duration
        info['NumPoints'] = self.num_points
        # info['IntervalMean'] = np.mean(self.interval_list)
        # info['IntervalMin'] = np.min(self.interval_list)
        # info['IntervalMax'] = np.max(self.interval_list)
        # info['IntervalStd'] = np.std(self.interval_list)
        # info['DiameterMean'] = self.nanmean(self.diameter_list)
        # info['DiameterMin'] = self.nanmin(self.diameter_list)
        # info['DiameterMax'] = self.nanmax(self.diameter_list)
        # info['DiameterStd'] = self.nanstd(self.diameter_list)
        # info['PressureMean'] = self.nanmean(self.pressure_list)
        # info['PressureMin'] = self.nanmin(self.pressure_list)
        # info['PressureMax'] = self.nanmax(self.pressure_list)
        # info['PressureStd'] = self.nanstd(self.pressure_list)
        info['IfMissingData'] = self.if_missing_data
        return info


class Swipe(BasicTouchEvent):
    @property
    def type(self):
        return 'Swipe'

    @property
    def x_mean(self):
        return np.nanmean(self.x_list)

    @property
    def y_mean(self):
        return np.nanmean(self.y_list)

    @property
    def x_std_var(self):
        return np.nanstd(self.x_list)

    @property
    def y_std_var(self):
        return np.nanstd(self.y_list)

    @property
    def x_start(self):
        try:
            return self.x_list[0]
        except IndexError:
            print(self.slot_index, self.tracking_id, self.x_list)

    @property
    def y_start(self):
        return self.y_list[0]

    @property
    def x_end(self):
        return self.x_list[-1]

    @property
    def y_end(self):
        return self.y_list[-1]

    @property
    def x_direction(self):
        if self.x_start > self.x_end:
            return 'left'
        elif self.x_start < self.x_end:
            return 'right'
        else:
            return 'center'

    @property
    def y_direction(self):
        if self.y_start > self.y_end:
            return 'down'
        elif self.y_start < self.y_end:
            return 'up'
        else:
            return 'center'

    @property
    def information_dict(self):
        info = {}
        info['StartTime'] = self.start_time
        info['EndTime'] = self.end_time
        info['Slot'] = self.slot_index
        info['Tracking'] = self.tracking_id
        info['Type'] = self.type
        info['XStart'] = self.x_start
        info['YStart'] = self.y_start
        info['XEnd'] = self.x_end
        info['YEnd'] = self.y_end
        info['XMean'] = self.x_mean
        info['YMean'] = self.y_mean
        info['XStd'] = self.x_std_var
        info['YStd'] = self.y_std_var
        info['Duration'] = self.duration
        info['NumPoints'] = self.num_points
        info['IfMissingData'] = self.if_missing_data
        # info['IntervalMean'] = np.mean(self.interval_list)
        # info['IntervalMin'] = np.min(self.interval_list)
        # info['IntervalMax'] = np.max(self.interval_list)
        # info['IntervalStd'] = np.std(self.interval_list)
        # info['DiameterMean'] = self.nanmean(self.diameter_list)
        # info['DiameterMin'] = self.nanmin(self.diameter_list)
        # info['DiameterMax'] = self.nanmax(self.diameter_list)
        # info['DiameterStd'] = self.nanstd(self.diameter_list)
        # info['PressureMean'] = self.nanmean(self.pressure_list)
        # info['PressureMin'] = self.nanmin(self.pressure_list)
        # info['PressureMax'] = self.nanmax(self.pressure_list)
        # info['PressureStd'] = self.nanstd(self.pressure_list)
        info['XDirection'] = self.x_direction
        info['YDirection'] = self.y_direction
        return info


class TouchEvent(object):
    def __init__(self, record):
        self.record = record
        if self.event_type == 'Click':
            self.event = Click(record=self.record)
        else:
            self.event = Swipe(record=self.record)
        pass

    @property
    def event_type(self):
        x = self.record['X'].to_numpy(dtype='float', na_value=np.nan)
        x = list(set(x[0:-1]))
        y = self.record['Y'].to_numpy(dtype='float', na_value=np.nan)
        y = list(set(y[0:-1]))
        if len(x) == len(y) == 1:
            event = 'Click'
        else:
            event = 'Swipe'
        return event


class Slot(object):
    def __init__(self, slot_index):
        self.slot_index = slot_index
        self.tracking_id = -1
        self._touch_x = 0
        self._touch_y = 0
        self._touch_diameter = 0
        self._touch_pressure = 0
        self._timestamp = np.nan
        self.record = pd.DataFrame(
            columns=['Time', 'Slot', 'ID', 'Tracking', 'Event', 'X', 'Y', 'Diameter', 'Pressure'])
        self.record_dropped = pd.DataFrame(
            columns=['Time', 'Slot', 'ID', 'Tracking', 'Event', 'X', 'Y', 'Diameter', 'Pressure'])
        self.record_full = pd.DataFrame(
            columns=['Time', 'Slot', 'ID', 'Tracking', 'Event', 'X', 'Y', 'Diameter', 'Pressure'])
        self.touch_events = {}
        self.statistic_click = None
        self.statistic_swipe = None

    def compileSlotStatistics(self):
        unique_tracking_ids = self.record['Tracking'].tolist()
        unique_tracking_ids = list(set(unique_tracking_ids))
        unique_tracking_ids.sort()
        self.statistic_click = pd.DataFrame(columns=['StartTime',
                                                     'EndTime',
                                                     'Slot',
                                                     'Tracking',
                                                     'Type',
                                                     'X',
                                                     'Y',
                                                     'Duration',
                                                     'NumPoints',
                                                     'IfMissingData'
                                                     # 'IntervalMean',
                                                     # 'IntervalMin',
                                                     # 'IntervalMax',
                                                     # 'IntervalStd',
                                                     # 'DiameterMean',
                                                     # 'DiameterMin',
                                                     # 'DiameterMax',
                                                     # 'DiameterStd',
                                                     # 'PressureMean',
                                                     # 'PressureMin',
                                                     # 'PressureMax',
                                                     # 'PressureStd'
                                                     ])
        self.statistic_swipe = pd.DataFrame(columns=['StartTime',
                                                     'EndTime',
                                                     'Slot',
                                                     'Tracking',
                                                     'Type',
                                                     'XDirection',
                                                     'XStart',
                                                     'XEnd',
                                                     'YDirection',
                                                     'YStart',
                                                     'YEnd',
                                                     'XMean',
                                                     'YMean',
                                                     'XStd',
                                                     'YStd',
                                                     'Duration',
                                                     'NumPoints',
                                                     'IfMissingData'
                                                     # 'IntervalMean',
                                                     # 'IntervalMin',
                                                     # 'IntervalMax',
                                                     # 'IntervalStd',
                                                     # 'DiameterMean',
                                                     # 'DiameterMin',
                                                     # 'DiameterMax',
                                                     # 'DiameterStd',
                                                     # 'PressureMean',
                                                     # 'PressureMin',
                                                     # 'PressureMax'
                                                     ])
        for id in unique_tracking_ids:
            touch = TouchEvent(record=self.record[self.record.Tracking == id])
            self.touch_events[id] = touch
            info = touch.event.information_dict
            if touch.event_type == 'Click':
                self.statistic_click = self.statistic_click.append(info, ignore_index=True)
            else:
                self.statistic_swipe = self.statistic_swipe.append(info, ignore_index=True)

    def addSlotRecordDataframe(self, dataframe):
        self.record_full = self.record_full.append(dataframe, ignore_index=True)
        self.record_full.sort_values(by='Time', inplace=True)

    def parseSlotRecordDataframe(self):
        self.record_full.reset_index(inplace=True)
        self.record = self.record_full.copy()
        tracking_id_with_nan = [self.record.iloc[index]['Tracking'] for index, row in
                                self.record.iterrows() if row[['X', 'Y']].isnull().any()]
        tracking_id_with_nan = list(set(tracking_id_with_nan))
        for id_nan in tracking_id_with_nan:
            self.record_dropped = self.record_dropped.append(self.record[self.record.Tracking == id_nan])
            self.record.drop(self.record[self.record.Tracking == id_nan].index, inplace=True)
