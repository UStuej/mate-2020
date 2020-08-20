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
	
	public static Mat[] scSec(final Mat[][] faceImgs /* This 2D array is in the format of faceImages[faceID][colorMaskedID]. */) throws IllegalArgumentException {
		
		// CONSTANTS
		final int IS_SQUARE_THRESHOLD = 20;
		final double SQUARE_HORIZ_OFFSET = 1.0 / 4.0;
		final double RECT_HORIZ_OFFSET = 1.0 / 4.0;
		final double RECT_VERT_OFFSET = 1.0 / 4.0;
		
		short[] retIdx = null;
		short remainingTotal = 10; // = 0 + 1 + 2 + 3 + 4
		
		// Get one of the square images
		for (short i = 0; i < faceImgs.length; i++) {
			
			Mat img = faceImgs[i][0];
			
			if (Math.abs(img.rows() - img.cols()) <= IS_SQUARE_THRESHOLD) {
				
				retIdx = new short[] {i, -1, -1, -1, -1};
				remainingTotal -= i;
				break;
				
			}
			
		}
		
		// Make sure a square image was found
		if (retIdx == null) {
			
			throw new IllegalArgumentException("30f64858-d36e-11ea-87d0-0242ac130003");
			
		}
		
		short currentImgIdx = retIdx[0];
		
		for (short i = 0; i < 3; i++) {
			
			Mat[] imgs = faceImgs[currentImgIdx];
			Mat firstImg = imgs[0];
			boolean is1Square = Math.abs(firstImg.rows() - firstImg.cols()) <= IS_SQUARE_THRESHOLD;
			
			short rRectColor = -1;
			
			for (short i2 = 0; i2 < imgs.length; i2++) {
				
				Mat img = imgs[i2];
				
				Rect rect = mpsRectDetect(img);
				
				if (rect == null)
					continue;
				
				Point midpoint = new Point(rect.x + (rect.width / 2.0), rect.y + (rect.height / 2.0));
				
				// dFIXME On a test run of this code, this section was not able to detect the right-most rectangle on SubwayCar4.JPG (the exact path for the input images in question: "C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/*/SubwayCar4_m_95-116_171-255_0-255.jpg").
				// This is likely due to a faulty threshold.
				if (is1Square && (midpoint.x / firstImg.cols()) >= (1.0 - SQUARE_HORIZ_OFFSET)/* && Math.abs(midpoint.y - imgCenter.y) <= 20.0 *//* dFIXME Is this second half necessary? */) {
					
					rRectColor = i2;
					break;
					
				} else if ((midpoint.x / firstImg.cols()) >= (1.0 - RECT_HORIZ_OFFSET)/* && Math.abs(midpoint.y - imgCenter.y) <= 20.0 *//* dFIXME Is this second half necessary? */) {
					
					rRectColor = i2;
					break;
					
				}
				
			}
			
			if (rRectColor == -1) {
				
				throw new IllegalArgumentException("f030e588-1043-4c26-ab09-e20e139b20c4");
				
			}
			
			for (short i2 = 0; i2 < faceImgs.length; i2++) {
				
				Mat img = faceImgs[i2][rRectColor];
				Rect rect = mpsRectDetect(img);
				
				boolean is2Square = Math.abs(firstImg.rows() - firstImg.cols()) <= IS_SQUARE_THRESHOLD;
				
				if (rect == null)
					continue;
				
				Point midpoint = new Point(rect.x + (rect.width / 2.0), rect.y + (rect.height / 2.0));
				
				if (is2Square && (midpoint.x / img.cols()) <= SQUARE_HORIZ_OFFSET/* && Math.abs(midpoint.y - imgCenter.y) <= 20.0 *//* dFIXME Is this second half necessary? */) {
					
					retIdx[i + 1] = currentImgIdx = i2;
					remainingTotal -= i2;
					break;
					
				} else if ((midpoint.x / img.cols()) <= RECT_HORIZ_OFFSET/* && Math.abs(midpoint.y - imgCenter.y) <= 20.0 *//* dFIXME Is this second half necessary? */) {
					
					retIdx[i + 1] = currentImgIdx = i2;
					remainingTotal -= i2;
					break;
					
				}
				
			}
			
			if (retIdx[i + 1] == -1) {
				
				throw new IllegalArgumentException("26e66660-fd52-4e1c-9de7-07881f9b8c53");
				
			}
			
		}
		
		Mat[] second = faceImgs[1];
		Mat[] remaining = faceImgs[remainingTotal];
		Point remainingCenter = new Point(remaining[0].width() / 2.0, remaining[0].height() / 2.0);
		short rectColor = -1;
		
		for (short i = 0; i < second.length; i++) {
			
			Mat img = second[i];
			Rect rect = mpsRectDetect(img);
			
			if (rect == null)
				continue;
			
			Point midpoint = new Point(rect.x + (rect.width / 2.0), rect.y + (rect.height / 2.0));
			
			if (/*Math.abs(midpoint.x - secondCenter.x) <= 20.0 *//* dFIXME Is this first half necessary? *//* && */(midpoint.y / img.rows()) <= RECT_VERT_OFFSET) {
				
				rectColor = i;
				break;
				
			}
			
		}
		
		if (rectColor == -1) {
			
			throw new IllegalArgumentException("75ce49f8-f4a2-47ce-9449-08d3d53853d4");
			
		}
		
		Mat[] ret = new Mat[5];
		Rect rect = mpsRectDetect(remaining[rectColor]);
		Point midpoint = new Point(rect.x + (rect.width / 2.0), rect.y + (rect.height / 2.0));
		
		for (short i = 0; i < 4 /* retIdx.length - 1 */; i++) {
			
			ret[i] = Imgcodecs.imread(String.format("./resources/subwaycar/SubwayCar%d.JPG", retIdx[i] + 1));
			
		}
		
		if (/*Math.abs(midpoint.x - secondCenter.x) <= 20.0 *//* dFIXME Is this first half necessary? *//* && */(midpoint.y / remaining[0].rows()) <= RECT_VERT_OFFSET) {
			
			Mat img = Imgcodecs.imread(String.format("./resources/subwaycar/SubwayCar%d.JPG", remainingTotal + 1));
			Mat dst = Mat.zeros(img.size(), img.type());
			Imgproc.warpAffine(img, dst, Imgproc.getRotationMatrix2D(remainingCenter, 180.0, 1.0), img.size());
			ret[4] = dst;
			
		} else if (/*Math.abs(midpoint.x - secondCenter.x) <= 20.0 *//* dFIXME Is this first half necessary? *//* && */(midpoint.y / remaining[0].rows()) >= (1.0 - RECT_VERT_OFFSET)) {
			
			ret[4] = Imgcodecs.imread(String.format("./resources/subwaycar/SubwayCar%d.JPG", remainingTotal + 1));
			
		} else {
			
			throw new IllegalArgumentException("452e45b2-bc49-4d42-bb99-72148480d471");
			
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
				
//		// Convert image to grayscale
//		Mat proc0 = Mat.zeros(img.size(), CvType.CV_8UC1);
//		Imgproc.cvtColor(img, proc0, Imgproc.COLOR_BGR2GRAY);
		
		// Blur image
		Mat proc0 = Mat.zeros(img.size(), img.type());
		Imgproc.GaussianBlur(img, proc0, new Size(5.0, 5.0), 0.0);
		
		// Convert image to binary colors via a threshold (only either completely black or completely white colors)
		Mat proc1 = Mat.zeros(proc0.size(), proc0.type());
		Imgproc.threshold(proc0, proc1, 60.0, 255.0, Imgproc.THRESH_BINARY);
		
		// Find edges in image
		Mat edges = Mat.zeros(proc1.size(), CvType.CV_8UC1);
		Imgproc.Canny(proc1, edges, 100.0, 300.0); // DEV: threshold2 = 100*3;
		
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
	
	public static Mat netFromImgs(final Mat[] faceImgs /* Array of CV_8UC3 Mats in the format of the returned array from #scSec */) {
		
		/* TODO
		 
		 Pseudo-code (assuming top-left origin):
		 
		 1. Size images appropriately to Mat array sFaceImgs
		 	a. faceImgs[0:3] all have same height (y-axis)
		 	b. faceImgs[4] has same width (x-axis) as faceImgs[1]
		 2. Create blank CV_8UC3 Mat with width ((sum of sFaceImgs[0:3] width)) and width ((height of sFaceImgs[0:3] (prob. use sFaceImgs[0] since it doesn't matter anyway) + height of sFaceImgs[4]))
		 3. Set sFaceImgs[0] in position (0, blank.height - sFaceImgs[0].height)
		 4. Set sFaceImgs[1] in position (sFaceImgs[0].width, blank.height - sFaceImgs[0].height)
		 5. Set sFaceImgs[2] in position (sFaceImgs[0].width + sFaceImgs[1].width, blank.height - sFaceImgs[0].height)
		 6. Set sFaceImgs[3] in position (sFaceImgs[0].width + sFaceImgs[1].width + sFaceImgs[2].width, blank.height - sFaceImgs[0].height)
		 7. Set sFaceImgs[4] in position (sFaceImgs[0].width, 0)
		 8. Return (now filled) blank image
		 
		 */
		
		
		Mat[] sFaceImgs = new Mat[5];
		
		// Get the minimum height of the bottom row of images
		int bMinHeight = Math.min(Math.min(Math.min(faceImgs[0].height(), faceImgs[1].height()), faceImgs[2].height()), faceImgs[3].height());
		
		// Scale the images to the same height (defined above)
		for (short i = 0; i < 4; i++) {
			
			if (faceImgs[i].height() == bMinHeight) {
				
				sFaceImgs[i] = faceImgs[i];
				
			} else {
				
				Mat dst = Mat.zeros(bMinHeight, Math.round(faceImgs[i].width() * (bMinHeight / (float) faceImgs[i].height())), CvType.CV_8UC3);
				Imgproc.resize(faceImgs[i], dst, dst.size());
				sFaceImgs[i] = dst;
				
			}
			
		}
		
		// Scale the top-most image to the same width as the one below it
		int tWidth = sFaceImgs[1].width();
		
		if (faceImgs[4].width() == tWidth) {
			
			sFaceImgs[4] = faceImgs[4];
			
		} else {
			
			Mat dst = Mat.zeros(Math.round(faceImgs[4].height() * (tWidth / (float) faceImgs[4].width())), tWidth, CvType.CV_8UC3);
			Imgproc.resize(faceImgs[4], dst, dst.size());
			sFaceImgs[4] = dst;
			
		}
		
		
		// Initialize the net (output) image with the correct size and type
		Mat net = Mat.zeros(sFaceImgs[0].height() + sFaceImgs[4].height(), sFaceImgs[0].width() + sFaceImgs[1].width() + sFaceImgs[2].width() + sFaceImgs[3].width(), CvType.CV_8UC3);
		
		sFaceImgs[0].copyTo(net.submat(new Rect(0, net.height() - bMinHeight, sFaceImgs[0].width(), bMinHeight)));
		
		// Insert the bottom row of images into the net
		{
			
			int netHeight = net.height();
			int bMinY = netHeight - bMinHeight;
			int xDisSum = 0;
			
			for (short i = 0; i < 4; i++) {
				
				sFaceImgs[i].copyTo(net.submat(new Rect(xDisSum, bMinY, sFaceImgs[i].width(), bMinHeight)));
				xDisSum += sFaceImgs[i].width();
				
			}
			
		}
		
		// Insert the top-most image into the net
		sFaceImgs[4].copyTo(net.submat(new Rect(sFaceImgs[0].width(), 0, tWidth, sFaceImgs[4].height())));
		
		return net;
		
	}

}
