import os 
import subprocess
import json
from sys import platform as _platform

"""
Author: Carl Kenny | csk29@uclive.ac.nz
Prog:   Console script that alerts user when the desired twitch channel surpasses n 
        followers. Is extremely useful for competitions where the streamer 
        announces that they will giveaway a prize at n followers
Note:   The API only allows 100 calls at a time, so if there are a lot of followers,
        this may take some serious time to process (maybe even minutes!).
Usage:  python3 twitch_followers_count.py
Date:   23/11/2014
"""

LIMIT = 100

def callCurlAndWriteToFile(channel, outputFile, offset, maxCount, currentCount=0):
    """ 
    Runs curl and redirects a json object to the desired output file 
    Example Twitch API calls
      "next": "https://api.twitch.tv/kraken/channels/test_user1/follows?limit=25&offset=25",
      "self": "https://api.twitch.tv/kraken/channels/test_user1/follows?limit=25&offset=0"
    """

    curlCall = "curl -H 'Accept: application/vnd.twitchtv.v2+json' \
            -X GET https://api.twitch.tv/kraken/channels/" + channel + '/follows/?limit=' + str(LIMIT)

    # Create JSON obj(dict) and decode it
    jsonObj = subprocess.check_output(curlCall, shell=True).decode("utf-8")
    decodedJSON = json.loads(jsonObj)
    
    # Append the decoded JSON obj to a tmp file (create if doesn't exist)
    fileName = os.getcwd() + '/twitch_followers_tmp.txt'
    fileTmp = open(fileName, 'w')
    fileTmp.write(jsonObj)
    fileTmp.close()

    currentCount += len(json.load(open(fileName))['follows'])

    try:
        if (len(decodedJSON['follows'])) < 100:
            # last recursive call
            followCount = len(fileTmp['follows'])
            fileTmp.close()
        elif currentCount > maxCount:
            os.remove(fileName)
            notifyUser(currentCount, channel)
        else:
            offset += 100
            callCurlAndWriteToFile(channel, outputFile, offset, maxCount, currentCount)
    except TypeError:
        print("Invalid URL, please check your spelling/\n###RESTARTING###")
        main()


def notifyUser(followers, channel):
    """ 
    Checks for host OS, then decides on an appropriate GUI pop-up message 
    :param followers int
    :param channel str
    :return void
    """

    if _platform == "linux" or _platform == "linux2":
        message = \
            "xmessage -print 'THE CHANNEL HAS REACHED {} GET IN QUICK. " \
            "Here is the URL: https://www.twitch.tv/{}'".format(str(followers), channel)
        os.system(message)
    else:
        print("THE CHANNEL HAS REACHED {} GET IN QUICK. " \
            "Here is the URL: https://www.twitch.tv/{}'".format(str(followers), channel))


def getChannelName():
    """ Returns string of channel name """
    return input("Complete the name of the channel, follow by [RETURN]\ntwitch.tv/")


def getFollowCount():
    """ Returns int of desired follow threshold """
    # TODO: Add the abililty to attempt to scrap this from the channel description
    return int(input("You will be notified when the follows surpass a threshold. \ "
                     "\nEnter the follower limit: "))


def main():
    channel = getChannelName()
    workingDirectory = os.getcwd()
    outputFile = workingDirectory + "followerCount.txt"
    maxCount = getFollowCount()
    offset = 0
    callCurlAndWriteToFile(channel, outputFile, offset, maxCount)

if __name__ == '__main__':
    main()
