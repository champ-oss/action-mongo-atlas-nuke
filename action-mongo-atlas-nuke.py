#!/usr/bin/python3
# usage: python action-mongo-atlas-nuke.py
# export MONGODB_ATLAS_PRIVATE_KEY, MONGODB_ATLAS_PUBLIC_KEY, PREFIX_PROJECT_INCLUDE as env variable
#########################################################################################################
# coding=utf-8
from __future__ import annotations

import os
from typing import List

import requests
import json
from requests.auth import HTTPDigestAuth
from retry import retry


def get_all_projects(public: str, private: str, url: str, prefix_project_include: str) -> List[str]:
    project_url = url + "/groups"
    response = requests.request("GET", project_url, auth=HTTPDigestAuth(public, private))
    project_list = json.loads(response.content)
    project_id_list = list()
    for project in project_list['results']:
        if project['name'].startswith(prefix_project_include):
            project_id = project['id']
            project_id_list.append(project_id)
    return project_id_list


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
    return None


def main():
    base_url = "https://cloud.mongodb.com/api/atlas/v1.0"
    public_key = os.environ["MONGODB_ATLAS_PUBLIC_KEY"]
    private_key = os.environ["MONGODB_ATLAS_PRIVATE_KEY"]
    # prefix mongo atlas project that are available to delete
    prefix_project_include = os.environ["PREFIX_PROJECT_INCLUDE"]

    # get all project ids in org, include prefix of projects that will be part of delete
    id_list = get_all_projects(public_key, private_key, base_url, prefix_project_include)

    # for each project id, get cluster name and delete
    for project_id in id_list:
        cluster_name = get_cluster_name(public_key, private_key, base_url, project_id)
        if cluster_name is not None:
            print(f"deleting {cluster_name} cluster")
            delete_cluster(public_key, private_key, base_url, project_id, cluster_name)

    # delete given projects with retry logic
    for project_id in id_list:
        try:
            print(f"deleting {project_id} project")
            delete_project(public_key, private_key, base_url, project_id)
        except:
            print(f"problem deleting {project_id} project, may not exist")


main()
