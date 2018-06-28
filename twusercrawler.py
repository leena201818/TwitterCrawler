#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import common

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='(%(asctime)s) [%(process)d] %(levelname)s: %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

import sys
import os
import time
import json
import util
import itertools
from twitter_crawler import TwitterCrawler

WAIT_TIME = 10
WAIT_TIME_COLLECT_USER = 1
WAIT_TIME_TREETS = 10
WAIT_TIME_RELATIONS = 1
CLIENT_ARGS = {"timeout": 30}


def flash_cmd_config(cmd_config, cmd_config_filepath, output_folder):
    with open(os.path.abspath(cmd_config_filepath), 'w') as cmd_config_wf:
        json.dump(cmd_config, cmd_config_wf)

    with open(os.path.abspath('%s/%s' % (output_folder, os.path.basename(cmd_config_filepath))), 'w') as cmd_config_wf:
        json.dump(cmd_config, cmd_config_wf)


def collect_tweets_by_search_terms(search_configs_filepath, output_folder, config):
    apikeys = list(config['apikeys'].values()).pop()

    search_configs = {}
    with open(os.path.abspath(search_configs_filepath), 'r') as search_configs_rf:
        search_configs = json.load(search_configs_rf)

    for search_config_id in itertools.cycle(search_configs):

        search_config = search_configs[search_config_id]

        search_terms = [term.lower() for term in search_config['terms']]
        querystring = '%s' % (' OR '.join('(' + term + ')' for term in search_terms))
        since_id = search_config['since_id'] if 'since_id' in search_config else 0
        geocode = tuple(search_config['geocode']) if ('geocode' in search_config and search_config['geocode']) else None

        logger.info('REQUEST -> (md5(querystring): [%s]; since_id: [%d]; geocode: [%s])' % (
        util.md5(querystring.encode('utf-8')), since_id, geocode))

        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder=output_folder)
            since_id = twitterCralwer.search_by_query(querystring, geocode=geocode, since_id=since_id)
        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack())
            pass

        search_config['since_id'] = since_id
        search_config['querystring'] = querystring
        search_config['geocode'] = geocode

        search_configs[search_config_id] = search_config

        flash_cmd_config(search_configs, search_configs_filepath, output_folder)

        logger.info('COMPLETED -> (md5(querystring): [%s]; since_id: [%d]; geocode: [%s])' % (
        util.md5(querystring.encode('utf-8')), since_id, geocode))
        logger.info('PAUSE %ds to CONTINUE...' % WAIT_TIME)
        time.sleep(WAIT_TIME)


def collect_tweets_by_ids(tweet_ids_config_filepath, output_folder, config):
    apikeys = list(config['apikeys'].values()).pop()

    tweet_ids_config = {}
    with open(os.path.abspath(tweet_ids_config_filepath), 'r') as tweet_ids_config_rf:
        tweet_ids_config = json.load(tweet_ids_config_rf)

    max_range = 100

    current_ix = tweet_ids_config['current_ix'] if ('current_ix' in tweet_ids_config) else 0
    total = len(tweet_ids_config['tweet_ids'][current_ix:])
    tweet_id_chuncks = util.chunks(tweet_ids_config['tweet_ids'][current_ix:], max_range)

    for tweet_ids in tweet_id_chuncks:
        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder=output_folder)
            twitterCralwer.lookup_tweets_by_ids(tweet_ids)
            current_ix += len(tweet_ids)

        except Exception as exc:
            logger.error(exc)
            logger.error(
                util.full_stack())  # don't care, if Ctrl+c is hit, does not handle it.  When you restart, it restarts from the last chunk (too much trouble to handle Ctrl + c).
            # you will get duplicate tweets, so what...
            pass

        tweet_ids_config['current_ix'] = current_ix

        flash_cmd_config(tweet_ids_config, tweet_ids_config_filepath, output_folder)

        logger.info('COMPLETED -> (current_ix: [%d/%d])' % (current_ix, total))
        logger.info('PAUSE %ds to CONTINUE...' % WAIT_TIME)
        time.sleep(WAIT_TIME)
    else:
        logger.info('[tweets_by_ids] ALL COMPLETED')


def collect_tweets_by_id_range(tweet_id_range_config_filepath, output_folder, config):
    apikeys = list(config['apikeys'].values()).pop()

    tweet_ids_config = {}
    with open(os.path.abspath(tweet_id_range_config_filepath), 'r') as tweet_id_range_config_rf:
        tweet_id_range_config = json.load(tweet_id_range_config_rf)

    max_range = 100
    current_id = tweet_id_range_config['current_id'] if ('current_id' in tweet_id_range_config) else 0
    end_id = tweet_id_range_config['end_id'] if ('end_id' in tweet_id_range_config) else 0

    tweet_id_chuncks = util.chunks(range(current_id, end_id), max_range)

    for tweet_ids in tweet_id_chuncks:

        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder=output_folder)
            twitterCralwer.lookup_tweets_by_ids(tweet_ids)
            current_id += len(tweet_ids)
        except Exception as exc:
            logger.error(exc)
            logger.error(
                util.full_stack())  # don't care, if Ctrl+c is hit, does not handle it.  When you restart, it restarts from the last chunk (too much trouble to handle Ctrl + c).
            # you will get duplicate tweets, so what...
            pass

        tweet_id_range_config['current_id'] = current_id

        flash_cmd_config(tweet_id_range_config, tweet_id_range_config_filepath, output_folder)

        logger.info('COMPLETED -> (current_id/end_id: [%d/%d])' % (current_id, end_id))
        logger.info('PAUSE %ds to CONTINUE...' % WAIT_TIME)
        time.sleep(WAIT_TIME)
    else:
        logger.info('[tweets_by_id_range] ALL COMPLETED')

'''
ok:save completed
error
'''
def collect_users_all(user_screen_names_ids,deep, output_folder, config):
    apikeys = list(config['apikeys'].values()).pop()

    if user_screen_names_ids.isdigit():
        call = 'user_id'
    else:
        call = 'screen_name'

    try:
        users = [user_screen_names_ids.strip('@')]
        twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS)
        ret = twitterCralwer.fetch_users(call=call, users=users, output_folder=output_folder)

        if ret == 'ok':
            since_id = 1
            ret, since_id, remove = twitterCralwer.fetch_user_timeline(user_screen_names_ids, since_id=since_id)
        if ret == 'ok':
            call = '/friends/ids'
            ret = twitterCralwer.fetch_user_relationships(call=call, user_id=user_screen_names_ids.strip('@'),deep=deep)


    except Exception as exc:
        logger.error(exc)
        return 'error'

    logger.info('PAUSE %ds to CONTINUE...' % WAIT_TIME)
    time.sleep(WAIT_TIME)
    return ret


'''
ok:save completed
error
'''
def collect_users(user_screen_names_ids, output_folder, config):
    apikeys = list(config['apikeys'].values()).pop()

    if user_screen_names_ids.isdigit() :
        call = 'user_id'
    else:
        call = 'screen_name'

    try:
        users = [user_screen_names_ids.strip('@')]
        twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS)
        ret = twitterCralwer.fetch_users(call=call, users=users,output_folder=output_folder)

    except Exception as exc:
        logger.error(exc)
        return 'error'

    logger.info('PAUSE %ds to CONTINUE...' % WAIT_TIME_COLLECT_USER)
    time.sleep(WAIT_TIME_COLLECT_USER)
    return ret

def collect_tweets_by_user_ids(user_id, output_folder, config,since_id = 1):
    apikeys = list(config['apikeys'].values()).pop()

    try:
        twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder=output_folder)
        ret,since_id, remove = twitterCralwer.fetch_user_timeline(user_id, since_id=since_id)
    except Exception as exc:
        logger.error(exc)
        return 'error'

    logger.info('COMPLETED -> (user_id: [%s]; since_id: [%d]; remove: [%s])' % (user_id, since_id, remove))
    logger.info('PAUSE %ds to CONTINUE...' % WAIT_TIME_TREETS)
    time.sleep(WAIT_TIME_TREETS)
    return ret


def collect_user_relatinoships_by_user_ids(call, user_id, deep,output_folder, config):
    apikeys = list(config['apikeys'].values()).pop()

    try:
        twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder=output_folder)
        ret = twitterCralwer.fetch_user_relationships(call=call, user_id=user_id.strip('@'),deep=deep)
    except Exception as exc:
        logger.error(exc)
        return 'error'
        pass

    logger.info('PAUSE %ds to CONTINUE...' % WAIT_TIME_RELATIONS)
    time.sleep(WAIT_TIME_RELATIONS)
    return  ret

def collect_places(call, places_config_filepath, output_folder, config):
    '''
        query: places_config_filepath = {"current_ix": 0, "places": ["Gainesville, FL", "Shanghai, China"]}
        ip: places_config_filepath = {"current_ix": 0, "places": ["74.125.19.104"]}
    '''

    apikeys = list(config['apikeys'].values()).pop()

    places_config = {}
    with open(os.path.abspath(places_config_filepath), 'r') as places_config_rf:
        places_config = json.load(places_config_rf)

    current_ix = places_config['current_ix'] if ('current_ix' in places_config) else 0

    places = places_config['places'][current_ix:]
    total = len(places)

    for place in places:
        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, oauth2=False, client_args=CLIENT_ARGS,
                                            output_folder=output_folder)
            twitterCralwer.geo_search(call=call, query=place)
            current_ix += 1  # one at a time... no choice
        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack())
            pass

        places_config['current_ix'] = current_ix

        flash_cmd_config(places_config, places_config_filepath, output_folder)

        logger.info('COMPLETED -> (current_ix: [%d/%d])' % (current_ix, total))
        logger.info('PAUSE %ds to CONTINUE...' % WAIT_TIME)
        time.sleep(WAIT_TIME)
    else:
        logger.info('collect_places_by_[%s] ALL COMPLETED' % (call))


def dospider(taskInfo):

    config_file = './config.json'

    if (not os.path.exists('logs')):
        os.makedirs('logs')

    formatter = logging.Formatter('(%(asctime)s) [%(process)d] %(levelname)s: %(message)s')
    handler = logging.handlers.RotatingFileHandler(
        'logs/twitter_tracker_%s.log' % taskInfo['tasktype'], maxBytes=50 * 1024 * 1024, backupCount=10)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info(sys.version)

    with open(os.path.abspath(config_file), 'r') as config_f:
        config = json.load(config_f)
        ret = 0
        try:
            deep = int(taskInfo['deep']) + 1

            if (taskInfo['tasktype'] == 'Twitter.userInfo'):
                output = './data/users_allinfo'
                output_folder = os.path.abspath(output)
                command_config = taskInfo['fbid']

                ret = collect_users_all(command_config,deep,output_folder, config)
                if ret == 'ok':
                    return 1
            elif (taskInfo['tasktype'] == 'Twitter.userBaseinfo'):
                output = './data/users_by_screen_names_ids'
                output_folder = os.path.abspath(output)
                command_config = taskInfo['fbid']
                ret = collect_users(command_config, output_folder, config)
                if ret == 'ok':
                    return 1
            # elif (taskInfo['tasktype'] in ['/friends/ids', '/friends/list', '/followers/ids', '/followers/list']):
            elif (taskInfo['tasktype'] == 'Twitter.userFriends'):
                output = './data/friends_ids'
                output_folder = os.path.abspath(output)
                command_config = taskInfo['fbid']

                ret = collect_user_relatinoships_by_user_ids('/friends/ids',command_config,deep,output_folder,config)
                if ret == 'ok':
                    return 1

            elif (taskInfo['tasktype'] == 'Twitter.userTimeline'):
                output = './data/friends_ids'
                output_folder = os.path.abspath(output)
                command_config = taskInfo['fbid']
                ret = collect_tweets_by_user_ids(command_config, output_folder, config)
                if ret == 'ok':
                    return 1



            elif (taskInfo['tasktype'] == 'search'):
                collect_tweets_by_search_terms(args.command_config, output_folder, config)
            elif (taskInfo['tasktype'] == 'user_timelines'):
                collect_tweets_by_user_ids(args.command_config, output_folder, config)
            elif (taskInfo['tasktype'] == 'tweets_by_ids'):
                collect_tweets_by_ids(args.command_config, output_folder, config)
            elif (taskInfo['tasktype'] == 'tweets_by_id_range'):
                collect_tweets_by_id_range(args.command_config, args.output, config)
            elif (taskInfo['tasktype'] == 'users_by_ids'):
                collect_users('user_id', args.command_config, args.output, config)
            elif (taskInfo['tasktype'] == 'users_by_screen_names'):
                collect_users('screen_name', args.command_config, args.output, config)
            elif (taskInfo['tasktype'] == 'places_by_queries'):
                collect_places('query', args.command_config, args.output, config)
            elif (taskInfo['tasktype'] == 'places_by_ips'):
                collect_places('ip', args.command_config, args.output, config)
            else:
                raise Exception("tasktype not found!")
        except KeyboardInterrupt:
            logger.error('You pressed Ctrl+C! SO I JUST Killed myself...')
            ret = 0
        except Exception as exc:
            logger.error(exc)
            ret = 0
        finally:
            pass

        return ret
