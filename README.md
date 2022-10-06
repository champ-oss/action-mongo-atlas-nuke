# action-mongo-atlas-nuke

Summary: This github action is used to delete Mongo Atlas cluster and project resources on a daily basis or as needed.

![ci](https://github.com/conventional-changelog/standard-version/workflows/ci/badge.svg)
[![version](https://img.shields.io/badge/version-1.x-yellow.svg)](https://semver.org)

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#Features)
* [Assumptions](#Assumptions)
* [Usage](#usage)
* [Project Status](#project-status)

## General Information
- mongo-nuke action

## Technologies Used
- python script
- github actions

## Features

* check for all projects
* delete all clusters from project list
* added retry logic to make sure all clusters are deleted
* delete all projects once clusters are deleted

## Assumptions

* action is good for ephemeral type org to delete resources on daily basis

## Usage

* look at examples/action-mongo-atlas-nuke.yml for usage

## Project Status
Project is: _in_progress_ 