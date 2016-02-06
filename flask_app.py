from flask import Flask, flash, redirect, url_for, \
                  request, render_template, send_file
import converter
import os
import io
from zipfile import ZipFile

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.debug = True


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

    msg_result = io.BytesIO()
    hsh_result = io.BytesIO()

    try:
        converter.convert(xml_source.stream, msg_source.stream, msg_result)
        msg_result.seek(0)
        hsh_result.write(converter.generate_integrity_hash(msg_result))
        msg_result.seek(0)
        hsh_result.seek(0)

        inMemoryOutputFile = io.BytesIO()
        with ZipFile(inMemoryOutputFile, 'w') as zipFile:
            zipFile.writestr("result.msg", msg_result.getvalue())
            zipFile.writestr("result.hsh", hsh_result.getvalue())

        inMemoryOutputFile.seek(0)
        return send_file(inMemoryOutputFile,
                         attachment_filename="result.zip",
                         as_attachment=True)
    except:
        flash('Error during conversion')
        return redirect(url_for('default'))
    finally:
        hsh_result.close()
        msg_result.close()

if __name__ == "__main__":
    app.run()
