package com.dorobotics.materov.y2020_test;

import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;

import com.dorobotics.materov.y2020_test.tests.MethodTests;

public class Main {
	
	// This is where I have my pre-masked and pre-cropped testing photos of the faces stored.
	// If someone else wants to run this, they will need to change the locations of
	// these files here; CTRL+F will probably work to change the first consistent parts.
	// This array is in the format a[face][colorMasked]
	final static String[][] imgPaths = {
			{
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/blue_v2/SubwayCar1_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/brown_v2-mod/SubwayCar1_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/green/SubwayCar1_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/orange/SubwayCar1_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/pink/SubwayCar1_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/purple/SubwayCar1_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/red/SubwayCar1_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/yellow_v2/SubwayCar1_m_21-33_103-255_0-255.jpg"
			}, {
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/blue_v2/SubwayCar2_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/brown_v2-mod/SubwayCar2_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/green/SubwayCar2_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/orange/SubwayCar2_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/pink/SubwayCar2_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/purple/SubwayCar2_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/red/SubwayCar2_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/yellow_v2/SubwayCar2_m_21-33_103-255_0-255.jpg"
			}, {
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/blue_v2/SubwayCar3_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/brown_v2-mod/SubwayCar3_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/green/SubwayCar3_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/orange/SubwayCar3_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/pink/SubwayCar3_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/purple/SubwayCar3_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/red/SubwayCar3_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/yellow_v2/SubwayCar3_m_21-33_103-255_0-255.jpg"
			}, {
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/blue_v2/SubwayCar4_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/brown_v2-mod/SubwayCar4_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/green/SubwayCar4_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/orange/SubwayCar4_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/pink/SubwayCar4_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/purple/SubwayCar4_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/red/SubwayCar4_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/yellow_v2/SubwayCar4_m_21-33_103-255_0-255.jpg"
			}, {
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/blue_v2/SubwayCar5_m_95-116_171-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/brown_v2-mod/SubwayCar5_m_5-20_40-135_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/green/SubwayCar5_m_75-90_73-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/orange/SubwayCar5_m_5-15_71-255_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/pink/SubwayCar5_m_150-183_48-110_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/purple/SubwayCar5_m_115-140_100-180_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/red/SubwayCar5_m_150-183_115-202_0-255.jpg",
				"C:/Users/Ben Alford/Desktop/Code/cv2testing/0_mask/output_bw-pe/yellow_v2/SubwayCar5_m_21-33_103-255_0-255.jpg"
			}
	};

	public static void main(String[] args) {
		
		System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
		
		// DEV assert imgPaths is rectangular
		// DEV assert (imgPaths.length >= 1)
		Mat[][] faceImgs = new Mat[imgPaths.length][imgPaths[0].length];
		
		// Load all images to memory
		for (short a = 0; a < imgPaths.length; a++) {
			for (short b = 0; b < imgPaths[a].length; b++) {
				
				Mat img = Imgcodecs.imread(imgPaths[a][b]);
				Mat ret = Mat.zeros(img.size(), CvType.CV_8UC1);
				Imgproc.cvtColor(img, ret, Imgproc.COLOR_BGR2GRAY);
				faceImgs[a][b] = ret;
				
			}
		}
		
		try {
			
			// DEV assert no element nor sub-element of any element may be null
			// DEV assert all images from any given element of faceImgs have identical sizes and types (type should be CV_8UC1)
			Mat[] imgs = MethodTests.scSec(faceImgs);
			
//			for (short i = 0; i < imgs.length; i++) {
//				
//				Imgcodecs.imwrite(String.format("./output/sc/sc%d.png", i), imgs[i]);
//				
//			}
			
			Mat net = MethodTests.netFromImgs(imgs);
			Imgcodecs.imwrite("./output/scnet.png", net);
			
		} catch (IllegalArgumentException e) {
			
			switch (e.getMessage()) {
				
				case "30f64858-d36e-11ea-87d0-0242ac130003":
					System.err.println("[ERROR]: No valid square was found! (code: 30f64858-d36e-11ea-87d0-0242ac130003)");
				break;
				
				case "f030e588-1043-4c26-ab09-e20e139b20c4":
					System.err.println("[ERROR]: One of the masked images does not contain a right colored rectangle! (code: f030e588-1043-4c26-ab09-e20e139b20c4)");
				break;
				
				case "26e66660-fd52-4e1c-9de7-07881f9b8c53":
					System.err.println("[ERROR]: One of the masked images does not contain a left colored rectangle! (code: 26e66660-fd52-4e1c-9de7-07881f9b8c53)");
				break;
				
				case "75ce49f8-f4a2-47ce-9449-08d3d53853d4":
					System.err.println("[ERROR]: One of the masked images does not contain a top colored rectangle! (code: 75ce49f8-f4a2-47ce-9449-08d3d53853d4)");
				break;
				
				case "452e45b2-bc49-4d42-bb99-72148480d471":
					System.err.println("[ERROR]: The top face's masked image does not contain either longways rectangles! (code: 452e45b2-bc49-4d42-bb99-72148480d471)");
				break;
				
//				default:
//					e.printStackTrace();
//				break;
				
			}
			
			e.printStackTrace();
			
		}
		
		System.out.println("Everything finished successfully.");
		
	}

}
