# Motion Detector
Motion Detection using OpenCV and Python
The trivial idea is to compute the difference between two frames apply a threshold the separate pixels that have changed from the others and then count all the black pixels. Then the average is calculated with this count and the total number of pixels and depending of the ceil the event is triggered or not.

Additional informations:

initRecorder: initialise the recorder with an arbitrary codec it can be changed with problems
in the run method no motion can be detected in the first 5 second because it is almost the time needed for the webcam to adjust the focus and the luminosity which imply lot's of changes on the image
processImage: contains all the images operations applied to the image
somethingHasMoved: The image iteration to count black pixels is contained in this method
