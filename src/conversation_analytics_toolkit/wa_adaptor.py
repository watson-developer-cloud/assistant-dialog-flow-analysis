# (C) Copyright IBM Corp. 2019, 2020.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd

def read_logs(service, workspace_id, num_logs, log_filter=None, sort="-request_timestamp"):
    try:
        log_list=[]
        current_cursor = None
        while num_logs > 0:
            response = service.list_logs(
                workspace_id=workspace_id,
                page_limit=500,
                cursor=current_cursor,
                sort=sort,
                filter=log_filter
            ).get_result()
            min_num = min(num_logs, len(response['logs']))
            log_list.extend(response['logs'][:min_num])
            #print("\r{} logs retrieved'.format(len(log_list)), end=''")
            print("\r{} logs retrieved".format(len(log_list)))
            num_logs = num_logs - min_num
            current_cursor = None
            # Check if there is another page of logs to be fetched
            if 'pagination' in response:
                # Get the url from which logs are to fetched
                if 'next_cursor' in response['pagination']:
                    current_cursor = response['pagination']['next_cursor']
                else:
                    break
    except WatsonApiException:
        print('You\'ve reached the rate limit of log api, refer to https://www.ibm.com/watson/developercloud/assist'
              'ant/api/v1/curl.html?curl#list-logs for additional information')
    except Exception as ex:
        print(ex)
    finally:
        log_df = pd.DataFrame(log_list)
        return log_df
