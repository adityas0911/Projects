# Project 3

This repository contains [project 3](https://rutgers.instructure.com/courses/281725/assignments/3179407) for the course [01:198:440:C1 INTRO ARTIFIC INTELL](https://rutgers.instructure.com/courses/281725) Summer 2024.

## Course Information

- **Course:** [01:198:440:C1 INTRO ARTIFIC INTELL](https://rutgers.instructure.com/courses/281725)
- **Professor:** [Charles Wes Cowan](mailto:w.cowan@rutgers.edu)

## Due Date

- **July 22, 2024 @ 11:59 PM EDT**

## Contributor(s)

- **Aditya Sharma**

  - **RUID:** 219008361
  - **NetID:** as4108
  - **Email:** [as4108@scarletmail.rutgers.edu](mailto:as4108@scarletmail.rutgers.edu)

- **Alexander Laudino**

  - **RUID:** 024004315
  - **NetID:** asl172
  - **Email:** [asl172@scarletmail.rutgers.edu](mailto:asl172@scarletmail.rutgers.edu)

## Project Structure

The project directory is structured as follows:

```bash
IAL-PROJECT-3
├── .gitattributes
├── data.csv
├── IAL_Project_3_Writeup.pdf
├── main.py
├── Project_3_Summer_2024.pdf
└── README.md
```

- [`IAL-PROJECT-3`](https://github.com/adityas0911/IAL-Project-3): The project directory.
- [`.gitattributes`](./.gitattributes): Git configuration file for defining attributes per path.
- [`data.csv`](./data.csv): The CSV file containing the data used for training and testing the model.
- [`IAL_Project_3_Writeup.pdf`](./IAL_Project_3_Writeup.pdf): The project writeup.
- [`main.py`](./main.py): The main Python script containing the implementation of the neural network model.
- [`Project_3_Summer_2024.pdf`](./Project_3_Summer_2024.pdf): The project description and requirements document.
- [`README.md`](./README.md): This file, providing an overview of the project and its structure.

## Running the Project

1. **Download the Project Files**

   - Download the zip folder from [GitHub](https://github.com/adityas0911/IAL-Project-3).

2. **Unzip the Files**

   - Extract the contents of the zip folder.

3. **Install Dependencies**

   - Install any necessary dependencies/libraries as required by the project.

4. **Configure Settings**

   - In [`./main.py`](./main.py), set the following variables:

     - **filename (line 172):** Specify the name of the CSV file. For example, [`'data.csv'`](./data.csv).
     - **conv_1_out_channel_size (line 174):** Specify the number of output channels in the first convolutional layer. For example, `18`.
     - **conv_2_out_channel_size (line 175):** Specify the number of output channels in the second convolutional layer. For example, `100`.
     - **dense_1_out_feature_size (line 176):** Specify the number of output features in the first dense layer. For example, `20`.
     - **kernal (line 178):** Specify the kernel size of the convolutional layers. For example, `3`.
     - **stride_size (line 179):** Specify the stride size of the convolutional layers. For example, `1`.
     - **padding_size (line 180):** Specify the padding size of the convolutional layers. For example, `1`.
     - **train_data_percentage (line 181):** Specify the percentage of data to use for training. For example, `0.8`.
     - **val_data_out_of_test_data_percentage (line 182):** Specify the percentage of test data to use for validation. For example, `0.8`.
     - **sgd_learning_rate (line 183):** Specify the learning rate for the SGD optimizer. For example, `0.01`.
     - **adam_learning_rate (line 184):** Specify the learning rate for the Adam optimizer. For example, `0.01`.
     - **rmsprop_learning_rate (line 185):** Specify the learning rate for the RMSProp optimizer. For example, `0.01`.
     - **batch_size (line 186):** Specify the batch size. For example, `128`.
     - **epochs (line 187):** Specify the number of epochs. For example, `10`.

5. **Run the Project**

   - Open a terminal and run the [`main`](./main.py) script:

     - `py ./main.py`

## Contact Information

- For any questions or issues related to the project, please contact the [contributor(s)](https://gitkraken.dev/link/dnNjb2RlOi8vZWFtb2Rpby5naXRsZW5zL2xpbmsvci83OGJhZDBiMjliYmVmMWM4YzIzNTIyMWFmMTgwMzY1MGQzNDQ3NzA1L2YvUkVBRE1FLm1kP3VybD1odHRwcyUzQSUyRiUyRmdpdGh1Yi5jb20lMkZhZGl0eWFzMDkxMSUyRklBTC1Qcm9qZWN0LTMuZ2l0JmxpbmVzPTE0?origin=gitlens) via their provided email(s).
