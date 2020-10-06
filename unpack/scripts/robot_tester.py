import urllib.robotparser
from urllib.parse import urlparse

user_agent = 'unpackbot'
url = "https://buzzfeed.com/contests"
parsed_url = urlparse(url)
robot_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
print(url, robot_url)
robotparser = urllib.robotparser.RobotFileParser()
robotparser.set_url(robot_url)
robotparser.read()
can_fetch = robotparser.can_fetch(user_agent, url)
print(can_fetch)
