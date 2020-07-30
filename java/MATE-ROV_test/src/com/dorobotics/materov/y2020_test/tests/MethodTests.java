package com.dorobotics.materov.y2020_test.tests;

import java.util.ArrayList;
import java.util.List;

import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.MatOfPoint;
import org.opencv.core.MatOfPoint2f;
import org.opencv.core.Rect;
import org.opencv.core.Size;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;

public class MethodTests {
	
	public static void scSec() {
		
		// This is where I have my pre-masked and pre-cropped testing photos of the faces stored.
		// If someone else wants to run this, they will need to change the locations of
		// these files here; CTRL+F will probably work to change the first consistent parts.
		final String[] imgPaths = {
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/blue_v2/SubwayCar1_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/blue_v2/SubwayCar2_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/blue_v2/SubwayCar3_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/blue_v2/SubwayCar4_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/blue_v2/SubwayCar5_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/brown_v2-mod/SubwayCar1_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/brown_v2-mod/SubwayCar2_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/brown_v2-mod/SubwayCar3_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/brown_v2-mod/SubwayCar4_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/brown_v2-mod/SubwayCar5_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/green/SubwayCar1_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/green/SubwayCar2_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/green/SubwayCar3_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/green/SubwayCar4_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/green/SubwayCar5_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/orange/SubwayCar1_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/orange/SubwayCar2_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_edited/orange/SubwayCar3_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/orange/SubwayCar4_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_edited/orange/SubwayCar5_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/pink/SubwayCar1_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/pink/SubwayCar2_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/pink/SubwayCar3_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/pink/SubwayCar4_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/pink/SubwayCar5_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/purple/SubwayCar1_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/purple/SubwayCar2_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/purple/SubwayCar3_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/purple/SubwayCar4_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/purple/SubwayCar5_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/red/SubwayCar1_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/red/SubwayCar2_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/red/SubwayCar3_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/red/SubwayCar4_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/red/SubwayCar5_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/yellow_v2/SubwayCar1_m_21-33_103-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/yellow_v2/SubwayCar2_m_21-33_103-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/yellow_v2/SubwayCar3_m_21-33_103-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/yellow_v2/SubwayCar4_m_21-33_103-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output/yellow_v2/SubwayCar5_m_21-33_103-255_0-255.jpg"
		};
		
		
		for (String imgPath : imgPaths) {
			
			Mat img = Imgcodecs.imread(imgPath);
			
			Rect rect = mpsRectDetect(img);
			
			if (rect == null) {
				
				// TODO Code to run if the 
				continue;
				
			}
			
		}
		
	}
	
	/**
	 * Detects a rectangle in a {@link Mat} image and returns a {@link Rect} object which defines the detected rectangle.
	 * 
	 * 
	 * @param img The input image, usually of type {@code CV_8UC3}.
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
