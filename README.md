# CPCleanupGlobalObject

This tools provides a way how to determine, if some global object created in Check Point global policy is used across all domains or not.

How does it work?
1. Get all network objects from global policy (hosts,networks,groups,address-range)
2. Search over each domain to check if particular object is used or not - using where-used api command
3. Write down results and generate API CLI commands for object deletion

By default is generating list of objects, which are not used in any domain or just used in one domain. 
Example: you have 12 domains on MDS and reported object is not used in any of 12 domains or it's just used on 1 domain from 12
