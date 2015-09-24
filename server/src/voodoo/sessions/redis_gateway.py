#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Xabier Larrakoetxea <xabier.larrakoetxea@deusto.es>
#         Pablo Orduña <pablo.orduna@deusto.es>
#
from __future__ import print_function, unicode_literals

import redis
import time
import voodoo.sessions.generator  as SessionGenerator
import voodoo.sessions.serializer as SessionSerializer
import voodoo.sessions.exc as SessionErrors

SESSION_REDIS_HOST = 'session_redis_host'
DEFAULT_SESSION_REDIS_HOST = 'localhost'

SESSION_REDIS_PORT = 'session_redis_port'
DEFAULT_SESSION_REDIS_PORT = 6379

SESSION_REDIS_LOCK_HASH_KEY = "redis_session_lock_hash_key"
DEFAULT_SESSION_REDIS_LOCK_HASH_KEY = "weblab_session:locks"

SESSION_REDIS_KEY_PREFIX = "redis_session_key_prefix"
DEFAULT_SESSION_REDIS_KEY_PREFIX = "weblab_session_data:"


class SessionRedisGateway(object):
    
    #static
    redisPools={}
    
    def __init__(self, cfg_manager, session_pool_id, timeout):
        
        #check if the pool id is an integer
        try:
            int(session_pool_id)
        except ValueError:
            raise TypeError("Session pool id needs to be an integer. Got '%s'" % session_pool_id)
        
        self.session_pool_id = session_pool_id
        if timeout is None:
            self.timeout = 10 * 365 * 24 * 3600 # expire in 10 years (also known as "never expire")
        else:
            self.timeout         = timeout
        self.cfg_manager     = cfg_manager
        (
            host,
            port,
            db_index,
            self.session_lock_key, #class var
            self.session_key_prefix, #class var
        ) = self._parse_config()
        
        
        self._generator  = SessionGenerator.SessionGenerator()
        self._serializer = SessionSerializer.SessionSerializer()
        
        
        #New pool or not new?
        if session_pool_id not in self.redisPools:
            pool = redis.ConnectionPool(host=host, port=port, db=db_index)
            SessionRedisGateway.redisPools[self.session_pool_id] = pool
        else:
            pool = self.redisPools[self.session_pool_id] 
        
        #We have the redis client now
        self._client_creator = lambda : redis.Redis(connection_pool=pool)
    
    def _parse_config(self):
        host                = self.cfg_manager.get_value(SESSION_REDIS_HOST, DEFAULT_SESSION_REDIS_HOST)
        port                = self.cfg_manager.get_value(SESSION_REDIS_PORT, DEFAULT_SESSION_REDIS_PORT)
        db_index             = self.session_pool_id
        session_lock_key      = self.cfg_manager.get_value(SESSION_REDIS_KEY_PREFIX, DEFAULT_SESSION_REDIS_LOCK_HASH_KEY)
        session_key_prefix    = self.cfg_manager.get_value(SESSION_REDIS_KEY_PREFIX, DEFAULT_SESSION_REDIS_KEY_PREFIX)
        return host, port, db_index, session_lock_key, session_key_prefix

    def clear(self):
        client = self._client_creator()
        # Get all the sessions data
        session_redis_keys = client.keys(self.session_key_prefix + '*')
        #append to the list the session lock key
        session_redis_keys.append(self.session_lock_key)
        #delete all
        client.delete(*session_redis_keys)
    
    def create_session(self, desired_sess_id=None):
        client = self._client_creator()
        
        if desired_sess_id is not None:
            new_id = desired_sess_id
            
            if client.exists(self.session_key_prefix + new_id):
                raise SessionErrors.DesiredSessionIdAlreadyExistsError("session_id: %s" % new_id)
        else:
            new_id = self._generator.generate_id()
        
        #lock session access with redis method
        while True:
            done = client.hset(self.session_lock_key, new_id, 1)
            if done == 1:
                break
            else: 
                if desired_sess_id is not None:
                    raise SessionErrors.DesiredSessionIdAlreadyExistsError("session_id: %s" % desired_sess_id)
                new_id = self._generator.generate_id()

        #Create session
        pickled_session = self._serializer.serialize({})
        client.setex(self.session_key_prefix + new_id, pickled_session, self.timeout)
                
        #Unlock session
        client.hdel(self.session_lock_key, new_id)
        return new_id
    
    
    
    def has_session(self, session_id):
        client = self._client_creator()
        return client.exists(self.session_key_prefix + session_id)
    
    
    
    def _get_session(self, session_id, redis_client):
        
        session_key = self.session_key_prefix + session_id
        
        #get the session
        pickled_session = redis_client.get(session_key)
        if pickled_session is None:
            raise SessionErrors.SessionNotFoundError( "Session not found: " + session_id )
        
        #reset the expiration
        redis_client.expire(session_key, self.timeout)
        
        #Unpickle and return the session
        return self._serializer.deserialize(pickled_session)
    
    
    
    def get_session(self, session_id):
        client = self._client_creator()
        return self._get_session(session_id, client)

    def _lock(self, client, session_id):
        #lock session access with redis method
        while True:
            done = client.hset(self.session_lock_key, session_id, 1)
            
            if done == 1:
                break
            else: 
                time.sleep(0.05)

    def get_session_locking(self, session_id):        
        client = self._client_creator()
        self._lock(client, session_id)

        try:
            session = self._get_session(session_id, client)
        except SessionErrors.SessionNotFoundError:
            #Unlock session
            client.hdel(self.session_lock_key, session_id)
            raise SessionErrors.SessionNotFoundError( "Session not found: " + session_id )
            
        return session



    def _modify_session(self, sess_id, sess_obj, redis_client):
        
        session_key = self.session_key_prefix + sess_id
        
        #insert session again and restart the expiration
        pickled_session = self._serializer.serialize(sess_obj)
       
        if not redis_client.exists(session_key):
            raise SessionErrors.SessionNotFoundError( "Session not found: " + sess_id )

        #delete session
        redis_client.set(session_key, pickled_session)
        redis_client.expire(session_key, self.timeout)

    def modify_session(self, sess_id, sess_obj):
        
        client = self._client_creator()
        self._modify_session(sess_id, sess_obj, client)
        
    
    def modify_session_unlocking(self, sess_id, sess_obj):
        try:
            client = self._client_creator()
            self._modify_session(sess_id, sess_obj, client)
        finally:
            #Unlock session
            client.hdel(self.session_lock_key, sess_id)
        
        
        
    def unlock_without_modifying(self, sess_id):
        
        client = self._client_creator()
        client.hdel(self.session_lock_key, sess_id)
        
    
    def list_sessions(self):
        
        #Get keys
        client = self._client_creator()
        session_redis_keys = client.keys(self.session_key_prefix + '*')
        
        #format and create a list with the keys
        session_keys = []
        for full_session_key in session_redis_keys:
            session_keys.append(full_session_key[len(self.session_key_prefix):])
        
        return session_keys
        
    
    def delete_expired_sessions(self):
        # Redis makes this for us :) but the locks don't expire so we
        # delete the ones that don't have session (zombies)
        self._delete_zombie_locks()
    
    def _delete_session(self, sess_id, redis_client):
        
        session_key = self.session_key_prefix + sess_id
        
        #Delete the session
        if not redis_client.delete(session_key):
            raise SessionErrors.SessionNotFoundError( "Session not found: " + sess_id )
    
    def delete_session(self, sess_id):
        
        client = self._client_creator()
        self._delete_session(sess_id, client)
        
    def delete_session_unlocking(self, sess_id):
        
        client = self._client_creator()
        try:
           self._delete_session(sess_id, client)
        finally:
            #Delete the lock always
            client.hdel(self.session_lock_key, sess_id)  


    def _delete_zombie_locks(self):
        
        client = self._client_creator()
        #Get all the hashes
        keys = client.hkeys(self.session_lock_key)
        
        # No keys, no zombie, no work
        if len(keys) == 0:
            return

        # Obtain the existance of all those keys in a single command
        existance_pipeline = client.pipeline()

        for key in keys:
            existance_pipeline.exists(self.session_key_prefix + key)

        results = existance_pipeline.execute()

        # If every element exists, no work to do
        if all(results):
            return

         # Otherwise, mark the elements to delete in a pipeline
        deleting_pipeline = client.pipeline()

        for key, exists in zip(keys, results):
            if not exists:
                deleting_pipeline.hdel(self.session_lock_key, key)

        # And delete them
        deleting_pipeline.execute()
        
