from flask import Flask, make_response, abort, redirect, request, send_from_directory, url_for
from PyPDF2 import PdfFileWriter, PdfFileReader
import qrcode
import datetime
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from logging.config import dictConfig


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s - %(levelname)s - %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
    }},
    'handlers': {
    		'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': "flask.log",
                'maxBytes': 100000000,
                'backupCount': 1
            }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['file']
    }
})

reasons = {
	"achats": 486,
	"convocation": 773,
	"enfants": 840,
	"famille": 587,
	"handicap": 638,
	"missions": 806,
	"sante": 554,
	"sport_animaux": 671,
	"travail": 388
}

app = Flask("attestation")


@app.route('/<user>/<reason>/')
def generator(user, reason):
	if user not in profiles or reason not in reasons:
		abort(404)
	pdf_name = generate_attestation(user, reason)
	return redirect(url_for('.get_pdf', file=pdf_name))

@app.route('/')
def redirection():
	u = request.args.get('profile', default="none", type=str)
	r = request.args.get('reason', default="none", type=str)
	if u not in profiles or r not in reasons:
		abort(404)
	else:
		return redirect(url_for('.generator', user=u, reason=r))

@app.route('/attestation/<file>')
def get_pdf(file):
	res = send_from_directory("attestations/", file, as_attachment=True, add_etags=False, mimetype='application/pdf',
		attachment_filename=file, cache_timeout=-1)
	res.headers["x-suggested-filename"] = file
	return res


def generate_attestation(profile, reason):
	infos = profiles[profile]

	img = Image.open("attestation.png")

	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype("/usr/share/fonts/truetype/arial.ttf", 15, layout_engine=ImageFont.LAYOUT_BASIC)
	draw.text((130, 178), '%s %s' % (infos['firstname'], infos['lastname']), (0, 0, 0), font=font)
	draw.text((130, 204), infos['birthday'], (0, 0, 0), font=font)
	draw.text((301, 204), infos['placeofbirth'], (0, 0, 0), font=font)
	draw.text((150, 230), "%s %s %s" % (infos['address'], infos['zipcode'], infos['city']), (0, 0, 0), font=font)
	draw.text((111, 1049), infos['city'], (0, 0, 0), font=font)
	draw.text((64, reasons[reason]), "X", (0, 0, 0), font=font)

	date = datetime.datetime.now()
	
	draw.text((92, 1075), date.strftime("%d/%m/%Y"), (0, 0, 0), font=font)
	draw.text((319, 1075), date.strftime("%H:%M"), (0, 0, 0), font=font)

	qr_text = ';\n '.join([
		'Cree le: %s a %s' % (date.strftime("%d/%m/%Y"), date.strftime("%Hh%M")),
		'Nom: %s' % infos['lastname'],
		'Prenom: %s' % infos['firstname'],
		'Naissance: %s a %s' % (infos['birthday'], infos['placeofbirth']),
		'Adresse: %s %s %s' % (infos['address'], infos['zipcode'], infos['city']),
		'Sortie: %s a %s' % (date.strftime("%d/%m/%Y"), date.strftime("%H:%M")),
		'Motifs: %s;\n' % reason
	])

	qr = qrcode.make(qr_text, border=0)
	qr = qr.resize((130, 130))
	img.paste(qr, (611, 1008))

	plt.imsave("output-1.pdf", np.array(img), format="pdf")

	img = Image.open("white-page.png")
	qr = qrcode.make(qr_text, border=0)
	qr = qr.resize((350, 350))
	img.paste(qr, (76, 76))

	plt.imsave("output-2.pdf", np.array(img), format="pdf")

	pdf1 = PdfFileReader('output-1.pdf')
	pdf2 = PdfFileReader('output-2.pdf')
	writer = PdfFileWriter()
	writer.addPage(pdf1.getPage(0))
	writer.addPage(pdf2.getPage(0))
	
	pdf_name = "attestation-%s-%s_%s.pdf" % (profile, date.strftime("%d_%m_%Y"), date.strftime("%Hh%M"))
	writer.write(open("attestations/%s" % pdf_name, "wb"))
	os.remove("output-1.pdf")
	os.remove("output-2.pdf")

	return pdf_name


if __name__ == '__main__':
	with open("profiles.json", "r") as f:
		profiles = json.load(f)

	if not os.path.exists('attestations/'):
		os.makedirs('attestations/')

	app.run(host='0.0.0.0', port=1234)
