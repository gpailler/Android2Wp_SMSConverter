# coding: utf-8

import argparse
import datetime
from lxml import etree
import logging
import os
import re

import base64
from Crypto.Cipher import AES
import hashlib
import uuid

from thirdparty import filetimes
from thirdparty import pkcs7

VERSION = '1.1'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def convert(xml, msg, result):
    input_android = etree.parse(xml)
    input_wp = etree.parse(msg)
    input_wp_root = input_wp.getroot()

    smses = input_android.xpath("/smses/sms")
    logger.info('{} SMS to convert'.format(len(smses)))
    for sms in smses:
        address = sms.get('address')
        date = sms.get('date')
        type = sms.get('type')  # 1 = received / 2 = sent
        body = sms.get('body')

        append_message(input_wp_root, address, date, type, body)

    input_wp.write(result,
                   encoding='utf-8',
                   pretty_print=True,
                   xml_declaration=True)
    logger.info('SMS converted')


def append_message(root, address, date, type, text):
    message = etree.Element('Message')
    recepients = etree.SubElement(message, 'Recepients')
    sender = etree.SubElement(message, 'Sender')
    if type == '1':
        sender.text = re.sub(r'[\s-]+', '', address, flags=re.UNICODE)
    else:
        recepientsstring = etree.SubElement(recepients, 'string')
        recepientsstring.text = address.strip()
    body = etree.SubElement(message, 'Body')
    body.text = text
    isincoming = etree.SubElement(message, 'IsIncoming')
    if type == '1':
        isincoming.text = 'true'
    elif type == '2':
        isincoming.text = 'false'

    etree.SubElement(message, 'IsRead').text = 'true'
    etree.SubElement(message, 'Attachments')

    timestamp = etree.SubElement(message, 'LocalTimestamp')
    input_timestamp = datetime.datetime.fromtimestamp(int(date[:-3]))
    timestamp.text = str(filetimes.dt_to_filetime(input_timestamp))

    root.append(message)


def create_checksum_file(result_file):
    file, ext = os.path.splitext(result_file.name)
    hshfile = file + '.hsh'
    with open(hshfile, 'wb') as f:
        logger.info('Writing checksum file {}'.format(f.name))
        f.write(generate_integrity_hash(result_file))


def generate_integrity_hash(file):
    hash = hashlib.sha256(file.read())
    hash_b64 = base64.b64encode(hash.digest())
    hash_b64 = pkcs7.encode(hash_b64)

    key = uuid.UUID('{D86B2FDE-C318-4DD2-8C9E-EB3F1A244DF8}')
    iv = uuid.UUID('{089B6AEC-E81D-49AC-91DF-AD071418E7A3}')

    encryptor = AES.new(key.bytes_le, AES.MODE_CBC, IV=iv.bytes_le)
    cipher = encryptor.encrypt(hash_b64)
    cipher_b64 = base64.b64encode(cipher)
    return cipher_b64


if __name__ == '__main__':
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    logger.addHandler(steam_handler)

    parser = argparse.ArgumentParser(
        description='Convert SMS from Android (SMS Backup&Restore app) '
                    'to Windows Phone (contact+message backup) or compute '
                    'checksum file for Windows Phone .msg file.',
        epilog='Visit https://github.com/gpailler/Android2Wp_SMSConverter '
               'for details')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(VERSION))
    subparsers = parser.add_subparsers(dest='action')

    # Options for conversion
    parser_convert = subparsers.add_parser('convert',
        help='Convert SMS from Android (SMS Backup&Restore app) '
             'to Windows Phone (contact+message backup)')
    parser_convert.add_argument('--xml',
                        help='Android XML file',
                        required=True,
                        type=argparse.FileType('rb'))
    parser_convert.add_argument('--msg',
                        help='Windows Phone MSG file',
                        required=True,
                        type=argparse.FileType('rb'))
    parser_convert.add_argument('--out',
                        help='Result file (default: %(default)s)',
                        default='result.msg',
                        type=argparse.FileType('w+b'))

    # Options for checksum generation
    parser_checksum = subparsers.add_parser('createchecksum',
        help='Compute .hsh checksum file from .msg file')
    parser_checksum.add_argument('--msg',
                        help='Windows Phone MSG file',
                        required=True,
                        type=argparse.FileType('rb'))

    args = parser.parse_args()

    if args.action == 'convert':
        _, ext = os.path.splitext(args.out.name)
        if ext.lower() == '.msg':
            logger.info('Merge {} and {} into {}'.format(
                        args.xml.name, args.msg.name, args.out.name))
            convert(args.xml, args.msg, args.out)
            args.out.seek(0)

            logger.info('Create checksum file for {}'.format(args.out.name))
            create_checksum_file(args.out)

            logger.info('Conversion done')
        else:
            parser.error('result file must have .msg extension')
    elif args.action == 'createchecksum':
        logger.info('Create checksum file for {}'.format(args.msg.name))
        create_checksum_file(args.msg)
        logger.info('Checksum created')
