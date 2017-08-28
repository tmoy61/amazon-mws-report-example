# amazon-mws-report-example

Sample code to request and retrieve a report from Amazon's
Marketplace Web Services (MWS) API.

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

If you get this AssertionError in MWS:
   assert content_md5(body) == digest

add this patch to boto/mws/connection.py
https://github.com/boto/boto/pull/3707/files
