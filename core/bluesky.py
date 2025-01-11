#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
(c) by Lukas Brunner (lukas.brunner@uni-hamburg.de) 2024 under a MIT License (https://mit-license.org)

Summary:

"""
import os
from atproto import Client

from secret import passwort


def _reply_to(reply_root, reply_parent):
    # https://atproto.blue/en/latest/atproto/atproto_client.models.app.bsky.feed.post.html#atproto_client.models.app.bsky.feed.post.ReplyRef
    
    if reply_root is None:
        return None
    if reply_parent is None:  # reply to top-level post
        return {
        "root": vars(reply_root), 
        "parent": vars(reply_root),
        }
    return {
        "root": vars(reply_root),
        "parent": vars(reply_parent),
    }


def post_image(
    fn, 
    text='', 
    image_alt='', 
    reply_root=None, 
    reply_parent=None, 
    langs=['english', 'german'],
):
    if langs == 'en':
        langs = ['english']
    elif langs == 'dt':
        langs == ['german']
        
    client = Client()
    client.login('weather-climate.bsky.social', passwort)

    with open(fn, 'rb') as ff:
        img = ff.read()
        
    return client.send_image(
        text=text,
        image=img,
        image_alt=image_alt,
        langs=langs,
        image_aspect_ratio={
                "width": 2,
                "height": 1
            },
        reply_to=_reply_to(reply_root, reply_parent),
    )


def post_gif(
    fn, 
    text='', 
    gif_alt='', 
    reply_root=None, 
    reply_parent=None,
    langs=['english', 'german'],
):
    if langs == 'en':
        langs = ['english']
    elif langs == 'dt':
        langs == ['german']
        
    client = Client()
    client.login('weather-climate.bsky.social', passwort)

    with open(fn, 'rb') as ff:
        gif = ff.read()
        
    return client.send_video(
        text=text,
        video=gif,
        video_alt=gif_alt,
        langs=langs,
        reply_to=_reply_to(reply_root, reply_parent),
    )


def post(
    fn, 
    text='', 
    alt='', 
    reply_root=None, 
    reply_parent=None,
    langs=['english', 'german'],
):
    if fn.endswith('.png'):
        return post_image(fn, text=text, image_alt=alt, reply_root=reply_root, reply_parent=reply_parent, langs=langs)
    elif fn.endsweith('.gif'):
        return post_gif(fn, text=text, gif_alt=alt, reply_root=reply_root, reply_parent=reply_parent, langs=langs)
    else:
        raise NotImplementedError
        