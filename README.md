# drillOffsetCalculation
## Summary:

With an input xray image of a hole-to-pad, output offset values with any identified contours. 

Uses python OpenCV and numpy libraries.



## Preview of Results:

Figure 1: Result 1 (less input noise)

![image](https://user-images.githubusercontent.com/124814751/223542304-b843523e-adfa-490d-a69b-05a458b703b5.png)



Figure 2: Result 2 (greater input noise)

![original_lowQual](https://user-images.githubusercontent.com/124814751/236031523-f117518a-ee61-4452-a46a-e25bcbfe1338.png)




## Choice Validation:

Figure 3: Using "Closing" instead of "Opening" 

![closing](https://user-images.githubusercontent.com/124814751/225425604-36974cf5-afe5-4d70-bf1e-b420e4979fe1.png)

Figure 4: Threshold Mask after a Closing Operation

![closing threshold mask](https://user-images.githubusercontent.com/124814751/225425635-258b563c-06ce-4b8a-880b-dacb2a02839a.png)



Figure 5: Using "Histogram Equalization" to improve contrast

![histogram equalization Opening](https://user-images.githubusercontent.com/124814751/225425768-b98d0755-f011-43a5-87cb-cdb5b4e9433e.png)

Figure 6: Histogram Equalization Threshold Mask

![histEqual and Opening threshold mask](https://user-images.githubusercontent.com/124814751/225425798-341363f1-ff78-4cb0-be60-cd0dfa6cf637.png)




Figure 7: Using both "Closing" and "Histogram Equalization"

![closing and hist equal](https://user-images.githubusercontent.com/124814751/225425836-ed85e70e-533b-43ac-8c2d-93560308e55b.png)

Figure 8: Closing + Histogram Equalization Threshold Mask

![closing and hist equal threshold mask](https://user-images.githubusercontent.com/124814751/225425976-41096d5d-6672-4814-a404-6d2f34cc1933.png)



## Filtering Contours

Figure 9: Unfiltered Contour Detection - Filtering Random Backgroud Noise

![image](https://user-images.githubusercontent.com/124814751/225454121-6f32ba21-80d8-4136-8957-0fa3ca4a6d8e.png)

Figure 10: Two-Tiers of enclosed circles

![image](https://user-images.githubusercontent.com/124814751/225454050-2aefbc73-00f0-4859-8ff1-740ecf812dfe.png)
