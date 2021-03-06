# NHSEnglandCases.py

from pandas import read_csv
from numpy import datetime64, timedelta64
import requests
from io import StringIO



class NHSEnglandCases:
    '''
    Object that handles retrieving COVID-19 cases in england
    as reported by NHS England at https://coronavirus.data.gov.uk/
    '''
    def __init__(
        self,
        URL=(r'https://coronavirus.data.gov.uk'
        r'/downloads/csv/coronavirus-cases_latest.csv'),
        date_cols=['Specimen date'],
        filter_data=True
    ):
        self.csv = self._download_csv(URL)
        self._date_cols = date_cols
        self.filter_data = filter_data

    def _download_csv(self, URL):
        # Download using URL
        csv = requests.get(URL, stream=True).content

        # Decode from string
        csv = csv.decode('utf-8')

        return csv

    @property
    def dataframe(self):
        '''Returns downloaded csv as a pandas dataframe'''
        df = read_csv(
            StringIO(self.csv),
            parse_dates=self._date_cols
        )

        # Re-order by date
        df.sort_values(self._date_cols, inplace=True)

        if self.filter_data:
            # Filter last 5 days out of dataset
            filter_date = datetime64('today') - timedelta64(5, 'D')
            df = df[
                df[self._date_cols[0]] <= filter_date
            ]
            # Filter out cases less than 10
            df = df[df['Cumulative lab-confirmed cases'] > 10]

        # Rename some columns
        cols = {
            'Specimen date': 'DateVal',
            'Daily lab-confirmed cases': 'EngConfSpecimens',
            'Cumulative lab-confirmed cases': 'CumEngConfSpec'
        }
        df.rename(columns=cols, inplace=True)
        return df

    def _filter_area_type(self, _type):
        df = self.dataframe
        return df[df['Area type'] == _type]

    def national(self, nation=None):
        df = self._filter_area_type('Nation')

        if nation is not None:
            df = df[df['Area name'] == nation]

        return df

    def regional(self, region=None):
        df = self._filter_area_type('Region')

        if region is not None:
            df = df[df['Area name'] == region]
        
        return df

    def utla(self, authority=None):
        df = self._filter_area_type('Upper tier local authority')

        if authority is not None:
            df = df[df['Area name'] == authority]
        
        return df
