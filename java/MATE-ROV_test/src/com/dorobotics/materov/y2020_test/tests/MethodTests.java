package com.dorobotics.materov.y2020_test.tests;

import java.util.ArrayList;
import java.util.List;

import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.MatOfPoint;
import org.opencv.core.MatOfPoint2f;
import org.opencv.core.Rect;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;

public class MethodTests {
	
	/**
	 * Detects a rectangle in a {@link Mat} image and returns a {@link Rect} object which defines the detected rectangle.
	 * 
	 * 
	 * @param img The input image, usually of type {@code CV_8UC3}.
	 * 
	 * @return The {@link Rect} object which defines the detected rectangle.  Returns {@code null} if a rectangle is not found.
	 */
	public static Rect mpsRectDetect(Mat img) {
				
		// Convert image to grayscale
		Mat proc0 = Mat.zeros(img.size(), CvType.CV_8UC1);
		Imgproc.cvtColor(img, proc0, Imgproc.COLOR_BGR2GRAY);
		
		// Blur image
		Mat proc1 = Mat.zeros(proc0.size(), proc0.type());
		Imgproc.GaussianBlur(proc0, proc1, new Size(5.0, 5.0), 0.0);
		
		// Convert image to binary colors via a threshold (only either completely black or completely white colors)
		Mat proc2 = Mat.zeros(proc1.size(), proc1.type());
		Imgproc.threshold(proc1, proc2, 60.0, 255.0, Imgproc.THRESH_BINARY);
		
		// Find edges in image
		Mat edges = Mat.zeros(proc2.size(), CvType.CV_8UC1);
		Imgproc.Canny(proc2, edges, 100.0, 300.0); // DEV: threshold2 = 100*3;
		
		// Find contours in image
		List<MatOfPoint> contours = new ArrayList<>();
        Imgproc.findContours(edges, contours, new Mat(), Imgproc.RETR_LIST, Imgproc.CHAIN_APPROX_SIMPLE);
        
        // Set this variable's scope so that it
        // can be accessed by the return statement
        Rect rect = null;
        
        // Check the contours
        for (int i = 0; i < contours.size(); i++) {
        	
        	MatOfPoint tempContour = contours.get(i);
            MatOfPoint2f newMat = new MatOfPoint2f(tempContour.toArray());
            int contourSize = (int) tempContour.total();
            MatOfPoint2f approxCurve_temp = new MatOfPoint2f();
            Imgproc.approxPolyDP(newMat, approxCurve_temp, contourSize * 0.05, true);
            
            if (approxCurve_temp.total() > 5) {
            	
                rect = Imgproc.boundingRect(new MatOfPoint(approxCurve_temp.toArray()));
                
            }
        	
        }
        
        return rect;
        
	}

}
