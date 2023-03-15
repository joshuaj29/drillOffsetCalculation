# drillOffsetCalculation
Summary:
With an input xray image of a hole-to-pad, output offset values with any identified contours. 
Uses python OpenCV and numpy libraries.


Preview of Results:

Result 1 (less input noise)
![image](https://user-images.githubusercontent.com/124814751/223542304-b843523e-adfa-490d-a69b-05a458b703b5.png)


Result 2 (greater input noise)
![image](https://user-images.githubusercontent.com/124814751/223542581-0c760126-fb80-4405-aef7-3f6dd38c6fcb.png)

.

Choice Validation:
Using "Closing" instead of "Opening"
![closing](https://user-images.githubusercontent.com/124814751/225425604-36974cf5-afe5-4d70-bf1e-b420e4979fe1.png)
Closing Threshold Mask
![closing threshold mask](https://user-images.githubusercontent.com/124814751/225425635-258b563c-06ce-4b8a-880b-dacb2a02839a.png)

.

Using "Histogram Equalization" to improve contrast
![histogram equalization Opening](https://user-images.githubusercontent.com/124814751/225425768-b98d0755-f011-43a5-87cb-cdb5b4e9433e.png)
Histogram Equalization Threshold Mask
![histEqual and Opening threshold mask](https://user-images.githubusercontent.com/124814751/225425798-341363f1-ff78-4cb0-be60-cd0dfa6cf637.png)

.

Using both "Closing" and "Histogram Equalization"
![closing and hist equal](https://user-images.githubusercontent.com/124814751/225425836-ed85e70e-533b-43ac-8c2d-93560308e55b.png)
Closing + Histogram Equalization Threshold Mask
![closing and hist equal threshold mask](https://user-images.githubusercontent.com/124814751/225425976-41096d5d-6672-4814-a404-6d2f34cc1933.png)
