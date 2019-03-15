import argparse
import getpass
import os
from cpapi import APIClient, APIClientArgs
from collections import Counter

argpar = argparse.ArgumentParser()
argpar.add_argument("-u", "--username", required=False, default=os.getenv('MGMT_CLI_USER'),
                    help="The management administrator's user name.\nEnvironment variable: MGMT_CLI_USER")
argpar.add_argument("-p", "--password", required=False,
                    help="The management administrator's password.\nEnvironment variable: MGMT_CLI_PASSWORD")
argpar.add_argument("-m", "--management", required=False, default=os.getenv('MGMT_CLI_MANAGEMENT', "127.0.0.1"),
                    help="The management server's IP address (In the case of a Multi-Domain Environment, use the IP address of the MDS domain).\nDefault: 127.0.0.1\nEnvironment variable: MGMT_CLI_MANAGEMENT")
argpar.add_argument("--port", "--server-port", required=False, default=os.getenv('MGMT_CLI_PORT', 443),
                    help="The port of the management server\nDefault: 443\nEnvironment variable: MGMT_CLI_PORT")
argpar.add_argument("-g", "--globaldomain", required=False, default=os.getenv('MGMT_CLI_GDOMAIN',"Global"),
                    help="The name, uid or IP-address of the global domain\nEnvironment variable: MGMT_CLI_DOMAIN")

def where_global_used(client,user,password,type_objects,domain):
    login_res = client.login(user,password,domain=domain)
    if login_res.success is False:
        print("Login failed: {}".format(login_res.error_message))
        exit(1)
    # print(domain)
    counter = 0
    obj_counter= list()
    uid_list = list()
    for uid, details in type_objects.items():
        uid_list.append(uid)
        # print(details)
    for obj in uid_list:
        # print(obj)
        counter +=1
        # where_used = client.api_call("where-used",{'uid':obj})
        # if where_used.data['used-directly']['total'] == 0:
        #     print("Object with name: ",obj,"not used on domain",domain)
        # if counter < 5:
        where_used = client.api_call("where-used", {'uid': obj})
        try:
            if where_used.data['used-directly']['total'] == 0:
                # print("Object with name: ", type_objects[obj][0], "not used on domain", domain)
                obj_counter.append(obj)
        except Exception as e:
            print(e,where_used.response())
    client.api_call("logout")
    return obj_counter


def main():
    # getting details from the user
    results = argpar.parse_args()
    # print results
    api_server = results.management
    user = results.username
    password = results.password
    port = results.port
    gdomain = results.globaldomain
    port = "443"

    if not user:
        user = input("Username:")

    if not api_server:
        api_server = input("Management IP:")
    if not password:
        password = getpass.getpass("Enter password: ")

    if not gdomain:
        gdomain = input("Global domain name:")
    client_args = APIClientArgs(server=api_server)
    with APIClient(client_args) as client:
        if client.check_fingerprint() is False:
            print("Could not get the server's fingerprint - Check connectivity with the server.")
            exit(1)
        login_res = client.login(user, password)
        if login_res.success is False:
            print("Login failed: {}".format(login_res.error_message))
            exit(1)
        objects_dict = dict()
        obj_type = ["group",'network','host','address-range']
        # obj_type = ["group"]

        domains = client.api_query("show-domains")
        client.api_call("logout")
        domains_list = list()
        for domain in domains.data:
            domains_list.append(domain['name'])
        print (domains_list)
        login_res = client.login(user, password,domain=gdomain)
        if login_res.success is False:
            print("Login failed: {}".format(login_res.error_message))
            exit(1)
        for obj_typ in obj_type:
            list_all = dict()
            print("Working on: ", obj_typ)
            global_type = client.api_query("show-"+obj_typ+"s","standard")
            print("Total amount: ", global_type.data.__len__())
            for item in global_type.data:
                list_all[item['uid']] = [item['name'],item['domain']['name']]
            objects_dict[obj_typ] = list_all
        domain = "global"
        for k, v in objects_dict.items():
            fout = open(domain+"_"+k+".csv",'w')
            for x, y in v.items():
                fout.write("{};{}\r".format(x,y))
            fout.close()
        client.api_call("logout")
        results_csv = open('results.csv','w')
        results_csv.write(obj_typ +",occurencies,object_name,uid\r")
        usage_obj_counter_result = list()
        for domain in domains_list:
            for obj_typ, type_objects in objects_dict.items():
                usage_obj_counter = where_global_used(client,user,password,type_objects,domain)
                print("done with ",obj_typ, "on", domain)
                usage_obj_counter_result +=usage_obj_counter
                summary =(Counter(usage_obj_counter_result))
                for uid,hitcount in summary.items():
                    if hitcount > (len(domains_list)-2) :
                        if type_objects.get(uid):
                            cli_command = "delete {} uid {}".format(obj_typ,uid)
                            results_csv.write(obj_typ+","+str(hitcount)+","+type_objects[uid][0]+","+uid+","+cli_command+"\r")

        results_csv.close()




if __name__ == "__main__":
    main()
