package com.dorobotics.materov.y2020_test;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.imgcodecs.Imgcodecs;

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
				
				faceImgs[a][b] = Imgcodecs.imread(imgPaths[a][b]);
				
			}
		}
		
		// DEV assert no element or sub-element of the aforementioned element may be null
		MethodTests.scSec(faceImgs);
		
		System.out.println("Everything finished successfully.");
		
	}

}
