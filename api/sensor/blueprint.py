from flask import Blueprint, request, current_app, Response
import datetime
import pymongo

import json
import os

_dir = os.path.dirname(os.path.abspath(__file__))
api_sensor = Blueprint('api_sensor', __name__, template_folder="templates", url_prefix='/api')

"""
Database Structure
    RESERVED ID:
        - 0: The information json
        - 1: 10 Minutely Average for 24 hours
        - 2: Hourly Average for 48 hours
        - 3: 12 Hour Average (at midnight and midday) for 360 days
        - 4: Monthly Average (24 months)
        - 5: Annual Quarterly Average kept indefinitely
        
    For Sensors unless specifically requested all sensors gets a memory allocation of 256 Mb the oldest none compiled
    data is deleted to make more room.
"""


class BadJson(Exception):
    pass


class NeedJson(Exception):
    pass


def check_help(Json) -> bool:
    """
    A helper method for deciding if the user needs help

    :param Json: the request Json
    :return: true if the user needs help
    """

    try:
        if (Json["help"] == True):
            return True
        else:
            return False

    except KeyError:
        return False


def get_json(request) -> tuple[bool, json]:
    """
    Method for handling user request as json and as string

    :param request: the actual request object
    :return: bool and json back to the user
    """

    content_type = request.headers.get('Content-Type')

    # check what type of content type is it
    if (content_type == 'application/json'):
        try:
            regis_info = request.json
        except Exception:
            raise BadJson

    elif (content_type == 'text/plain'):
        try:
            regis_info = json.loads(request.data)
        except json.decoder.JSONDecodeError:
            raise BadJson
    else:
        raise NeedJson

    help = check_help(regis_info)

    return help, regis_info


@api_sensor.route('sensor/register', methods=['POST'])
def sensor_register():
    """
    Get sensors from path

    :return: sends back the sensor
    """
    # check what type of content type is it
    try:
        help, regis_info = get_json(request)
    except BadJson:
        return "Bad json structure (json format), set { \"help\" : 1 } to request help", 400
    except NeedJson:
        return "Please request registration using a Json format, set { \"help\" : true } to request help", 400

    # check if help is needed
    try:
        if (help == True):
            return """Typical Registration Format...
            {
                "name"            : # string insert name here
                "display_name     : # string name that is going to be displayed
                "desc"            : # string description of the sensors
                "compile_data"    : # bool does the data need to be compile every month etc
                "compile_freq"    : # how often is the average found? if undefined, every hour is clumped
            }
            """
    except KeyError:
        pass

    # get the sensor database
    db = current_app.config["DATABASE"].Sensor  # type: pymongo.MongoClient
    # check if it already exists
    if regis_info["name"] in db.list_collection_names():
        return f"name {regis_info['name']} is already taken, please choose a new name", 400

    # create new collection and set up documents
    newSensor = db[regis_info['name']]
    regis_info["_id"] = 0
    newSensor.insert_one(regis_info)

    return f"sucessfully registered {regis_info['name']} as a new sensor", 201


@api_sensor.route('sensor/<sensor_name>', defaults={'timeframe': None}, methods=['GET'])
@api_sensor.route('sensor/<sensor_name>/<timeframe>', methods=['GET'])
def get_sensor(sensor_name, timeframe):
    """
    Get sensors from path typically return values from the
    last 30 days

    :param sensor_name: name of the sensor
    :param timeframe: the timeframe of reading request
    :return: sends back the sensor
    """
    # check return for what timeframe
    try:
        help = get_json(request)
    except NeedJson:
        pass

    # get the sensor database
    db = current_app.config["DATABASE"].Sensor  # type: pymongo.MongoClient
    # add to the collection
    sensor = db[sensor_name]

    cur_date = datetime.datetime.today()
    end_date = cur_date - datetime.timedelta(days=30)

    output = {}
    counter = 0
    # iterate i n the result adding it to json
    for i in sensor.find({ "time": {
            "$gte": end_date,
            "$lte": cur_date
        }
    }):
        output[counter] = i
        counter += 1


    return Response(str(output), mimetype='application/json')


@api_sensor.route('sensor/<sensor_name>', methods=['POST'])
def post_sensor(sensor_name):
    """
    Add a sensor data

    :param sensor_name: name of the sensor
    :return: sends back the sensor
    """

    try:
        help, regis_info = get_json(request)
    except BadJson:
        return "Bad json structure (json format), set { \"help\" : 1 } to request help", 400
    except NeedJson:
        return "Please request registration using a Json format, set { \"help\" : true } to request help", 400

    # check if help is needed
    try:
        if help == True:
            return """Typical Registration Format...
            {
                "time" : # when the data point was taken
                "data" : # the data points
                "unit" : # the data point unit (if there is units)
            }
            """
    except KeyError:
        pass

    # get the sensor database
    db = current_app.config["DATABASE"].Sensor  # type: pymongo.MongoClient
    # check if exist
    if sensor_name not in db.list_collection_names():
        return f"name {sensor_name} does not exist, please either register a new sensor or try a different name", 400

    # check if time is already added
    try:
        regis_info["time"]
        print("time exist")
    except KeyError:
        print("adding time")
        time = datetime.datetime.now()
        regis_info["time"] = time

    print(regis_info["time"])

    # add to the collection
    sensor = db[sensor_name]
    sensor.insert_one(regis_info)

    return f"Posted {regis_info['data']} {regis_info['unit']}, for the time {time} for sensor {sensor_name}"
