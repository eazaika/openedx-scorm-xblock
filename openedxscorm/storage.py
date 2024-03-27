"""
Storage backend for scorm metadata export.
"""
import os
from django.conf import settings

from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage


class S3ScormStorage(S3BotoStorage):
    """
    S3 backend for scorm metadata export
    """
    def __init__(self, xblock, bucket, querystring_auth, querystring_expire):
        self.xblock = xblock
        self.custom_domain = None

        super(S3ScormStorage, self).__init__(bucket=bucket, querystring_auth=querystring_auth,
                         querystring_expire=querystring_expire)

    def url(self, name, parameters=None, expire=None):
        """
        Override url method of S3BotoStorage
        """
        # No need to use assets proxy when authentication is disabled
        if not self.querystring_auth:
            return super(S3ScormStorage, self).url(name, parameters, expire)

        if name.startswith(self.xblock.extract_folder_path):
            # remove trailing '?' if it's present
            handler_url = self.xblock.runtime.handler_url(self.xblock, 'assets_proxy').rstrip("?/")

            # construct the URL for proxy function
            return "{}/{}".format(handler_url, self.xblock.index_page_path)

        # This branch is executed when the `url` method is called from `assets_proxy`
        return super(S3ScormStorage, self).url(os.path.join(self.xblock.extract_folder_path, name), parameters, expire)

def s3(xblock):
    """
    Creates and returns an instance of the S3ScormStorage class.

    This function takes an xblock instance as its argument and returns an instance
    of the S3ScormStorage class. The S3ScormStorage class is defined in the
    'openedxscorm.storage' module and provides storage functionality specific to
    SCORM XBlock.

    Args:
        xblock (XBlock): An instance of the SCORM XBlock.

    Returns:
        S3ScormStorage: An instance of the S3ScormStorage class.
    """
    bucket = xblock.xblock_settings.get('S3_BUCKET_NAME', settings.AWS_STORAGE_BUCKET_NAME)
    querystring_auth = xblock.xblock_settings.get('S3_QUERY_AUTH', True)
    querystring_expire = xblock.xblock_settings.get('S3_EXPIRES_IN', 604800)
    storage_class = get_storage_class('openedxscorm.storage.S3ScormStorage')
    return storage_class(xblock=xblock, bucket=bucket,
                         querystring_auth=querystring_auth,
                         querystring_expire=querystring_expire)
