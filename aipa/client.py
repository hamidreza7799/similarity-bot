import logging
import os
from datetime import datetime

import pandas as pd
import requests


class RestClient:
    """
    handles api logging
    """
    BASE_URL = 'https://example.url.com'    # should be overridden

    def __init__(self, log_path=None, name=None):

        self.log_path = log_path
        self.name = name or 'REST'

    def _call_api(self, method, api_tag, url, **kwargs):

        logging.getLogger(self.name).info(f' {method} {api_tag}')
        full_url = url if url.startswith('http') else self.BASE_URL + url
        response = requests.request(method, full_url, **kwargs)

        self._log_to_file(method=method, url=url, tag=api_tag,
                          timestamp=str(datetime.now()),
                          duration=response.elapsed.total_seconds(),
                          response_code=response.status_code, data=kwargs.get('data', {}),
                          response=response.text[:128].encode('utf8'))
        return response

    def _log_to_file(self, **kwargs):

        data = {key: [value] for key, value in kwargs.items()}
        df = pd.DataFrame(data)

        if not os.path.isfile(self.log_path):
            df.to_csv(self.log_path, header=list(kwargs.keys()), sep='\t', index=False)
        else:
            df.to_csv(self.log_path, mode='a', header=False, sep='\t', index=False)
