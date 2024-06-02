

def calculate_hr_zones(max_heart_rate):
    #set max at 2 so that any HRs above .97 are considered anaerobic
    breakpoints = {'Endurance':0,
                   'Moderate':0.59,
                   'Tempo':0.78,
                   'Threshold':0.87,
                   'Anaerobic':0.97}
    zones = {name: pct * max_heart_rate for name, pct in breakpoints.items()}
    return zones

