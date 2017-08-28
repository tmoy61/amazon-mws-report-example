'''
Todd Moyer
2017 Aug 23

This code isn't polished or production ready, but at least it gets you started.
Amazon MWS has a bit of a learning curve.  Hopefully this will help 
get you going.

Many thanks to Mike Lin for the code that got me started.
https://gist.github.com/mmlin/944fda9a466006a0c93726006991dd88

This code may run for a few minutes.  It takes a while for MWS to create
the report.

MWS API docs at 
https://docs.developer.amazonservices.com/en_US/reports/Reports_Overview.html
MWS Scratchpad at 
https://mws.amazonservices.com/scratchpad/index.html
Boto docs at 
http://docs.pythonboto.org/en/latest/ref/mws.html?#module-boto.mws

THIS CODE COMES WITH NO WARANTEE OR GUARENTEE OF ANY KIND.
USE IT AT YOUR OWN RISK.
'''

# -*- coding: utf-8 -*-

import sys
import time

from boto.mws.connection import MWSConnection

# ********************** Fill in your credentials. **************************
SELLER_ID	= 'add yours here'
ACCESS_KEY	= 'add yours here'
SECRET_KEY	= 'add yours here'

MARKETPLACE_IDS	= {
    'CA':	'add yours here'
    'MX':	'add yours here'
    'US':	'add yours here'
    }

# Provide your credentials.
conn = MWSConnection(
    Merchant			= SELLER_ID,
    aws_access_key_id		= ACCESS_KEY,
    aws_secret_access_key	= SECRET_KEY,
)

# ********************** Adjust dates.  **************************
# Request report.
# Adjust dates so you get some data but not too much.
# Report types documented here.
# https://docs.developer.amazonservices.com/en_US/reports/Reports_ReportType.html
rptReq = conn.request_report(
    ReportType		= '_GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_',
    # Adjust as necessary  StartDate		= '2017-08-01T10:00:00Z',
    # Adjust as necessary  EndDate		= '2017-08-01T11:00:00Z',
    MarketplaceIdList	= [MARKETPLACE_IDS['US']],
)
reqId	= rptReq.RequestReportResult.ReportRequestInfo.ReportRequestId
reqStat	= rptReq.RequestReportResult.ReportRequestInfo.ReportProcessingStatus
print("Rpt Request ID:", reqId, "Status:", reqStat)
if reqStat != '_SUBMITTED_':
    sys.stderr.write("Received unexpected status when requesting report:",
                     reqStat)
    sys.stderr.write("Expected '_SUBMITTED_'")
    sys.exit(1)

# Wait until report is ready.
# Avoid over-polling that would trigger throttling.
# Poll twice a minute for 5 minutes.
rptId	= None
for x in range(10):
    time.sleep(30)
    rptStatResp = conn.get_report_request_list(
        ReportRequestIdList	= [reqId]
    )
    rptReqInfo	= rptStatResp.GetReportRequestListResult.ReportRequestInfo[0]
    if not (hasattr(rptReqInfo, 'ReportProcessingStatus')):
        sys.stderr.write("Report status request does not contain",
                         "the expected 'ReportProcessingStatus'")
        sys.exit(2)
    rptStat	= rptReqInfo.ReportProcessingStatus

    # Report still running.  Continue to wait.
    if rptStat in ('_SUBMITTED_', '_IN_PROGRESS_'):
        print("Report still running with status", rptStat)
        continue
    
    # Report finished with an error or has an unknown status.
    if rptStat != '_DONE_':
        sys.stderr.write("Report shows an error or unknown status of '{0}'".format(rptStat))
        sys.exit(3)

    # Report finished successfully.
    if not (hasattr(rptReqInfo, 'GeneratedReportId')):
        sys.stderr.write("Report status request does not contain",
                         "the expected 'GeneratedReportId'")
        sys.exit(4)
    rptId	= rptReqInfo.GeneratedReportId
    print("Report completed with ID", rptId)
    break

if rptId is None:
        sys.stderr.write("Report timed out after 5 minutes.")
        sys.exit(5)

# Fetch and process the report.
rptResp = conn.get_report(
    ReportId	= rptId
)
# Report is bytes, not str.
# Have to be careful converting because weird chars like degree sign.
rptTxt		= rptResp.decode(errors='ignore')
fldNames	= None
# Lines terminated with "\r\n".
# Hopefully that is consistent across all platforms.
for rec in rptTxt.split(sep="\r\n"):
    # print(repr(rec), '|')

    # Since using end-of-line as *separator*, will get trailing empty line.
    # Ignore it.
    if len(rec) < 2:
        continue
    
    # Get header from first line
    if fldNames is None:
        fldNames	= rec.split(sep="\t")
        # Last column name may have extra whitespace.  Remove it.
        fldNames[-1]	= fldNames[-1].strip()
        continue

    # Create a dict using the column names as keys.
    vals = rec.split(sep="\t")
    order = dict(zip(fldNames, vals))
    print("---------------------------\n", order)

