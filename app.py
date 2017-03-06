from flask import Flask, render_template, request, redirect
from twython import Twython, TwythonError
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.charts import Bar, output_file, show


import json
import pandas 
import time
import numpy
import csv
import re
import operator

app = Flask(__name__)

app.vars={}

##### This is the result page
@app.route('/relate',methods=['GET','POST'])
def relate():
        ##### request was a POST
        app.vars['hashtag'] = request.form['hashtag']
        
        # Here is the code from jupyter
        #
        # Twitter keys
        CONSUMER_KEY = 'P048GUC2C0g0CIs4S0hUuU1Wq'
        CONSUMER_SECRET = 'GiD2pvtlYa2HyZOqWdh5SH81YsrXbgtfXhtjAGfiWaYFQSLRdE'
        OAUTH_TOKEN = '92925384-gJEnzPCiYOiF5ZpOWT6fNboIjnUe9GRuAtZuJfN4O'
        OAUTH_TOKEN_SECRET = '4mIHev3GIfeaiVDVilHaM2z815vg61HMPEXgbrLmZVcCH'
        # Connect to the Twiter API
        twitter_api = Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        # Find the hashtag from request.form
        hashtag ='#' + app.vars['hashtag']
        count = 500
        search_results = twitter_api.search(q=hashtag, count=count)
        all_tweets = search_results['statuses']
        # Find all hashtag words, and formulate into a list
        all_hash_word = []
        for tweet in all_tweets:
            all_hash_word.append(re.findall(r'#\w*', tweet['text']))

        all_hash_string = []
        for line in all_hash_word:
            all_hash_string.append(''.join(line))

        myString = " ".join(all_hash_string)
        all_hash_list = myString.split('#')
        all_hash_list = [x.strip(' ') for x in all_hash_list]
        # convert to all lower cases
        all_hash_list = [x.lower() for x in all_hash_list]
        # make hashword list into a dictionary with word and the frequency of word
        word_dict = {}
        for word in all_hash_list:
            if word in word_dict:
                word_dict[word] += 1
            else:
                word_dict[word] = 1
        word_dict = sorted(word_dict.items(), key=operator.itemgetter(1), reverse=True)
        # pretend pandas is useful at this point
        word_pd = pandas.DataFrame(word_dict)
        word_pd.columns = ['Hashword', 'Count']
        word_pd_plot = word_pd[1:30]
        
        fig = Bar(word_pd_plot, 'Hashword', values='Count', title="Relatable Hashwords Count",  
            legend="top_right", plot_width=1000, plot_height=600)
        fig.xaxis.axis_label_text_font_size = '25pt'
        ##### see if this works
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()
        script, div = components(fig)
        html = render_template(
                'relatable.html',
                plot_script=script,
                plot_div=div,
                js_resources=js_resources,
                css_resources=css_resources,
                hashtag = hashtag
                )

        ##### retern a template with two vars mySTring and word_pd_plot
        return encode_utf8(html)


##########This is the question page
# don't need change this
@app.route('/')
def index():
     return render_template('index.html')

    

if __name__ == "__main__":
    app.run(port=33507)


