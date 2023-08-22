

from flask import Flask, render_template, request
from googleapiclient import discovery

app = Flask(__name__)
API_KEY = ''
disc_url = ""
client = discovery.build(
      "commentanalyzer",
      "v1alpha1",
      developerKey=API_KEY,
      discoveryServiceUrl= disc_url
    )


@app.route('/', methods=['GET', 'POST'])
def translate(gcf_request=None):
    """
    main handler - show form and possibly previous translation
    """

    # Flask Request object passed in for Cloud Functions
    # (use gcf_request for GCF but flask.request otherwise)
    local_request = gcf_request if gcf_request else request

    # reset all variables (GET/POST)
    text = toxicity = None

    # form submission and if there is data to process (POST)
    if local_request.method == 'POST':
        text = local_request.form['text'].strip()
        if text:
            analyze_request = {
            'comment': { 'text': text },
            'requestedAttributes': {'TOXICITY': {}},'languages':['en']
        }
            toxicity = client.comments().analyze(body=analyze_request).execute()

    # create context & render template
    if toxicity == None:
        context = {
        'orig':  {'text': text, 'lc': 'Source Text'},
        'trans': {'text': toxicity, 'lc': 'Toxicity score'},
    }
    else:    
        context = {
            'orig':  {'text': text, 'lc': 'Source Text'},
            'trans': {'text': toxicity['attributeScores']['TOXICITY']['spanScores'][0]['score']['value'], 'lc': 'Toxicity score'},
        }
    return render_template('index.html', **context)


if __name__ == '__main__':
    import os
    app.run(debug=True, threaded=True, host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
