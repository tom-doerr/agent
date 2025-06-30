#!/usr/bin/env python3

import datetime
import subprocess
import time
from pathlib import Path
import os

import dspy

lm = dspy.configure(lm=dspy.LM('deepseek/deepseek-reasoner', max_tokens=20_000))

refiner = dspy.Predict('artifact, constraints, critique, context -> refined_artifact',
                       instructions="Refine the artifact based on the critique.")
critic = dspy.Predict('artifact, constraints, context -> critique',
                      instructions="Critique the artifact based on the constraints and common sense.")
is_finished_checker = dspy.Predict('history -> is_finished: bool, reasoning')

CONSTRAINTS_FILE = Path('constraints.md')
ARTIFACT_FILE = Path('artifact.md')

# Load location from config or use default
LOCATION = "Mering"
if Path('nlco_config.toml').exists():
    try:
        import toml
        config = toml.load('nlco_config.toml')
        LOCATION = config.get('weather', {}).get('location', {}).get('city', LOCATION)
    except:
        pass


def create_context_string() -> str:
    mem = subprocess.run(['free', '-h'], capture_output=True, text=True, check=True).stdout
    
    # Simple weather using curl
    try:
        # Get current + 2 day forecast in compact format
        weather_raw = subprocess.run(['curl', '-s', f'wttr.in/{LOCATION}?format=j1'], 
                                   capture_output=True, text=True, timeout=3).stdout
        # Parse just the essentials from JSON
        import json
        w = json.loads(weather_raw)
        current = w['current_condition'][0]
        weather = (f"{LOCATION}: {current['weatherDesc'][0]['value']} {current['temp_C']}°C "
                  f"feels:{current['FeelsLikeC']}°C humidity:{current['humidity']}% "
                  f"wind:{current['windspeedKmph']}km/h")
        # Add tomorrow's forecast
        tomorrow = w['weather'][1]
        weather += f"\n    Tomorrow: {tomorrow['hourly'][4]['weatherDesc'][0]['value']} {tomorrow['maxtempC']}°/{tomorrow['mintempC']}°C"
    except:
        weather = f"{LOCATION}: unavailable"
    
    return (
        f"Datetime: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"Weather: {weather}\n"
        f"'free -h':\n{mem}\n"
    )


def iteration_loop():
    history = []
    for i in range(10):
        print(f"Iteration {i + 1} {'=' * 50}")

        artifact = ARTIFACT_FILE.read_text().strip()
        constraints = CONSTRAINTS_FILE.read_text().strip()
        context = create_context_string()

        critique = critic(artifact=artifact, constraints=constraints, context=context).critique
        print(f"Critique:\n{critique}\n")

        refined = refiner(artifact=artifact, constraints=constraints,
                          critique=critique, context=context).refined_artifact
        print('-' * 80)
        print(f"Artifact:\n{refined}")

        ARTIFACT_FILE.write_text(refined)
        history += [f'Iteration {i + 1}', artifact, constraints, critique, refined]

        # if is_finished_checker(history=history).is_finished:
        if False:
            finished_check_result = is_finished_checker(history=history)
            print(f"Finished check: {finished_check_result.is_finished} | Reasoning: {finished_check_result.reasoning}\n")
            stop_iterating = finished_check_result.is_finished
        # if finished_check_result.is_finished:
        else:
            stop_iterating = False
        if stop_iterating:
            # print("Artifact finished " + '=' * 50)
            print("Artifact finished after iteration", i + 1, "|" * 50)
            break


def main():
    last_mtime = None
    while True:
        mtime = CONSTRAINTS_FILE.stat().st_mtime
        if mtime != last_mtime:
            print(f"Constraints changed at {datetime.datetime.fromtimestamp(mtime)}. Running iterations…")
            last_mtime = mtime
            iteration_loop()
        time.sleep(1)            # don’t spin-lock the CPU


if __name__ == "__main__":
    main()

