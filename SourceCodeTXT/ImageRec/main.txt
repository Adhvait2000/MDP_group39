
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import *

app = Flask(__name__)
CORS(app)
model = load_model()

@app.route('/status', methods=['GET'])
def status():
    """
    This is a health check endpoint to check if the server is running
    :return: a json object with a key "result" and value "ok"
    """
    return jsonify({"result": "ok"})

@app.route('/image', methods=['POST'])
def image_predict():
    """
    This is the main endpoint for the image prediction algorithm
    :return: a json object with a key "result" and value a dictionary with keys "obstacle_id" and "image_id"
    """
    
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join('uploads', filename))
    
    try: 
        #for task 1, the filename is in the format "<img>_<timestamp>_<obstacle_id>.jpg"
        constituents = file.filename.split("_")
        obstacle_id = constituents[2].strip(".jpg")

    except:
        obstacle_id = "1"

    
    image_id = inference(filename,model)
    
    # Return the obstacle_id and image_id
    result = {
        "obstacle_id": obstacle_id,
        "image_id": image_id
    }
   
    return jsonify(result)

@app.route('/stitch', methods=['GET'])
def stitch():
    """
    This endpoint is for the stitching command. It will stitch all the annotated images in the runs folder
    """
    img = stitch_image()
    img.show()
    return jsonify({"result": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
