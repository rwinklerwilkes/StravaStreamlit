import csv
import fitparse
import gzip
import os
from gpxcsv import gpxtolist
from tqdm import tqdm
from dateutil import parser
import pytz
import datetime

def standardize_time(timestamp):
    #expected format:
    #2012-07-30 17:54:08+00:00
    if timestamp is None:
        return timestamp
    if isinstance(timestamp, datetime.datetime):
        parsed_date = timestamp
        est_date = parsed_date
    else:
        parsed_date = parser.parse(timestamp)
        if not parsed_date.tzinfo:
            parsed_date = parsed_date.replace(tzinfo=pytz.utc)
        est = pytz.timezone('US/Eastern')
        est_date = parsed_date.astimezone(est)
    output = est_date.strftime('%Y-%m-%d %H:%M:%S')
    return output

def get_expected_format():
    return ('time','distance','lat','lon','elev','power','cadence','heart_rate')

def parse_gzip(filename):
    with gzip.open(f'../data/raw/{filename}', 'rb') as f:
        file_content = f.read()
    return file_content

def write_output(filename, output, track_name):
    output_filename = filename.split('.')[0]
    with open(f'../data/processed/{output_filename}.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(output)

    with open(f'../data/metadata/processed_files.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([filename, output_filename, track_name])

def parse_gpx(filename):
    gpx_list = gpxtolist(f'../data/raw/{filename}')
    track_name = None
    for point in gpx_list:
        if not track_name:
            track_name = point.get('name')
        assert get_expected_format() == ('time','distance','lat','lon','elev','power','cadence','heart_rate')
        output.append([standardize_time(point.get('time')),
                       point.get('distance'),
                       point.get('lat'),
                       point.get('lon'),
                       point.get('ele'),
                       point.get('power'),
                       point.get('cad'),
                       point.get('heart_rate')])
    write_output(filename, output, track_name)

def parse_fit(filename, content=None):
    fitfile = fitparse.FitFile(f'../data/raw/{filename}')
    output = []
    track_name = filename.split('.')[0]
    for record in fitfile.get_messages("record"):
        row_output = {}
        for data in record:
            use = False
            if data.name in ['position_lat', 'position_long']:
                value = data.value
                if value:
                    # Answer here https://gis.stackexchange.com/questions/371656/garmin-fit-coordinate-system
                    # Answer why 11930465 here: https://gis.stackexchange.com/questions/122186/convert-garmin-or-iphone-weird-gps-coordinates
                    value /= 11930465
                    use = True
            elif data.name == 'timestamp':
                value = standardize_time(data.value)
                use = True
            elif data.name in ['distance','power', 'cadence', 'heart_rate']:
                value = data.value
                use = True
            elif data.name == 'altitude':
                if data.value:
                    if data.units and data.units == 'm':
                        value = data.value * 3.28084
                    else:
                        value = data.value
                    use = True
            if use:
                row_output[data.name] = value
        assert get_expected_format() == ('time','distance','lat','lon','elev','power','cadence','heart_rate')
        final_row_output = [row_output['timestamp'],
                            row_output.get('distance', None),
                            row_output.get('position_lat', None),
                            row_output.get('position_long', None),
                            row_output.get('altitude', None),
                            row_output.get('power', None),
                            row_output.get('cadence', None),
                            row_output.get('heart_rate', None)]
        output.append(final_row_output)
    write_output(filename, output, track_name)

def parse_tcx(filename):
    data = tcx_reader.read(f'../data/raw/{filename}', only_gps=False)
    track_name = filename.split('.')[0]
    output = []
    for trackpoint in data.trackpoints:
        assert get_expected_format() == ('time','distance','lat','lon','elev','power','cadence','heart_rate')
        tpd = trackpoint.to_dict()
        final_row_output = [standardize_time(tpd.get('time')),
                            tpd.get('distance'),
                            tpd.get('latitude'),
                            tpd.get('longitude'),
                            tpd.get('elevation'),
                            tpd.get('Watts'),
                            tpd.get('cadence'),
                            tpd.get('hr_value')]
        output.append(final_row_output)
    write_output(filename, output, track_name)

def unzip_file(filename):
    import shutil
    #filename with .gz
    original_filename = filename
    #filename without .gz
    new_filename = filename[:-3]
    with gzip.open(f'../data/raw/{original_filename}', 'rb') as f_in:
        with open(f'../data/raw/{new_filename}', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return new_filename

def parse_file(filename):
    if filename[-3:] == 'gpx':
        parse_gpx(filename)
        return True, filename
    elif filename[-3:] == 'fit':
        parse_fit(filename)
        return True, filename
    elif filename[-3:] == 'tcx':
        parse_tcx(filename)
        return True, filename
    elif filename[-2:] == 'gz':
        filename = unzip_file(filename)
        return parse_file(filename)
    else:
        return False, filename

def parse_all_files(directory):
    all_files = os.listdir(directory)
    failed = []
    for file in tqdm(all_files):
        success, name = parse_file(file)
        if not success:
            failed.append(name)
    return failed

parse_gpx('Lunch_Ride.gpx')

filename = '1138501591.fit.gz'
parse_fit(filename)

filename = '9029218105.tcx'

from tcxreader.tcxreader import TCXReader, TCXTrackPoint
tcx_reader = TCXReader()

#This is just an XML file - I may be able to do the parsing on my own.
#TCXReader assumes all cadence values will be ints
data = tcx_reader.read(f'data/raw/example_issue.txt')

missing_files = parse_all_files('data/raw')