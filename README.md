# Sleepy-Joe
Flask app infrastructure for sleep contest


 - For this repo, create your own branch, and [submit a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)
 - Format your doc strings [according to Google](http://google.github.io/styleguide/pyguide.html)
 - Ruben has a flask project online [here](http://ranc-aws-env.arz8dufmi3.us-east-2.elasticbeanstalk.com/0. Let him know if you want to look behind the curtain/at the code base.

Work Items:

 - Flask infrastructure
   - Bootstrap frontend/Jinja2
 - Helper Library for storing FitBit Historical Sleep Data in `postgresql`
   - Helper Library for getting FitBit data
 - Figure out OAuth 2.0 Sever-to-Sever token exchange.
   - Store tokens in `postgresql` OR use AWS KMS
 - Single Person Sleep Stat View (Bokeh Plots
 - Multi Person Sleep Stat View (Contest)
 - Figure out AWS for collborating on single project across accounts
 - Sphinx docs
 - Unit-tests