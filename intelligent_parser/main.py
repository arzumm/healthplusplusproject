import os
import io
import sys
import cv2
import numpy as np
from PIL import Image

from flask import Flask, redirect, render_template, request, jsonify

from google.cloud import firestore
from google.cloud import storage
from google.cloud import vision

app = Flask(__name__)
MAX_FEATURES = 1000
GOOD_MATCH_PERCENTAGE = 0.20
ref = None

#calculates and applies homography
def alignImages(image, reference):
	#get grayscale
	imgG = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	refG = cv2.cvtColor(reference, cv2.COLOR_BGR2GRAY)

	#apply ORB for features and descriptors
	orb = cv2.ORB_create(MAX_FEATURES)
	imgKeyPoints, imgDescriptors = orb.detectAndCompute(imgG, None)
	refKeyPoints, refDescriptors = orb.detectAndCompute(refG, None)

	#match features from image to reference
	matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
	matches = matcher.match(imgDescriptors, refDescriptors, None)

	#sort matches by score for filtering
	matches.sort(key=lambda x: x.distance, reverse=False)
	goodMatcheTotal = int(len(matches) * GOOD_MATCH_PERCENTAGE)
	matches = matches[:goodMatcheTotal]

	#draw top matches of reference points
	topMatches = cv2.drawMatches(image, imgKeyPoints, reference, refKeyPoints, matches, None)

	#Gather coords for best matches
	imgPoints = np.zeros((len(matches), 2), dtype = np.float32)
	refPoints = np.zeros((len(matches), 2), dtype = np.float32)

	for i, match in enumerate(matches):
		imgPoints[i, :] = imgKeyPoints[match.queryIdx].pt
		refPoints[i, :] = refKeyPoints[match.trainIdx].pt

	#calculate homography
	homography, mask = cv2.findHomography(imgPoints, refPoints, cv2.RANSAC)

	#apply homography
	height, width, channels = image.shape

	#frame = np.float32([[0,0], [0,height], [width,height], [width, 0]]).reshape(-1,1,2)
	#result = cv2.perspectiveTransform(frame, homography)

	result = cv2.warpPerspective(image, homography, (width, height))


	return result, homography

#calls align images, crops result, returns resulting image
def getAlignedImage(image, reference):
	#align image
	result, homography = alignImages(image, reference)

	#gather width, height of resulting shape
	height, width, channels = reference.shape
	
	#get contours
	imgG = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(src = imgG, ksize = (5,5), sigmaX = 0)
	t, binary = cv2.threshold(src = blur,thresh = 127, maxval = 255, type = cv2.THRESH_BINARY)
	contours, _ = cv2.findContours(image = binary, mode = cv2.RETR_EXTERNAL, method = cv2.CHAIN_APPROX_SIMPLE)

	#update bounding rectangles
	cornerMinX = 0
	cornerMinY = 0
	for c in contours:
		x, y, w, h = cv2.boundingRect(c)
		
		cornerMinX = x
		cornerMinY = y

	#crop the image
	crop = result[cornerMinY:cornerMinY+height, cornerMinX:cornerMinX+width]

	return crop

@app.route('/restart')
def restart():
    global ref

    def delete_collection(coll_ref, batch_size):
        docs = coll_ref.limit(batch_size).get()
        deleted = 0

        for doc in docs:
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batch_size:
            return delete_collection(coll_ref, batch_size)

    delete_collection(firestore.Client().collection(u'photos'), 1)
    delete_collection(firestore.Client().collection(u'templates'), 1)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ.get('CLOUD_STORAGE_BUCKET'))
    blobs = bucket.list_blobs()
    bucket.delete_blobs(blobs)
    ref = None
    return render_template('homepage.html')

@app.route('/template', methods=['POST'])
def template():
    global ref

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ.get('CLOUD_STORAGE_BUCKET'))
    photo = request.files['pic']
    ref = photo.filename
    blob = bucket.blob(photo.filename)
    blob.upload_from_string(photo.read(), content_type=photo.content_type)
    blob.make_public()
    return render_template('homepage.html')

@app.route('/templateMeta', methods=['POST'])
def templateMeta():
    json = request.json
    firestore_client = firestore.Client()
    doc_ref = firestore_client.collection(u'photos').document(ref)
    doc_ref.set(json)

    sqs = doc_ref.get().get('params')

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ.get('CLOUD_STORAGE_BUCKET'))
    blob = bucket.blob(ref)
    with io.BytesIO() as out:
        blob.download_to_file(out)
        inside = out.getvalue()
    nparr = np.fromstring(inside, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    nparr = np.asarray(img)
    #cv2.imwrite("ori" + ref, nparr) #debug
    vision_client = vision.ImageAnnotatorClient()
    data = {}

    for sq in sqs:
        image_obj = Image.fromarray(nparr)
        cropped_image = image_obj.crop(map(int, sqs[sq].split(",")))
        arr = np.asarray(cropped_image)
        #cv2.imwrite(sq + ref, arr) #debug
        contents = cv2.imencode('.jpg', arr)[1].tostring()
        image = vision.types.Image(content=contents)
        response = vision_client.document_text_detection(image=image)
        data[sq] = response.full_text_annotation.text.replace("\n", "")
    results = doc_ref.get().get('results')
    results[ref] = data
    doc_ref.update({'results': results}) 
    return render_template('homepage.html')

@app.route('/newpic', methods=['POST'])
def newpic():
    firestore_client = firestore.Client()
    doc_ref = firestore_client.collection(u'photos').document(ref)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(os.environ.get('CLOUD_STORAGE_BUCKET'))
    photo = request.files['pic']
    blob = bucket.blob(ref)
    with io.BytesIO() as out:
        blob.download_to_file(out)
        inside = out.getvalue()
        refer = np.fromstring(inside, np.uint8)
        reference = cv2.imdecode(refer, cv2.IMREAD_COLOR)
    nparr = np.fromstring(photo.read(), np.uint8)
    new = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    result = getAlignedImage(new, reference)
    #cv2.imwrite("aligned" + photo.filename, result) #debug
    vision_client = vision.ImageAnnotatorClient()
    sqs = doc_ref.get().get('params')
    data = {}

    for sq in sqs:
        im = Image.fromarray(result)
        cropped_image = im.crop(map(int, sqs[sq].split(",")))
        arr = np.asarray(cropped_image)
        #cv2.imwrite(sq + photo.filename, arr) #debug
        cropped_image = cv2.imencode('.jpg', arr)[1].tostring()
        image = vision.types.Image(content=cropped_image)
        response = vision_client.document_text_detection(image=image)
        data[sq] = response.full_text_annotation.text.replace("\n", "")
    results = doc_ref.get().get('results')
    results[photo.filename] = data
    doc_ref.update({'results': results}) 
    return render_template('homepage.html')

@app.route('/getdata')
def getdata():
    firestore_client = firestore.Client()
    doc_ref = firestore_client.collection(u'photos').document(ref)
    ret = doc_ref.get().get('results')
    return jsonify(ret)

@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    
    # Create a Cloud Storage client.
    storage_client = storage.Client()

    # Get the Cloud Storage bucket that the file will be uploaded to.
    bucket = storage_client.get_bucket(os.environ.get('CLOUD_STORAGE_BUCKET'))

    # Create a new blob and upload the file's content to Cloud Storage.
    photo = request.files['file']
    blob = bucket.blob(photo.filename)
    blob.upload_from_string(
            photo.read(), content_type=photo.content_type)

    # Make the blob publicly viewable.
    blob.make_public()
    image_public_url = blob.public_url
    
    # Create a Cloud Vision client.
    vision_client = vision.ImageAnnotatorClient()

    # Retrieve a Vision API response for the photo stored in Cloud Storage
    image = vision.types.Image()
    image.source.image_uri = 'gs://{}/{}'.format(os.environ.get('CLOUD_STORAGE_BUCKET'), blob.name)
    
    response = vision_client.annotate_image({'image': image})
    labels = response.label_annotations
    faces = response.face_annotations
    web_entities = response.web_detection.web_entities

    # Create a Cloud Firestore client
    firestore_client = firestore.Client()

    # Get a reference to the document we will upload to
    doc_ref = firestore_client.collection(u'photos').document(blob.name)

    # Note: If we are using Python version 2, we need to convert
    # our image URL to unicode to save it to Cloud Firestore properly.
    if sys.version_info < (3, 0):
        image_public_url = unicode(image_public_url, "utf-8")

    # Construct key/value pairs with data
    data = {
        u'image_public_url': image_public_url,
        u'top_label': labels[0].description
    }

    # Set the document with the data
    doc_ref.set(data)

    # Redirect to the home page.
    return render_template('homepage.html', labels=labels, faces=faces, web_entities=web_entities, image_public_url=image_public_url)


@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
