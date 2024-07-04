# ROI Training Inc - Venus Document Management System
# Last Edit: 7/4/2024

import datetime
import os
import hashlib

from flask import current_app
from google.cloud import storage
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename

def upload_image_file(img):
    """
    Upload the user-uploaded file to Google Cloud Storage and retrieve its
    publicly-accessible URL.
    """
    if not img:
        return None

    public_url = storage.upload_file(
        img.read(),
        img.filename,
        img.content_type
    )

    current_app.logger.info(
        'Uploaded file %s as %s.', img.filename, public_url)

    return public_url

def _check_extension(filename, allowed_extensions):
    file, ext = os.path.splitext(filename)
    if (ext.replace('.', '').lower() not in allowed_extensions):
        raise BadRequest(
            '{0} has an invalid name or extension'.format(filename))


def _safe_filename(filename):
    """
    Generates a unique filename that is unlikely to collide with existing
    objects in Google Cloud Storage.

    ``filename.ext`` is transformed into ``filenameYYYYMMDDHHMMSS.ext`` 
    filename is then sha256 to generate a unique filename for GCS Bucket    
    """
    filename = secure_filename(filename)
    date = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    basename, extension = filename.rsplit('.', 1)
    tempname = "{0}{1}{2}".format(basename, date, extension).encode('utf-8')
    hashname = hashlib.sha256(tempname).hexdigest()
    return hashname


def upload_file(file_stream, filename, content_type):
    """
    Uploads a file to a given Cloud Storage bucket and returns the public url
    to the new object.
    """
    _check_extension(filename, current_app.config['ALLOWED_EXTENSIONS'])
    filename = _safe_filename(filename)

    bucketname = os.getenv('GOOGLE_STORAGE_BUCKET') or os.getenv(
        'GOOGLE_CLOUD_PROJECT') + '-bucket'

    client = storage.Client()
    bucket = client.bucket(bucketname)
    blob = bucket.blob(filename)

    blob.upload_from_string(
        file_stream,
        content_type=content_type)

    url = blob.public_url

    return url
