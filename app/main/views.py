from flask import request, render_template, flash, session
from io import BytesIO
import requests
import json
from . import main
from .forms import ModelResultsForm, ScattererForm, UploadForm
from .. import host_utils

host = host_utils.host


@main.route("/deletemodel/<model_id>", methods=['DELETE'])
def delete_model(model_id):
    delete_url = '{}/models?model_id={}'.format(host, model_id)
    requests.delete(delete_url)
    return "Model removed succesfully!"


@main.route("/models", methods=['GET'])
def get_models():
    data = requests.get('{}/models'.format(host)).content
    data = json.loads(data)
    return render_template('models.html', data=data, host=host)


@main.route("/deletemodelresult/<model_result_id>", methods=['DELETE'])
def delete_model_result(model_result_id):
    print('Deleting model result {}'.format(model_result_id))
    delete_url = '{}/modelresult?model_result_id={}'.format(host, model_result_id)
    requests.delete(delete_url)
    return "Model results removed succesfully!"


@main.route("/modelresults/", methods=['GET', 'POST'])
def get_models_result():
    form = ModelResultsForm()
    model_id = request.args.get("model_id")
    data = requests.get('{}/models'.format(host)).content
    data = json.loads(data)
    form.model_names_list.choices = [(m['id'], m['model_name']) for m in data]

    if request.method == 'POST':
        model_id = form.model_names_list.data
        model_results = requests.get('{}/modelresult?model_id={}'.format(host, model_id)).content
    else:
        if model_id is not None:
            form.model_names_list.data = model_id
            model_results = requests.get('{}/modelresult?model_id={}'.format(host, model_id)).content
        else:
            model_results = requests.get('{}/modelresult?'.format(host)).content

    data = json.loads(model_results)
    return render_template('modelresults.html', form=form, data=json.loads(data), host=host)


@main.route("/scatterer", methods=['GET', 'POST'])
def scatterer():
    form = ScattererForm()
    data = requests.get('{}/models'.format(host)).content
    data = json.loads(data)
    form.model_names_list.choices = [(i, m['model_name']) for i, m in enumerate(data)]
    figure = None
    if request.method == 'POST' and form.validate_on_submit():
        model_info = data[form.model_names_list.data]
        session['Radius'] = form.radius.data
        session['LongitudinalSpeed'] = form.longitudinal.data
        session['TransverseSpeed'] = form.transverse.data
        session['DensityOfScatterer'] = form.density_of_scatter.data
        session['Frequency'] = json.loads(model_info['params'])['frequency']
        session['SpeedOfSound'] = json.loads(model_info['params'])['speed_of_sound']
        session['DensityOfMedium'] = json.loads(model_info['params'])['density_of_medium']
        session['Type'] = form.type_value.data
        session['From'] = form.from_value.data
        session['To'] = form.to_value.data
        session['Step'] = form.step.data
        session['Dx'] = json.loads(model_info['params'])['dx']
        session['ModelPath'] = 'models/{}.mat'.format(model_info['model_name'])
        session['ModelName'] = model_info['id']
        url = '{}/scatterer'.format(host)
        headers = {
            'cache-control': "no-cache",
        }
        data = {
            'Radius': session['Radius'],
            'LongitudinalSpeed': session['LongitudinalSpeed'],
            'TransverseSpeed': session['TransverseSpeed'],
            'DensityOfScatterer': session['DensityOfScatterer'],
            'Frequency': session['Frequency'],
            'SpeedOfSound': session['SpeedOfSound'],
            'DensityOfMedium': session['DensityOfMedium'],
            'Dx': session['Dx'],
            'Type': session['Type'],
            'From': session['From'],
            'To': session['To'],
            'Step': session['Step'],
            'ModelPath': session['ModelPath'],
            'ModelName': session['ModelName']
        }
        r = requests.post(url, headers=headers, data=data)
        if r.status_code != 200 and r.status_code != 201:
            flash_errors(form)
        else:
            figure = json.loads(r.content)['figure']
            print(figure)
            # figure = r.content.decode('ascii').replace('"', '')

        form.radius.data = None
        form.longitudinal.data = None
        form.transverse.data = None
        form.density_of_scatter.data = None
        form.type_value.data = None
        form.from_value.data = None
        form.to_value.data = None
        form.step.data = None

    return render_template('scatterer.html', form=form, figure=figure, data=data)


@main.route("/loadmodel", methods=['GET', 'POST'])
def modelfield():
    form = UploadForm()
    figure = None
    if request.method == 'POST' and form.validate_on_submit():
        file_bytes = request.files['input_file'].read()
        session['dx'] = form.dxvalue.data
        session['frequency'] = form.frequency.data
        session['speed_of_sound'] = form.speed_of_sound.data
        session['density_of_medium'] = form.density_of_medium.data
        session['model_name'] = form.model_name.data

        url = '{}/savemodel'.format(host)
        headers = {
            'cache-control': "no-cache",
        }
        data = {
            'ModelName': session['model_name'],
            'Dx': session['dx'],
            'Frequency': session['frequency'],
            'SpeedOfSound': session['speed_of_sound'],
            'DensityOfMedium': session['density_of_medium']
        }
        files = {
            'ModelFile': file_bytes
        }
        r = requests.post(url, headers=headers, data=data, files=files)
        if r.status_code != 200 and r.status_code != 201:
            flash('Exception occurred {}'.format(r.content), 'error')
        else:
            print(r.content)
            figure = json.loads(r.content)['figure']
            flash('Model {}  successfully loaded!'.format(session['model_name']), 'info')
    else:
        flash_errors(form)

    request.files = None
    form.dxvalue.data = None
    form.input_file.data = None
    form.model_name.data = None

    return render_template('loadmodel.html', form=form, figure=figure)


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')


@main.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')