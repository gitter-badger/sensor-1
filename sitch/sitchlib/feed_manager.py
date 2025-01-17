import os
import requests
import time
from datetime import datetime
from utility import Utility


class FeedManager(object):
    def __init__(self, config):
        self.mcc_list = config.mcc_list
        self.state_list = config.state_list
        self.feed_dir = config.feed_dir
        self.url_base = config.feed_url_base
        self.feed_cache = []
        self.born_on_date = datetime.now()

    def update_feed_files(self):
        all_feed_ids = self.state_list + self.mcc_list
        for feed_id in all_feed_ids:
            FeedManager.place_feed_file(self.feed_dir, self.url_base, feed_id)
        print("Feed: Finished pulling all feed files")
        return

    @classmethod
    def place_feed_file(cls, feed_dir, url_base, item_id):
        """ Retrieves and places feed files for use by the Enricher modules

        Args:
            feed_dir (str): Destination directory for feed files
            url_base (str): Base URL for hosted feed files
            item_id(str): For FCC, this is the two-letter ("CA" or "TN",
             for example), which is used in the retrieval of the feed file as
             well as the construction of the local feed file name.  For MCC this
             is the MCC, but in string form.  Not integer.

        """
        destination_file = Utility.construct_feed_file_name(feed_dir,
                                                                item_id)
        temp_file = "%s.TEMP" % destination_file
        origin_url = FeedManager.get_source_url(url_base, item_id)
        msg = "Feed: Downloading %s to %s" % (origin_url, temp_file)
        print(msg)
        response = requests.get(origin_url, stream=True)
        with open(temp_file, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)
        time.sleep(1)
        print("Feed: Moving %s to %s" % (temp_file, destination_file))
        os.rename(temp_file, destination_file)
        return

    @classmethod
    def get_source_url(cls, url_base, mcc):
        src_url = "%s/%s.csv.gz" % (url_base, mcc)
        return src_url
