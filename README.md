# Sekula.id - Growth Learning Skill App
# Product Capstone

## C23-PC668
## Active Team Member	:
1.	(ML)  M160DSX3083 – Rifki Aprian – Universitas Darma Persada
2.	(ML)  M322DSY0204 – Anisya Niken Ayu Ningtyas – Universitas Presiden
3.	(CC)  C151DSX4877   – Rizky Fajar Sulistyo – Universitas Brawijaya
4.	(CC)  C040DSX1643 – Lanang Almasyuri – Institut Teknologi Sumatera


## Abstract:

According to Kompas.com, The Minister of Labour, Ida Fauziyah, said that 12 percent of unemployment in Indonesia is dominated by bachelor and diploma graduates. It mentioned the causative factor of this problem since there are no links and matches after graduating from college. Even though with a Diploma or Bachelor education, students should be able to meet desired career qualifications by the work environment. Then what are the main factors for students experiencing miss link and match after graduation? Do they experience developmental issues during their college education? In this problem statement, our team would like to highlight one of the causes of this problem, which is that students tend to not have career planning while in college. Even though career planning can lead us to prepare ourselves thoroughly during college with the soft skills and hard skills needed by the intended career to have sufficient self-qualifications. We designed the sekula.id project to address college students to prepare for career paths. Sekula.id will provide information about the qualifications for certain careers and recommend course paths, either soft skill or hard skill, and their links, volunteer, and internship. Students can also explore many activities as volunteer and internship information to support their career. Sekula.id will bring students on the right path to achieve their careers.

* Machine Learning :
We utilized three course datasets from Kaggle and merged them. Employing the concept of content-based filtering, we transformed the datasets into vector form using TF-IDF. Additionally, we converted the user input into a vector using the same method. By calculating the cosine similarity between the dataset vectors and the user input vector, we determined the courses with the highest similarity as recommendations.

* Cloud Computing :
We used a serverless recommended solution for greater scalability, focus on development, and faster deployment time. We deployed Flask to Cloud Run and used Cloud SQL to implement the MySQL database. We also developed routing, request, response and other features to do various web app management using Flask with this cloud run. We also set up cloud storage buckets to store machine learning files and data. We set up the CI/CD pipeline using github, cloud build, and google container registry so that it can be easily accessed and used by the Cloud Run service. And finally Deploy Flask containers to Cloud Run, so that web applications can be run automatically and scalably in a serverless environment.

This application can be accessed through the link below:
https://flask-app-45cyhhvmdq-et.a.run.app
