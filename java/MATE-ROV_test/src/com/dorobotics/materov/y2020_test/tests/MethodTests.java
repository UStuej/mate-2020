package com.dorobotics.materov.y2020_test.tests;

import java.util.ArrayList;
import java.util.List;

import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.MatOfPoint;
import org.opencv.core.MatOfPoint2f;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Size;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;

public class MethodTests {
	
	public static short[] scSec(final Mat[][] faceImgs /* This 2D array is in the format of faceImages[faceID][colorMaskedID]. */) throws IllegalArgumentException {
		
		short[] ret = null;
		
		// Get one of the square images
		for (short i = 0; i < faceImgs.length; i++) {
			
			Mat img = faceImgs[i][0];
			
			if (Math.abs(img.rows() - img.cols()) < 10 /* Previous literal is a variable threshold */) {
				
				ret = new short[5];
				ret[0] = i;
				break;
				
			}
			
		}
		
		// Make sure a square image was found
		if (ret == null) {
			
			throw new IllegalArgumentException("30f64858-d36e-11ea-87d0-0242ac130003");
			
		}
		
		short currentImgIdx = ret[0];
		
		for (short i = 0; i < 3; i++) {
			
			Mat[] imgs = faceImgs[currentImgIdx];
			
			for (short i2 = 0; i2 < imgs.length; i2++) {
				
				Mat img = imgs[i2];
				
				Rect rect = mpsRectDetect(img);
				Point midpoint = new Point(rect.x + (rect.width / 2.0), rect.y - (rect.height / 2.0));
				
			}
			
		}
		
		return ret;
		
	}
	
	/**
	 * Detects a rectangle in a {@link Mat} image and returns a {@link Rect} object which defines the detected rectangle.
	 * 
	 * 
	 * @param img The input image, usually of type {@code CV_8UC1}.
	 * 
	 * @return The {@link Rect} object which defines the detected rectangle.  Returns {@code null} if a rectangle is not found.
	 */
	public static Rect mpsRectDetect(final Mat img) {
				
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
