#!/usr/bin/python3
# usage: python action-mongo-atlas-nuke.py
# export MONGODB_ATLAS_PRIVATE_KEY, MONGODB_ATLAS_PUBLIC_KEY as env variable
#########################################################################################################
# coding=utf-8
import os
import requests
import json
from requests.auth import HTTPDigestAuth
from retry import retry
from typing import List


def get_all_projects(public: str, private: str, url: str) -> List[str]:
    project_url = url + "/groups"
    response = requests.request("GET", project_url, auth=HTTPDigestAuth(public, private))
    project_list = json.loads(response.content)
    id_list = []
    for p in project_list['results']:
        id_list.append(p['id'])
    return id_list


def get_cluster_name(public: str, private: str, url: str, project_id: str) -> str:
    cluster_url = url + "/groups/" + project_id + "/clusters"
    response = requests.request("GET", cluster_url, auth=HTTPDigestAuth(public, private))
    cluster_list = json.loads(response.content)
    for c in cluster_list['results']:
        cluster_name = c['name']
        return cluster_name


def delete_cluster(public: str, private: str, url: str, project_id: str, cluster_name: str) -> None:
    cluster_delete_url = url + "/groups/" + project_id + "/clusters/" + cluster_name
    response = requests.request("DELETE", cluster_delete_url, auth=HTTPDigestAuth(public, private))
    print(response)


@retry(delay=60, tries=5)
def delete_project(public: str, private: str, url: str, project_id: str) -> None:
    status = None
    try:
        project_delete_url = url + "/groups/" + project_id
        response = requests.request("DELETE", project_delete_url, auth=HTTPDigestAuth(public, private))
        statuscode = response.status_code
        if statuscode != 202:
            raise

    except Exception as error:
        print(error)
        raise


def main():
    base_url = "https://cloud.mongodb.com/api/atlas/v1.0"
    public_key = os.environ["MONGODB_ATLAS_PUBLIC_KEY"]
    private_key = os.environ["MONGODB_ATLAS_PRIVATE_KEY"]

    # get all project ids in org
    id_list = get_all_projects(public_key, private_key, base_url)

    # for each project id, get cluster name and delete
    for project_id in id_list:
        cluster_name = get_cluster_name(public_key, private_key, base_url, project_id)
        if cluster_name is not None:
            print(f"deleting {cluster_name} cluster")
            delete_cluster(public_key, private_key, base_url, project_id, cluster_name)

    # delete all projects with retry logic
    for project_id in id_list:
        print(f"deleting {project_id} project")
        delete_project(public_key, private_key, base_url, project_id)


main()
