#import "@preview/gentle-clues:1.2.0": info


#set page(numbering: "1 of 1")
#set par(justify: true)

#text(size: 14pt)[Bio-Medical Visualization and Visual Analytics]\
#text(size: 24pt)[Project Assignment 1]\
#text[Group 3: Lukas Blazsovsky, Vincent Rauchegger, Simon Wolffhardt]

#v(0.5cm)

#outline()

#pagebreak()

= Dataset Description

The dataset describes diabetes patient admissions/encounters in several US hospitals over a period of 10 years. It consists of over 100,000 rows and 50 variables. Each record is made up of patient information like gender, age group and weight group but also variables describing the encounter like the length of stay, the admission source and the readmittance duration.

The dataset can be accessed via
https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008.

== Raw Dataset Variables

The initial dataset consists of the following columns (variables):

#info[
  Some variables are not listed here, because their function is unknown or they are not relevant to our analysis.
]

#table(
  columns: (auto, 1fr, 1fr),
  table.header[
    *Variable*
  ][
    *Description*
  ][
    *Possible Values*
  ],
  [`encounter_id`], [Every encounter with a patient has a unique identifying number.], [Integers.],
  [`patient_nbr`], [Every patient has a unique identifying number.], [Integers.],
  [`race`], [The race of the patient.], par(justify: false)[`'Caucasian', 'AfricanAmerican', '?', 'Other', 'Asian', 'Hispanic'`],
  [`gender`], [The gender of the patient.], par(justify: false)[`'Female', 'Male', 'Unknown/Invalid'`],
  [`age`], [The age group of the patient.], par(justify: false)[`'[0-10)', '[10-20)',  '[20-30)', '[30-40)', '[40-50)', '[50-60)', '[60-70)', '[70-80)', '[80-90)', '[90-100)'`],
  [`weight`], [The weight group of the patient.], par(justify: false)[`'?', '[0-25)', '[25-50)', '[50-75)', '[75-100)', '[100-125)', '[125-150)', '[150-175)', '[175-200)', '>200'`],
  [`admission_type_id`], [An ID mapping to the type of admission.], par(justify: false)[
    `Emergency` (1),
    `Urgent` (2),
    `Elective` (3),
    `Newborn` (4),
    `Not Available` (5),
    `NULL` (6),
    `Trauma Center` (7),
    `Not Mapped` (8),
  ],
  [`discharge_disposition_id`], [An ID mapping to the discharge disposition.], par(justify: false)[
    Integer from 1-29. Examples are `Discharged to home` (1), `Expired` (11), `Hospice / home` (13), `NULL` (18)
  ],
  [`admission_source_id`], [An ID mapping to the source of admission.], par(justify: false)[
    Integer from 1-26. Examples are `Physician Referral` (1), `Clinic Referral` (2), `Transfer from a hospital` (4), `NULL` (17)
  ],
  [`time_in_hostpital`], [Number of days the patient stayed at the hospital.], par(justify: false)[
    Integers (number of days).
  ],
  [`medical_specialty`], [What type of medical specialty was dealing with the patient.], par(justify: false)[
    `'Pediatrics-Endocrinology', '?', 'InternalMedicine', 'Family/GeneralPractice', 'Cardiology', 'Surgery-General', 'Orthopedics', ...`
  ],
  [
    `num_lab_procedures`, \
    `num_procedures`, \
    `num_medications`, \
    `number_outpatient`, \
    `number_emergency`, \
    `number_inpatient`, \
    `number_diagnoses` \
  ], [Several metrics counting certain actions performed by the hospital staff or prior patient history.], par(justify: false)[
    Integers.
  ],
  [
    `diag_1`, \
    `diag_2`, \
    `diag_3` \
  ], [Diagnosis as ICD-9 code. (See https://en.wikipedia.org/wiki/List_of_ICD-9_codes)], par(justify: false)[
    ICD-9 code.
  ],
  [
    `max_glu_serum`, \
    `A1Cresult`
  ], [Result of laboratory tests, if performed], par(justify: false)[
    e.g.: '`Normal`', '`>200`', '`>300`', '`None`'
  ],
  [
    `metformin`, \
    `repaglinide`, \
    `nateglinide`, \
    `chlorpropamide`, \
    `...`, \
    `insulin`, \

  ], [Several medication statuses.], par(justify: false)[
    `'No', 'Steady', 'Down', 'Up'`
  ],
  [`change`], [If the medication changed in any way.], par(justify: false)[
    `'Ch', 'No'`
  ],
  [`diabetesMed`], [If the patient takes diabetes medication.], par(justify: false)[
    `'Yes', 'No'`
  ],
  [`readmitted`], [If and after how many days a patient has been readmitted.], par(justify: false)[
    `'NO', '<30', '>30'`
  ],
  
)

#pagebreak()

== Data Quality Issues

+ *Missing values:* Many records have missing values in certain fields, often, but not always, indicated by a question mark (?).
+ *Inconsistent naming of boolean categories:* Some variables have values that are binary but have named values, like 'Yes' or 'No'. The column 'change' has 'Ch' instead of 'Yes'.
+ *Categorical values that are represented by an ID*: Some values are represented by an ID and need to be corresponded to their string representation via an additional provided CSV-file.
+ *Categorical values with overlap*: Columns like '`admission_source_id`' have multiple values associated with incomplete or missing data like '`NULL`', '`Not Mapped`', '`Not Available`' and '`Unknown/Invalid`'.
+ *Limited number of detailed Diagnosis*: The dataset only includes up to three diagnosis per record even though there can be many more per encounter.
+ *Numerical values that have ben categorized into value ranges*: Values like age or weight were anonymized by replacing them with the respective range, making these columns harder to process.

= Initial Analysis Questions

These are the initial research questions we formulated:

+ What are the highest risk factors for patient readmission?
+ What are the key differences between early and late readmission?
+ How does a change in medication strategy change the readmission risk?


#pagebreak()

= Exploratory Analysis

First we want to get an overview of the different patient attributes in the dataset.


#figure(
  caption: "Distribution of patient attributes",
  grid(columns: 2)[
    #image("img/image.png", width: 100%)
  ][
    #image("img/image-1.png", width: 100%)
  ][
    #image("img/image-age.png", width: 100%)
  ][
    #image("img/image-weight.png")
  ]
)

Let us analyze each attribute:
- *Gender*: The majority of patients are classified as female in the dataset.
- *Race*: Most patients are classified as Caucasian, followed by African American. This makes sense given the origin of the data. A significant portion of the dataset has missing values for this attribute.
- *Age*: The age distribution shows that most patients are between 50 and 80 years old.
- *Weight*: The weight attribute has a large number of missing values, making it difficult to draw conclusions. Among the available data, most patients fall into the weight categories between 75 and 125.

= Summary
