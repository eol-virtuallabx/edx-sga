"""
Utility functions for the SGA XBlock
"""
from __future__ import absolute_import

import datetime
import hashlib
import os
import time
from functools import partial

import six

import pytz
from django.conf import settings
from django.core.files.storage import default_storage
from edx_sga.storage import SgaStorage
from edx_sga.constants import BLOCK_SIZE

sga_storage = SgaStorage()

def utcnow():
    """
    Get current date and time in UTC
    """
    return datetime.datetime.now(tz=pytz.utc)


def is_finalized_submission(submission_data):
    """
    Helper function to determine whether or not a Submission was finalized by the student
    """
    if submission_data and submission_data.get('answer') is not None:
        return submission_data['answer'].get('finalized', True)
    return False


def get_file_modified_time_utc(file_path):
    """
    Gets the UTC timezone-aware modified time of a file at the given file path
    """
    if settings.DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage':
        return pytz.utc.localize(datetime.datetime.utcfromtimestamp(os.path.getmtime(default_storage.path(file_path))))
    file_timezone = pytz.utc

    return file_timezone.localize(
        sga_storage.modified_time(file_path)
    ).astimezone(
        pytz.utc
    )


def get_sha1(file_descriptor):
    """
    Get file hex digest (fingerprint).
    """
    sha1 = hashlib.sha1()
    for block in iter(partial(file_descriptor.read, BLOCK_SIZE), b''):
        sha1.update(block)
    file_descriptor.seek(0)
    return sha1.hexdigest()


def get_file_storage_path(locator, file_hash, original_filename):
    """
    Returns the file path for an uploaded SGA submission file
    """
    return (
        six.u(
            '{loc.org}/{loc.course}/{loc.block_type}/{loc.block_id}/{file_hash}{ext}'
        ).format(
            loc=locator,
            file_hash=file_hash,
            ext=os.path.splitext(original_filename)[1]
        )
    )


def sga_file_contents_iter(file_path):
    """
    Returns an iterator over the contents of a file located at the given file path
    """
    file_descriptor = sga_storage.open(file_path)
    return iter(partial(file_descriptor.read, BLOCK_SIZE), b'')


def file_contents_iter(file_path):
    """
    Returns an iterator over the contents of a file located at the given file path
    """
    file_descriptor = default_storage.open(file_path)
    return iter(partial(file_descriptor.read, BLOCK_SIZE), b'')
