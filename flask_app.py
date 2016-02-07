from flask import Flask, flash, redirect, url_for, \
                  request, render_template, send_file
from os import path, urandom
from io import BytesIO
from zipfile import ZipFile

import converter


app = Flask(__name__)
app.secret_key = urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.debug = False


@app.route('/')
def default():
    return render_template('index.html',
                           max_file_size=app.config['MAX_CONTENT_LENGTH'])


@app.route('/convert', methods=['POST'])
def convert():
    xml_source = request.files['xmlFile']
    msg_source = request.files['msgFile']

    if xml_source.filename == '' or msg_source.filename == '':
        flash('Please upload valid Xml and Msg files')
        return redirect(url_for('default'))

    msg_result = BytesIO()
    hsh_result = BytesIO()

    try:
        converter.convert(xml_source.stream, msg_source.stream, msg_result)

        msg_result.seek(0)
        hsh_result.write(converter.generate_integrity_hash(msg_result))

        msg_result.seek(0)
        hsh_result.seek(0)
        zip_stream = generate_zipfile(msg_result.getvalue(),
                                      hsh_result.getvalue(),
                                      'result')
        return send_file(zip_stream,
                         attachment_filename='result.zip',
                         as_attachment=True)
    except Exception as ex:
        flash(type(ex).__name__ + ' - ' + str(ex.args))
        return redirect(url_for('default'))


@app.route('/createchecksum', methods=['POST'])
def createchecksum():
    msg_source = request.files['msgFile']

    if msg_source.filename == '':
        flash('Please upload valid Msg file')
        return redirect(url_for('default'))

    hsh_result = BytesIO()

    try:
        hsh_result.write(converter.generate_integrity_hash(msg_source.stream))
        hsh_result.seek(0)

        name, _ = path.splitext(msg_source.filename)
        return send_file(hsh_result,
                         attachment_filename=name + '.hsh',
                         as_attachment=True)
    except Exception as ex:
        flash(type(ex).__name__ + ' - ' + str(ex.args))
        return redirect(url_for('default'))


def generate_zipfile(msg_content, hsh_content, filename):
    zip_stream = BytesIO()
    with ZipFile(zip_stream, 'w') as zip_file:
        zip_file.writestr(filename + '.msg', msg_content)
        zip_file.writestr(filename + '.hsh', hsh_content)

    zip_stream.seek(0)
    return zip_stream


if __name__ == '__main__':
    app.run()
