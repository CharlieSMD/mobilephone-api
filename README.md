# Mobile Phone Catalogue Website

## Project Overview
A mobile phone catalogue and comparison website that helps users browse, compare, and discuss Android and iOS phones.

## Tech Stack
- **Backend**: .NET (C#)
- **Database**: PostgreSQL
- **Frontend**: React + Material UI
- **Deployment**: AWS (EC2, S3, RDS)

## Main Features
- Phone information browsing (Android/iOS)
- Search and filter functionality
- Phone comparison feature
- User account system
- Favorites, comments, and rating functionality

## Week 2 Tasks
- [ ] Define main features
- [ ] Design database schema
- [ ] Choose tech stack
- [ ] Create project structure 

-----------------------------
Week 2

Environment Installation: 
•	Installed Homebrew - package manager
•	Installed .NET 8 SDK - backend
•	Installed Node.js v24.4.1 - react
•	Installed npm v11.4.2 - Material UI


1. backend/MobilePhoneAPI/Program.cs
Backend API code using .NET 8 and C#
Created 3 API endpoints for phones data and health check
2. database/schema.sql
Database design using PostgreSQL
Created 6 tables for users, phones, specs, favorites, comments, and ratings
3. frontend/mobilephone-frontend/src/App.tsx
Frontend interface code using React 18, TypeScript, and Material UI v7
Built mobile phone catalogue with search and product cards
4. README.md
Wrote project overview, tech stack, and Week 2 tasks
-------------------------------
Week 3
User Authentication System:
• Implemented user registration and login functionality
• Added JWT token authentication with 7-day expiration
• Created secure password encryption using BCrypt
• Configured CORS for frontend-backend communication
Backend Development:
backend/MobilePhoneAPI/
Added dependencies, created user models, implemented authentication service, and configured API endpoints
Frontend Development:
frontend/mobilephone-frontend/
Added HTTP client, built login/registration forms, implemented authentication state management, and created user dashboard
Database Integration:
backend/MobilePhoneAPI/Migrations/
Generated database migrations for user table creation

----------------------------


Week 4 
1. Find data from Kaggle Datasets – Mobile Phones
2. Backend:
•	Created Phone data model with fields: brand, model, storage, RAM, screen, camera, battery, price
•	Implemented PhoneService with data reading, search, and brand filtering capabilities
•	Developed PhoneController with 5 API endpoints:
•	Get all phones
•	Get specific phone
•	Search phones
•	Filter by brand
•	Get all brands

3. Frontend:
•	Updated Home component to use real API data
•	Implemented real-time search functionality supporting brand, model, and storage search
•	Optimized interface, such as removing images and displaying brand names in headers


----------
Week 5 Summary
Main Goal
Extend mobile phone data with detailed specifications and implement "View Details" functionality.
Backend
Extended Phone Model: Added 12 new fields (weight, dimensions, processor, OS, release year, etc.)
Database Migration: Updated PostgreSQL schema with new fields
Data Import: Switched from JSON to direct CSV import to database
PhoneService Update: Changed from reading JSON file to database queries
Frontend
View Details Component: Created modal dialog for detailed specifications
Interface Optimization: Removed price display, added product image placeholder
Real-time Integration: Connected to updated backend API
