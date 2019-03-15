# CPCleanupGlobalObject

This tools provides a way how to determine, if some global object created in Check Point global policy is used across all domains or not.

How does it work?
1. Get all network objects from global policy (hosts,networks,groups,address-range)
2. Get list of all domains on MDS
3. Search over each domain to check if particular object is used or not - using where-used api command
4. Write down results and generate API CLI commands for object deletion for each object type

By default is generating list of objects, which are not used in any domain or just used in one domain. 
Example: you have 12 domains on MDS and reported object is not used in any of 12 domains or it's just used on 1 domain from 12 (this kind of object should be only local object)

Requirements:
Download and install the Check Point API Python SDK repository, follow the instructions in the SDK repository.
https://github.com/CheckPointSW/cp_mgmt_api_python_sdk

Written for python3, but if you put in first line also this:
from __future__ import print_function
it should run on python2

How to use?
python global_object_cleanup.py -m management_ip -u username -p password -g "global domain name"


