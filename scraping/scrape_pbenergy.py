#%%
import os
import re
from email.utils import parsedate_to_datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

OUTFILENAME = "pbenergy.csv"
URL_ENERGY = "https://www.westfalenwind.de/ueber-uns/unsere-windparks/energie-displays/"
URL_WEATHER = "https://wetter.upb.de/handy.html"
HEADERS_ENERGY = {
    # 'User-Agent': 'My User Agent 1.0',
}
HEADERS_WEATHER = {}

def get_response(url, headers):
    response = requests.get(url, headers=headers)
    return response

def make_soup(response):
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

def parse_energy_data(soup, response):
    timestamp = parsedate_to_datetime(response.headers.get("Date"))
    values = []
    print(f"# Daten vom: {timestamp}")
    displays = soup.find_all("div", class_="energiedisplay-heading")
    for display in displays:
        place = display.text
        print(f"## {place}")
        rows = display.parent.find_all("div", class_="energiedisplay-row")
        for row in rows:
            label = " ".join(row.find(class_="label").text.strip().split())
            value = float(row.find(class_="value").text.replace(",", ".").strip())
            unit = row.find(class_="unit").text.strip()
            print(f"### {label}")
            print(f"{value} {unit}")
            value = {
                "timestamp": timestamp,
                "place": place,
                "label": label,
                "value": value,
                "unit": unit,
            }
            values.append(value)
    return values

def parse_weather_data(soup, response):
    text = soup.text
    timestamp = re.findall(r"\d\d\.\d\d\.\d\d, \d\d:\d\d", text)[0]
    # Pressure
    re_pressure = re.findall(r"(Luftdruck): (.*) (hPa.*)", text)[0]
    pressure = float(re_pressure[1])
    pressure_unit = re_pressure[2]
    # Temperature
    re_temp = re.findall(r"Temp: (.*) (°C)", text)[0]
    temp = float(re_temp[0])
    temp_unit = re_temp[1]
    # Wind
    re_wind = re.findall(r"Windst.*: (.*), (.*) (.*) (km/h)", text)[0]
    wind_level = int(re_wind[0])
    wind_level_name = re_wind[1]
    wind_speed = float(re_wind[2])
    wind_speed_unit = re_wind[3]
    re_wind_direction = re.findall(r"Windrichtung: (.*), (.*°)", text)[0]
    wind_direction = re_wind_direction[0]
    wind_direction_angle = re_wind_direction[1]
    data = {
        "weather_timestamp": timestamp,
        "barometric_pressure": pressure,
        "barometric_pressure_unit": pressure_unit,
        "temperature": temp,
        "temperature_unit": temp_unit,
        "wind_speed": wind_speed,
        "wind_speed_unit": wind_speed_unit,
        "wind_level": wind_level,
        "wind_level_name": wind_level_name,
        "wind_direction": wind_direction,
        "wind_direction_angle": wind_direction_angle,
    }
    return data

def create_dataframe(values_energy, values_weather):
    df_energy = pd.DataFrame(values_energy)
    df_weather = pd.DataFrame([values_weather])
    return df_energy.merge(df_weather, how="cross")

def write_csv(outfilename, df):
    if os.path.exists(outfilename):
        df_old = pd.read_csv(outfilename)
        df_new = df_old.append(df)
    else:
        df_new = df
    df_new.to_csv(outfilename, index=False)

def main():
    response_energy = get_response(URL_ENERGY, HEADERS_ENERGY)
    soup_energy = make_soup(response_energy)
    values_energy = parse_energy_data(soup_energy, response_energy)
    response_weather = get_response(URL_WEATHER, HEADERS_WEATHER)
    soup_weather = make_soup(response_weather)
    values_weather = parse_weather_data(soup_weather, response_weather)
    df = create_dataframe(values_energy, values_weather)
    write_csv(OUTFILENAME, df)
    return values_energy, values_weather, df

if __name__ == "__main__":
    x, y, df = main()
