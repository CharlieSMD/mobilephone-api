Mobile Phone Catalogue Website Project Proposal
1. Introduction
This project aims to build a mobile phone catalogue and comparison website. Today’s phones have complex specs, making choices hard. This site will list popular Android and iOS phones in one place, helping users browse, compare, and discuss.
As someone who loves mobile devices and often changes phones, I’ve noticed how scattered phone info is. This project combines my interest with technical learning goals. 
2. Objectives
•	Build a rich phone database with Android/iOS models using TechSpecs API.
•	Allow search, filter, and sorting by various attributes.
•	Enable side-by-side phone comparisons.
•	Support user accounts, favourites, comments, and ratings.
•	Deliver a responsive, smooth user experience.
•	Deploy a stable, scalable website on AWS.
3. Requirements
3.1 Functional Requirements
•	Phone Info: Browse by category, view full specs (Android/iOS only).
•	Search/Filter: By brand, OS, year, chip, year, colour, etc.
•	Comparison: Select some phones, view differences.
•	Accounts: Register, log in/out, update profile, reset password.
•	Interaction: favourite phones, comment, reply, rate, and optionally upload images.
3.2 Non-Functional Requirements
•	Load Time :
The website should load main pages (home, catalogue, comparison) in under 2 seconds for a smooth user experience.
•	Logging & Maintenance :
The system should maintain backend logs for key events (e.g., login attempts, errors, failed API calls) to support debugging and long-term maintenance.
•	Security :
All user passwords must be securely hashed and stored. HTTPS will be enforced across the entire site.
4. Functionality
•	Browse phones with full details and images.
•	Advanced search and filtering.
•	Compare phones side-by-side.
•	Create and manage user accounts.
•	Save favourites and join discussions via comments and ratings.
5. Tech Stack
Backend: .NET (C#)
Database: MySQL or PostgreSQL
Frontend: React (preferred) or Angular, Material UI,
Deployment: AWS, EC2 for backend, S3 for frontend, RDS for database
6. Timeline 
·       Week 2: Define main features, design database schema, and choose tech stack.
·       Week 3: Create UI wireframes, plan frontend layout, and set up project structure.
·       Week 4: Set up backend with .NET and database (PostgreSQL); implement user auth (register/login).
·       Week 5: Build APIs for phone list and phone details; connect frontend to backend.
·       Week 6: Add search, filters, and sorting features on the frontend.
·       Week 7: Develop phone comparison feature (select 2–4 phones, show differences).
·       Week 8: Implement user features: favourites, comments, star ratings, and profile update.
·       Week 9: Optimize performance, fix bugs, improve UI/UX, and secure the app.
·       Week 10: Deploy to AWS (EC2, S3, RDS), do full testing, write documentation, and finalize project.
7. Deployment Plan
•	Backend deployed on AWS EC2
•	Frontend on S3, delivered via CloudFront
•	Database on RDS
8. Testing Plan
•	Unit Tests: For backend logic and frontend components
•	Integration Tests: Between frontend, backend, and database
•	Functional Tests: Verify user actions work as expected
•	Manual Tests: Check on different devices and browsers
•	Bug Fixing & Retesting: Ensure stability and polish
9. Conclusion
This project solves the problem of scattered phone information by offering a centralized, user-friendly, and interactive comparison site. It will not only help users but also deepen my full-stack and cloud development skills.

