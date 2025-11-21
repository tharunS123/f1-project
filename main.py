from src.f1_data import get_race_telemetry, load_race_session
from src.animation import create_animation
import sys
import matplotlib.pyplot as plt

def main(year=None, round_number=None, output_file="output_animation.mp4", playback_speed=1):

  session = load_race_session(year, round_number)
  print(f"Loaded session: {session.event['EventName']} - {session.event['RoundNumber']}")

  # Get the drivers who participated in the race

  race_telemetry = get_race_telemetry(session)

  # TODO: Remove after testing

  # Trim to 500 frames for testing

  race_telemetry = race_telemetry[:100]

  # Get example lap for track layout

  example_lap = session.laps.pick_fastest().get_telemetry()

  drivers = session.drivers

  driver_codes = {
    num: session.get_driver(num)["Abbreviation"]
    for num in drivers
  } 

  still_frame = False

  if "--generate-track" in sys.argv:
    still_frame = True

  create_animation(race_telemetry, example_lap, driver_codes, output_file, playback_speed, still_frame=still_frame)

if __name__ == "__main__":

  # Get the year and round number from user input

  year = 2024

  round_number = 22

  playback_speed = 10

  output_file="output_animation.mp4"

  main(year, round_number, output_file, playback_speed)