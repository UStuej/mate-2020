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
	
	public static void mpsRectDetect() {
		
		// Get source image
		Mat img = Imgcodecs.imread("C:/Users/bushy/Downloads/files/files/output/green/SubwayCar3_m_75-90_73-255_0-255.jpg");
		
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
        
        Point[] points = null;
        Rect rect = null; // TODO MAIN OUTPUT VAR
        
        // Check the contours
        for (int i = 0; i < contours.size(); i++) {
        	
        	MatOfPoint tempContour = contours.get(i);
            MatOfPoint2f newMat = new MatOfPoint2f(tempContour.toArray());
            int contourSize = (int) tempContour.total();
            MatOfPoint2f approxCurve_temp = new MatOfPoint2f();
            Imgproc.approxPolyDP(newMat, approxCurve_temp, contourSize * 0.05, true);
            
            if (approxCurve_temp.total() > 5) {
            	
                points = approxCurve_temp.toArray();
                
                rect = Imgproc.boundingRect(new MatOfPoint(points));
                
            }
        	
        }
        
        if (points == null || rect == null) {
        	
        	System.out.println("One or more of the variables is null.");
        	
        } else {
        	
        	System.out.print("[ ");
        	
        	for (Point p : points) {
        		
        		System.out.print(p.toString() + " , ");
        		
        	}
        	
        	System.out.println("]");
        	
        	
//        	System.out.printf("[ ( %d , %d ) , ( %d , %d ) , ( %d , %d ) , ( %d , %d ) ]\n");
        	System.out.println(rect.toString());
        	
        }
        
	}

}
