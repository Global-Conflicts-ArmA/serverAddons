
from pymongo import MongoClient
from .threading_utils import call_slow_function, has_call_finished, get_call_value
from datetime import datetime
import logging
from .env import mongo_host_uri, debug
import requests as requests
from bson import ObjectId


logger = logging.getLogger(__name__)

client = MongoClient(mongo_host_uri)
db = client.prod


def get_bugreports(steam_id, mission_name):
    
    
    if debug == 1:
        steam_id = "76561198000360814"
        mission_name = "co23_testmiss_v2.mapn_ame"
        
        
    version, unique_name = get_name_and_version(mission_name)
    mission = db.get_collection("missions").find_one(
        {
            "uniqueName": unique_name,
        },
        projection={"reports": 1}
    )

    validation_result = validate_user(steam_id)

    if validation_result["error"]:
        return [validation_result["error"], False]

    if not mission:
        logger.critical("Mission not found failed. %s", str({
            "query": {
                "uniqueName": unique_name,
            }

        }))
        return [f"Failed looking up mission.", False]

    # replace /n with <br/>
    reports = ""
    bugIndex = 1
    for reportObj in mission.get("reports", []):
        text = reportObj.get("text", "")

        reports = reports + f"<t font='EtelkaMonospacePro'>{bugIndex}#</t><br/>"
        reports = reports + text.replace("/n", "<br/>") + "<br/><br/>"
        bugIndex = bugIndex + 1

    # build strucuted text

    return [reports, True]


def submit_rating(message, steam_id, mission_name):

    if debug == 1:
        steam_id = "76561198000360814"
        mission_name = "co23_testmiss_v2.mapn_ame"

    validation_result = validate_user(steam_id)

    if validation_result["error"]:
        return [validation_result["error"], False]

    user = validation_result["user"]

    rating = {
        "date": datetime.now(),
        "ratingAuthorId": user["discord_id"],
        "value": message,
    }
    version, unique_name = get_name_and_version(mission_name)
    has_rating = db.get_collection("missions").find_one(
        {
            "uniqueName": unique_name,
            "ratings.ratingAuthorId": user["discord_id"]
        }
    )

    if has_rating:

        db.get_collection("missions").update_one(
            {
                "uniqueName": unique_name,
                "ratings.ratingAuthorId": user["discord_id"]
            },
            {
                "$set": {
                    "ratings.$.value":  message,
                    "ratings.$.date":  datetime.now()
                }
            }
        )
    else:
        db.get_collection("missions").update_one(
            {
                "uniqueName": unique_name,

            }, {
                "$addToSet": {"ratings": rating}
            }
        )

    return [f"Rating submited!", True]


def validate_user(steam_id):
    user = db.get_collection("users").find_one(
        {"steam.steam_id": steam_id})

    if not user:
        return {
            "error": "Steam account not linked. Go to your profile page on the website and link it to use this feature."}

    try:
        is_blacklisted = user['blacklist']['website']
        if is_blacklisted:
            return {"error": "You are blacklisted from interactions with the website."}
    except KeyError:
        pass
    return {"user": user, "error": None}


def submit_review_or_bugreport(message, steam_id, mission_name, type_str):

    if debug == 1:
        steam_id = "76561198000360814"
        mission_name = "co23_testmiss_v2.mapn_ame"

    validation_result = validate_user(steam_id)

    if validation_result["error"]:
        return [validation_result["error"], False]

    user = validation_result["user"]

    version, unique_name = get_name_and_version(mission_name)

    add = {f"{type_str}s": {
        "_id": ObjectId(),
        "version": version,
        "authorID": user["discord_id"],
        "date": datetime.now(),
        "text": message.strip(),
    }}

    mission = db.get_collection("missions").find_one_and_update(
        {
            "uniqueName": unique_name,
        },
        {
            "$addToSet": add,
        }, projection={"name": 1, "authorID": 1}
    )

    if not mission:
        logger.critical("Mission not found or review insertion failed. %s", str({
            "query": {
                "uniqueName": unique_name,
            },
            "update": {
                "$addToSet": add,
            }
        }))
        return [f"Failed submiting {type_str}.", False]

    try:
        discord_user = get_discord_user(user["discord_id"])
    except Exception as e:
        return ["Error retrieving Discord user", False]

    data = {
        "name": mission["name"],
        "uniqueName": unique_name,
        type_str: message.strip(),
        "version": version,
        f"{type_str}Author": discord_user["nickname"] or discord_user["displayName"],
        "reviewDisplayAvatarURL": discord_user["displayAvatarURL"],
        "authorId": mission["authorID"],
    }

    try:
        send_to_bot(data, type_str)
    except Exception:
        return [f"{type_str.capitalize()} submited, but failed sending it to the bot.", True]

    return [f"{type_str.capitalize()} submited!", True]


def get_name_and_version(mission_name):
    name_start = mission_name.find("_")
    if "." in mission_name:
        name_end = mission_name.rfind(".")
    else:
        name_end = len(mission_name)
        
    unique_name_with_version = mission_name[name_start + 1:name_end]
    version = unique_name_with_version[unique_name_with_version.rfind(
        "_") + 1:]
    name_end = unique_name_with_version.rfind("_")

    unique_name = unique_name_with_version[:name_end]
    return version, unique_name


def call_submit_review(message, steam_id, mission_name):
    return call_slow_function(submit_review_or_bugreport, (message, steam_id, mission_name, "review"))


def call_submit_bugreport(message, steam_id, mission_name):
    return call_slow_function(submit_review_or_bugreport, (message, steam_id, mission_name, "report"))


def call_get_bugreports(steam_id, mission_name):
    return call_slow_function(get_bugreports, (steam_id, mission_name))


def call_submit_rating(message, steam_id, mission_name):
    return call_slow_function(submit_rating, (message, steam_id, mission_name))


def send_to_bot(review_data, type_str):

    req = requests.post(
        f"http://localhost:3001/missions/{'review' if type_str=='review' else 'bugreport'}", data=review_data)

    if req.status_code != 201:
        logger.warn("Failed sending it to the bot. %s", str(req))
        raise f"Error sending {type_str} to bot."
    else:

        return "ok"


def get_discord_user(discord_id):

    req = requests.get(
        f'http://localhost:3001/users/{discord_id}')
    if req.status_code != 200:
        raise "Error retrieving Discord user."
    else:
        return req.json()


has_call_finished  # noqa - this function has been imported from threading_utils.py
get_call_value  # noqa - this function has been imported from threading_utils.py
