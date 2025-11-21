import fastf1
import fastf1.plotting
import numpy as np
import json

# Enable local cache (adjust path if you prefer)
fastf1.Cache.enable_cache('.fastf1-cache')

FPS = 10
DT = 1 / FPS

def load_race_session(year, round_number):
  session = fastf1.get_session(year, round_number, 'R')
  session.load(telemetry=True)
  return session

def get_race_telemetry(session):
  drivers = session.drivers

  driver_codes = {
    num: session.get_driver(num)["Abbreviation"]
    for num in drivers
  } 

  driver_data = {}

  global_t_min = None
  global_t_max = None

  # 1. Get all of the drivers telemetry data

  for driver_no in drivers:

    driver_code = driver_codes[driver_no]

    laps = session.laps.pick_drivers(driver_no)
    driver_tel = laps.get_telemetry()

    if driver_tel.empty:
      continue

    t = driver_tel["SessionTime"].dt.total_seconds().to_numpy()
    x = driver_tel["X"].to_numpy()
    y = driver_tel["Y"].to_numpy()

    driver_data[driver_code] = {
      't': t,
      'x': x,
      'y': y
    }

    t_min = t.min()
    t_max = t.max()

    if global_t_min is None or t_min < global_t_min:
      global_t_min = t_min

    if global_t_max is None or t_max > global_t_max:
      global_t_max = t_max

    # TODO: Remove after testing


  # Create a Timeline

  timeline = np.arange(global_t_min, global_t_max, DT)

  # 2. Resample each driver's telemetry onto the common timeline

  resampled_data = {}

  for code, data in driver_data.items():

    t = data['t']
    x = data['x']
    y = data['y']

    x_resampled = np.interp(timeline, t, x)
    y_resampled = np.interp(timeline, t, y)

    resampled_data[code] = {
      't': timeline,
      'x': x_resampled,
      'y': y_resampled
    }

  # Build the structure to return

  frames = []

  for i, t in enumerate(timeline):
    frame_data = {}
    for code, data in resampled_data.items():
      frame_data[code] = {
        'x': data['x'][i],
        'y': data['y'][i]
      }
    frames.append({
      't': t,
      'drivers': frame_data
    })

  return frames