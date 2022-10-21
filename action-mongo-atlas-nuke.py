#!/usr/bin/python3
# usage: python action-mongo-atlas-nuke.py
# export MONGODB_ATLAS_PRIVATE_KEY, MONGODB_ATLAS_PUBLIC_KEY, MONGODB_PROJECT_ID_LIST as env variable
#########################################################################################################
# coding=utf-8
from __future__ import annotations

import os
import requests
import json
from requests.auth import HTTPDigestAuth
from retry import retry


def get_cluster_name(public: str, private: str, url: str, project_id: str) -> str | None:
    try:
        cluster_url = url + "/groups/" + project_id + "/clusters"
        response = requests.request("GET", cluster_url, auth=HTTPDigestAuth(public, private))
        cluster_list = json.loads(response.content)
        for cluster in cluster_list['results']:
            return cluster['name']
    except:
        return None


def delete_cluster(public: str, private: str, url: str, project_id: str, cluster_name: str) -> None:
    cluster_delete_url = url + "/groups/" + project_id + "/clusters/" + cluster_name
    response = requests.request("DELETE", cluster_delete_url, auth=HTTPDigestAuth(public, private))
    print(response)


@retry(delay=15, tries=40)
def delete_project(public: str, private: str, url: str, project_id: str) -> None:
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

    # load list into variable
    id_list = json.loads(os.environ["MONGODB_PROJECT_ID_LIST"])

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
