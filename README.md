# dumpytter

## Overview
dumpytter retrieves your tweets and store them into a SQLite DB.

## Required Libraries
- rauth

## Preparation

#### Get twitter API tokens

You first need to get a consumer key, a consumer secret, an access token, and an access token secret on [Twitter Application Management site](https://apps.twitter.com/).

You then create a config file `~/.dumpytter/config.ini`:

	[global]
	consumer_key = xxxxxx
	consumer_sec = xxxxxx
	access_token = xxxxxx
	access_sec   = xxxxxx

#### DB file creation

Open terminal to create a DB table as well as a DB file:

	$ mkdir ~/.dumpytter
	$ sqlite3 ~/.dumpytter/dumpytter.db < sql/tbl_create.sql

## Usage

## Copyright, License
Copyright (c) 2015, Shigemi ISHIDA


This software is released under the BSD 3-clause license.
See LICENSE.
