## B.C. Data Visualization-- BC Surgical Wait Times Dashboard 


### Section 1: Motivation and Purpose

1. **Project Background**

In July 2011, the B.C. Government became the first province in Canada to open its data to the public under an open licence. After making government data available online, the B.C. Government decided to make government data visualizable online to further satisfy the requirement of making the information hidden in data easy to understand from the feedbacks of the public. It made an open bidding for the project of developing B.C. Data Visualization APP.

2.	**Our Role**

We are Nightingale Visualization Tech Company. Our mission is to visualize the information underneath data and make it universally understandable and useful. We won the bid of the project to develop B.C. Data Visualization APP for the medical data. And our team of four is responsible for the BC Surgical Wait Times Dashboard.

3.	**Target audience**

The target audience of our dashboard is extensive, from every single one who resides in B.C. to the government authorities, from the researchers to the medical workers. 

4.	**Aim of the Dashboard**

Long waiting times is an important issue for health services in Canada, and the main concern is about waiting times for elective treatments [[1]("https://www.oecd-ilibrary.org/social-issues-migration-health/waiting-times-for-health-services_242e3c8c-en")]. Among the OECD countries, Canada’s waiting times problem ranks in the medium-high priority level, while Germany, Korea, Japan, Switzerland, and U.S rank in low priority level [[2]("https://www.oecd-ilibrary.org/sites/242e3c8c-en/1/3/1/index.html?itemId=/content/publication/242e3c8c-en&_csp_=e90031be7ce6b03025f09a0c506286b0&itemIGO=oecd&itemContentType=book#chapter-d1e287")]. After the COVID-19 outbreak, tens of thousands of scheduled surgeries being cancelled or postponed across Canada, which prolonged the surgical wait times. In B.C. province, between Mar. 16 and May 18, 2020, it was estimated that 30298 elective nonurgent surgeries were either postponed or not scheduled because of the COVID-19 pandemic [[3]("https://www2.gov.bc.ca/assets/gov/health/conducting-health-research/surgical-renewal-plan.pdf")]. If we could have a public dashboard of surgical data like that of COVID-19 for the province, it will help both the patients to know the situation and the doctors as well as the health authorities to look at where improvements are most needed [[4]("https://bc.ctvnews.ca/b-c-doctors-criticize-top-down-approach-and-government-secrecy-as-minister-defends-surgical-strategy-1.5767547")]. Our app will show how many waiting and completed cases in B.C. and allow users to check the trend of completed cases proportion and the waiting times for different procedures in by filtering different health authorities, hospitals, and procedures.


### Section 2:  Description of the Data

**Data Set: "BC Quarterly Surgical Wait Times"**

Source: [https://catalogue.data.gov.bc.ca/dataset/bc-surgical-wait-times/resource/f294562c-a6fd-4d7f-8f99-c51c91891c67](https://catalogue.data.gov.bc.ca/dataset/bc-surgical-wait-times/resource/f294562c-a6fd-4d7f-8f99-c51c91891c67)

This dataset provides information of elective surgical procedures' wait times in British Columbia. This dataset contains the information of patients of all ages and only the scheduled surgical cases not the unscheduled ones. The data is collected quartely at the end of each quarter from year 2009 to 2021. The dataset has the following variables:


1. **Quarter** : The quarter for which data is collected.
2. **Year** : The year for which data is collected.
3. **Waiting** : The number of surgical cases waiting at the end each quarter 
4. **Completed**: The number of surgical cases completed within each quarter.
5. **Health authority**: The health authority of the hospital from where data is collected.
6. **Hospital name**: The name of the hospital where the surgical procedures are performed.
7. **Procedure group**: The name of the surgical procedure type and data has 83 unique procedures.
8. **Completed 50th percentile**: For completed procedures, the number of weeks 50th percentile of the patients waited for surgery.
9. **Completed 90th percentile**: For completed procedures, the number of weeks 90th percentile of the patients waited for surgery.

**Dimesion of data**: The dataset has total 151277 observation for 9 variables, and after removing the missing values or low volume procedures (<=5) due to privacy concern, clean dataset consist of 122086 observations. 

The dataset provides BC surgical data on a quarterly basis. The waiting column can be categorized as representing the number of patients on a surgical **wait-list** at the end of each quarter.  The number of completed cases can be categorized as representing the work done or **efficiency** for each procedure at each hospital during that quarter.  The percentile information can be categorized as representing the **wait-time** in weeks for cases completed during that quarter. 

### Section 3: Research Questions and Usage Scenarios

**Research Questions**

Health literature repeatedly demonstrates that prolonged surgical wait-times are detrimental to patient health. [[5]("https://www.policyalternatives.ca/sites/default/files/uploads/publications/BC%20Office/2016/04/ccpa-bc_ReducingSurgicalWaitTimes_summary.pdf")], [[6]("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1959190/")]  It follows that having reduced wait-lists and increased efficiency is associated with reduced wait-times and improved health outcomes.[[7]("https://pubmed.ncbi.nlm.nih.gov/27603225/")]  To explore these concepts further there are some research questions that the dashboard visulatizations will be able to answer:

1. Are there any trends in wait-list and efficiency numbers throughout the year, across years or across health authorities?

2. Are all health authorities and hospitals equally efficient? 

3. What are the differences in wait-times between procedure groups? 

4. Are there any procedure group that are not being completed in a timely manner? There are international maximum wait-time guidelines set for many surgical procedures [[8]("https://www2.gov.bc.ca/gov/content/health/accessing-health-care/surgical-wait-times")]. 

5. Are there any variations within this surgical data that may be associated with the pandemic? Covid has resulted in public health restrictions for society and the healthcare system. [[9]]("https://bc.ctvnews.ca/scroll-through-this-timeline-of-the-1st-year-of-covid-19-in-b-c-1.5284929"). 


**Usage Scenario**

Anna is a Regional Service Co-ordinator at Interior Health Authority. She wants to check the efficiency (on the base of performed surgeries) of their health authority in compariosn to other five health authorities of BC. She wants to know if Interior Health or any other health authority is doing better/worse than others or needs to improve their services. She will look for that information on "BC Surgical Wait Times" dashboard and will find out the analysis of total completed surgeries and total waiting surgeries of all the health authorities and their respective efficiency (i.e., percentage of completed surgeries). She gets an idea of which health authority is doing good/bad in performing surgeries. If health authority 'X' is doing worse than others then she select authority 'X' to see further for this specific health authority as she wants to know the performance of each hospital under that specific authoiry and waiting time for different procedures of that authority in order to figure out which hospital or procedure group is dropping the efficiency of that authority. Additionaly, she will also get information regarding the impact of COVID-19 on the efficiency of all the health authorities.

