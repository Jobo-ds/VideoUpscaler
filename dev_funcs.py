"""
This file has Methods for testing different results.

"""

import matplotlib as plt


"""
Frame Cleaning
"""

def compare_image(image1, image2, modifiction):
  plt.figure(figsize=(9,9))
  plt.subplot(1,2,1)
  plt.imshow(image1)
  plt.title('Orignal')
  plt.axis('off')
  plt.subplot(1,2,2)
  plt.imshow(image2)
  plt.title(str(modifiction))
  plt.axis('off')
  plt.tight_layout()
  mng = plt.get_current_fig_manager()
  mng.full_screen_toggle()
  plt.show()

def exampleClean(main_json_file):
    file_info = loadJSON(main_json_file)
    folder = file_info["folder"] + "/" + "checkpoints"
    checkpoint_number = "00000000"
    frameNr = 1
    frameNr = str(frameNr).zfill(10)
    frame_path = folder + "/" + checkpoint_number + "/" + frameNr + ".jpg"

    # Original frame
    img = cv2.imread(frame_path)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    """
    Different Types of Image Manipulation
    """

    # 2D Convolution
    # kernel = np.ones((10, 10), np.float32) / 100
    # cnv = cv2.filter2D(img, -1, kernel)
    # compare_image(img, cnv, "2D Convolution")

    # # Blur
    # blur = cv2.blur(img, (10, 10))
    # compare_image(img, blur, "Blur")

    # # Median Filtering
    # median = cv2.medianBlur(img, 5)
    # compare_image(img, median, "Median Filter")

    # Sharpening with kernel
    # kernel1 = np.array([[0, -1, 0],
    #                    [-1, 5, -1],
    #                    [0, -1, 0]])
    # kernel2 = np.array([[-1, -1, -1],
    #                    [-1, 9, -1],
    #                    [-1, -1, -1]])
    # kernel3 = np.array([[0, -1, 0],
    #                    [-1, 5, -1],
    #                    [0, -1, 0]])
    # #image_sharp = cv2.filter2D(src=img, ddepth=-1, kernel=kernel3)
    # image_sharp = cv2.bilateralFilter(src=img, d=9, sigmaColor=25, sigmaSpace=20)
    #compare_image(img, image_sharp, "Sharpened")

    #wb = cv2.xphoto.createGrayworldWB()

    #SimpleWB Implementation
    # wb = cv2.xphoto.createSimpleWB()
    # wb.setP(1)
    # wb.setOutputMax(190)

    #WB Base
    image_whitebalance = wb.balanceWhite(img)
    compare_image(img, image_whitebalance, "White Balance")




    # # Median filtering
    # median = cv2.medianBlur(noise_img, 5)
    # compare_image(noise_img, median)


"""
Upscaling Frames
"""

#Create examples of available models. BROKEN?
def modelExamples(main_json_file):
    models = os.listdir("models")
    file_info = loadJSON(main_json_file)
    folder = file_info["folder"] + "/" + "checkpoints"
    for model in models:
        i = 0
        checkpoint_number = str(i).zfill(8)
        frameNr = 1
        frame = cv2.imread(folder + "/" + checkpoint_number + "/" + str(frameNr) + ".jpg")
        scale = model[-4:-3]
        modelName = str(model[:-6]).lower()
        if not path.exists(folder + "/" + checkpoint_number + "/" + "Examples/"):
            os.makedirs(folder + "/" + checkpoint_number + "/" + "Examples/", exist_ok=False)
        # Create simple resizes for comparison
        if not path.exists(folder + "/" + checkpoint_number + "/" + "Examples/" + str(frameNr) + "-comparison-" + model[:-3] + ".jpg"):
            img = cv2.imread(folder + "/" + checkpoint_number + "/" + str(frameNr) + ".jpg", cv2.IMREAD_UNCHANGED)
            width = int(img.shape[1] * int(scale)*100 / 100)
            height = int(img.shape[0] * int(scale)*100 / 100)
            dim = (width, height)
            resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            cv2.imwrite(folder + "/" + checkpoint_number + "/" + "Examples/" + str(frameNr) + "-comparison-x" + str(scale) + ".jpg", resized_img)
        # Run Model
        print(f"Using model : {model} (x{scale})")
        sr = dnn_superres.DnnSuperResImpl_create()
        modelPath = "models/" + model
        sr.readModel(modelPath)
        sr.setModel(modelName, int(scale))
        if not path.exists(folder + "/" + checkpoint_number + "/" + "Examples/" + str(frameNr) + "-upscale-" + model[:-3] + ".jpg"):
            start = time.perf_counter()
            result = sr.upsample(frame)
            cv2.imwrite(folder + "/" + checkpoint_number + "/" + "Examples/" + str(frameNr) + "-upscale-" + model[:-3] + ".jpg", result)
            end = time.perf_counter()
            process_time = end - start
            print(f"Process time: {process_time} seconds")