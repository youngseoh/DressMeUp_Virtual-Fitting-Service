# 👗Dress Me Up

![image](https://github.com/DressMeUp-2023/DressMeUp-CV/assets/100707876/8d2b0ebe-1930-47e1-86c8-38bd9d4a390a)


Virtual Fitting Service - In situations where trying on clothes in person is difficult, this service allows users to virtually fit clothes onto their bodies
Users can take a photo of their own body and the clothes they wish to try on, and then virtually fit the desired clothes onto their body

## Contributors

FE : 숙명여자대학교 IT공학전공20 신경원

BE : 숙명여자대학교 IT공학전공20 한채연

DL : 숙명여자대학교 IT공학전공20 황영서

![image](https://github.com/DressMeUp-2023/DressMeUp-CV/assets/100707876/39391e37-10b9-4437-9106-79db0dc97220)

## Key Functionalities

1. Select & Add Model

![DMP1](https://github.com/DressMeUp-2023/DressMeUp-CV/assets/100707876/827fdbba-30ff-43ff-860c-6db1fa12bda0)

- Human Segmenation : Using the DeepLabV3-ResNet101 model, pre-trained on the COCO dataset, to identify and extract humans, removing the background.

2. Select & Add Cloth

![DMP2](https://github.com/DressMeUp-2023/DressMeUp-CV/assets/100707876/b3a41e30-5872-4561-b939-df45eb04f97c)

- Cloth Segmentation & classification : Using the iMaterialist (Fashion) 2019 dataset from FGVC6 and the U2Net model to perform segmentation of tops, bottoms, and dresses. The clothing parts are extracted, and the background is removed.
- Cloth Classification (specific categories)  : Using approximately 3000 images crawled from Google, we fine-tuned the ResNet18 model to classify clothing into categories such as long/short pants, long/short skirts, and long/short dresses.

3. Fitting 

![DMP3](https://github.com/DressMeUp-2023/DressMeUp-CV/assets/100707876/90f09878-db01-4f30-b378-21a51954e378)

- **Pose Estimation:** Using OpenPose to estimate the joint positions of a person and extract joint coordinates, in order to dress up different body parts according to the specifically classified clothing types.
- **Cloth Warp:** Applying perspective transform warping to fit the clothing to specific joint coordinates of the person, based on the type of clothing.

4. Save Image

![DMP4](https://github.com/DressMeUp-2023/DressMeUp-CV/assets/100707876/c49f2d71-9b7d-4de9-9277-31c52edc1932)

## Set UP

- Download the `cloth_segm.pth` file from Google Drive and place it in the following directory: `cloth-segmentation/model/cloth_segm.pth`
- Download the `long_short_segmentation.pth` file from Google Drive and place it in the following directory: `cloth-segmentation/long_short_segmentation.pth`

[pth Link](https://drive.google.com/drive/folders/1SphcENsSqJtFs9iVxzoSheV9OMYZC821)



